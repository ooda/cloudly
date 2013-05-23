import os
from os.path import join
from datetime import date
import gzip
import json

from twitter import TwitterStream, OAuth
from cloudly import rqworker, logger, cache
from cloudly.decorators import throttle
from cloudly.dictutils import merge, find_item


log = logger.init(__name__)


class Tweets(object):
    """Encapsulate a TwitterStream.
    If credentials are not provided, they are taken from the environment:

        TWITTER_CONSUMER_KEY
        TWITTER_CONSUMER_SECRET
        TWITTER_ACCESS_TOKEN
        TWITTER_ACCESS_TOKEN_SECRET

    """
    def __init__(self, consumer_key=None, consumer_secret=None,
                 access_token=None, access_token_secret=None):
        """Init with or without credentials. If not provided, they'll be taken
        from the environment.
        """
        if not (consumer_key and consumer_secret and
                access_token and access_token_secret):
            consumer_key = os.environ['TWITTER_CONSUMER_KEY']
            consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
            access_token = os.environ['TWITTER_ACCESS_TOKEN']
            access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

        self.oauth = OAuth(access_token, access_token_secret,
                           consumer_key, consumer_secret)
        self.stream = TwitterStream(auth=self.oauth)

        self.default_coordinates = [-180, -90, 180, 90]

    def having(self, wordlist=None, coordinates=None):
        """Track tweets potientially filtering them.

        WARNING: wordlist and coordinates are ORed by Twitter. Can't AND both.

        If `wordlist` is given a list of phrases will by tracked.

        From Twitter's documentation:

        > A phrase may be one or more terms separated by spaces, and a phrase
        > will match if all of the terms in the phrase are present in the
        > Tweet, regardless of order and ignoring case. By this model, you can
        > think of commas as logical ORs, while spaces are equivalent to
        > logical ANDs (e.g. 'the twitter' is the AND twitter, and
        > 'the,twitter' is the OR twitter).

        Thus, using the example above, the parameter wordlist would be,
        respectively:

            wordlist = ['the twitter']
            wordlist = ['the', 'twitter']

        Cf. https://dev.twitter.com/docs/streaming-apis/parameters#track

        If `coordinates` is given, it must be a list of of the form:

            [lng1, lat1, lng2, lat2]

        This is a generator function.
        """
        track = ",".join(wordlist) if wordlist else None
        locations = ",".join(map(str, coordinates)) if coordinates else None

        if track and locations:
            generator = self.stream.statuses.filter(track=track,
                                                    locations=locations)
        elif track:
            generator = self.stream.statuses.filter(track=track)
        elif locations:
            generator = self.stream.statuses.filter(locations=locations)
        else:
            raise ValueError("Must provide one of wordlist or coordinates")

        for tweet in generator:
            if locations:
                if 'coordinates' in tweet and tweet['coordinates']:
                    yield tweet
            else:
                yield tweet

    def with_coordinates(self):
        """Utility method yielding all geolocated tweets.
        This is a generator function.
        """
        for tweet in self.having(coordinates=self.default_coordinates):
            yield tweet


class StreamManager(object):
    """Manage a stream of Twitter messages by dividing the stream into two:
        - one of tweet messages;
        - one of limit messages (called metadata hereafter).

    Both streams are sent to user-provided processor functions:
    `tweet_processor_fct` and `metadata_processor_fct`.

    The manager also takes care of counting: firehose messages, tweets sent
    down to us (the stream) and detections has established by the tweet
    processor function, which for that must return the number of detections.

    Every so often, a dict object is sent to the metadata processor function.
    Something like:

        {'counts': {
            'detection': 4403,
            'firehose': 1426307,
            'stream': 122900,
            'cached': 4
            }
        }

    The manager also takes care of queuing to workers if the parameter
    `is_queuing` is set to True. This should always be done in production since
    Twitter will not wait for tweets to be processed. The faster we process the
    better.

    Finally, you have to provide a name for the manager. It is used as a redis
    namespace key for counting and resuming between calls.
    """
    __attrs__ = ['tweet_processor_fct', 'metadata_processor_fct'
                 'name', 'metadata_cache_key', 'firehose_count_key']

    def __init__(self, name, tweet_processor, metadata_processor=None,
                 is_queuing=False, cache_length=100):

        self.name = name
        self.metadata_cache_key = "counts_{}".format(self.name)
        self.firehose_count_key = "firehose_count_{}".format(self.name)

        self.redis = cache.get_redis_connection()
        self.redis.delete(self.firehose_count_key)

        self.tweet_processor_fct = tweet_processor
        self.metadata_processor_fct = metadata_processor
        self.is_queuing = is_queuing

        self.tweet_cache = []
        self.cache_length = cache_length

    def run(self, generator):
        """Gather tweets and either enqueue them for processing later by a
        worker process or process them immediately. This behavior depends on
        the `is_queuing` parameter.
        """
        for data in generator:
            # For some reason, sometime we can't jsonify TwitterResponseWrapper
            data = dict(data)

            if 'limit' in data:
                if self.metadata_processor_fct:
                    # The argument firehose_count is the total number of
                    # undelivered tweets since the connection was opened. Since
                    # we want to count irrespective of connection
                    # opening/closing we compute a delta since last count and
                    # add that to the firehose count. This allows us to keep a
                    # correct count in-between connections.
                    firehose_count = data['limit']['track']
                    firehose_delta = firehose_count - int(
                        (self.redis.getset(self.firehose_count_key,
                                           firehose_count) or 0))

                    self.redis.hincrby(self.metadata_cache_key, 'firehose',
                                       firehose_delta)
            else:
                self.tweet_cache.append(data)
                # Increment the total number of tweets in the stream.
                self.redis.hincrby(self.metadata_cache_key, "stream", 1)
                # Increment the total number of tweets in the firehose.
                # Remember, the firehose count provided by Twitter (track)
                # is the number of undelivered tweets:
                # Total = undelivered + delivered
                self.redis.hincrby(self.metadata_cache_key, 'firehose', 1)

                if len(self.tweet_cache) >= self.cache_length:
                    if self.is_queuing:
                        rqworker.enqueue(self.tweet_processor,
                                         self.tweet_cache)
                    else:
                        self.tweet_processor(self.tweet_cache)
                    # Empty cache for next batch.
                    self.tweet_cache = []

            # We might not receive limit message, be sure to call
            # metadata_processor. Don't have to worry calling it too often,
            # it's throttled.
            if self.metadata_processor_fct:
                self.metadata_processor()

    def __getstate__(self):
        return {attr: getattr(self, attr, None) for attr in self.__attrs__}

    def __setstate__(self, state):
        for attr, value in state.iteritems():
            setattr(self, attr, value)

        self.redis = cache.get_redis_connection()

    def tweet_processor(self, tweets):
        """Process tweets by calling the user provided function. Note that the
        function must return the number of positive detections, or else you
        won't have a count of detections.
        """
        log.debug("Processing {!r} tweets".format(len(tweets)))
        detection_count = self.tweet_processor_fct(tweets) or 0
        # Increment the total number of detections.
        self.redis.hincrby(self.metadata_cache_key, 'detection',
                           detection_count)

    @throttle(milliseconds=4000)
    def metadata_processor(self):
        """Compute counts and other metadata about this stream.
        Send results to the user provided processor function. The decorator
        makes sure we don't queue too often by waiting for the given amount of
        time between successive calls.
        """
        counts = {key: int(value) for key, value in
                  self.redis.hgetall(self.metadata_cache_key).iteritems()}

        counts['cached'] = len(self.tweet_cache)

        metadata = {'counts': counts}
        log.debug(metadata)

        if self.is_queuing:
            rqworker.enqueue(self.metadata_processor_fct, metadata)
        else:
            self.metadata_processor_fct(metadata)


def persist_db(database, tweets):
    """Write to a CouchDB database the given list of tweets."""
    log.debug("{} tweets to db".format(len(tweets)))

    for tweet in tweets:
        tweet['_id'] = tweet['id_str']
    database.update(tweets)


def persist_file(tweets, directory):
    """Persist given tweets to a gzipped file."""
    log.debug("{} tweets to gzipped file".format(len(tweets)))

    filename = join(directory, "{}.gz".format(date.today()))
    with gzip.open(filename, "a+") as f:
        write(tweets, f)


def write(tweets, f=None):
    """Write to the console or to the given file descriptor."""
    jsoned = [json.dumps(tweet) + '\n' for tweet in tweets]
    if f:
        f.writelines(jsoned)
    else:
        print "\n-------------\n".join([tweet['text'] for tweet in tweets])


def keep(attrs, tweets):
    """Strip each tweet so as to keep only the given attributes.
    Attributes are given as a list of the form:

        ['text', 'user.screen_name', 'user.name']

    where the dot notation represent embedded dicts:

        tweet = {
            'text': "This is a tweet."
            'user': {
                'screen_name': "John Doe"
                'name': "john_doe"
            }
        }
    """
    new_tweets = []
    for tweet in tweets:
        stripped = {}
        for attr in attrs:
            stripped = merge(stripped, find_item(attr.split('.'), tweet))
        new_tweets.append(stripped)
    return new_tweets
