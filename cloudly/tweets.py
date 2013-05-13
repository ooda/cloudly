import os
from twitter import TwitterStream, OAuth


def get_stream():
    """Create a TwitterStream instance using credentials taken from the
    environment.
    """
    return TwitterStream(auth=_get_auth())


def with_coordinates():
    """Yield tweets that are geolocated, i.e. their `coordinates` field is
    non-empty. This is a generator function.
    """
    stream = get_stream()
    for tweet in stream.statuses.filter(locations="-180,-90,180,90"):
        if 'coordinates' in tweet and tweet['coordinates']:
            yield tweet


def with_words(wordlist):
    """Track a list of phrases using the `filter` keyword.
    From Twitter's documentation:

    > A phrase may be one or more terms separated by spaces, and a phrase
    > will match if all of the terms in the phrase are present in the
    > Tweet, regardless of order and ignoring case. By this model, you can
    > think of commas as logical ORs, while spaces are equivalent to
    > logical ANDs (e.g. 'the twitter' is the AND twitter, and
    > 'the,twitter' is the OR twitter).

    Thus, using the example above, the parameter wordlist would be:

        wordlist = ['the twitter']
        wordlist = ['the', 'twitter']

    Cf. https://dev.twitter.com/docs/streaming-apis/parameters#track

    This is a generator function.
    """
    stream = get_stream()
    for tweet in stream.statuses.filter(track=",".join(wordlist)):
        yield tweet


def _get_auth():
    """Return a OAuth object with credentials taken from the environment."""
    consumer_key = os.environ['TWITTER_CONSUMER_KEY']
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
    access_token = os.environ['TWITTER_ACCESS_TOKEN']
    access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

    return OAuth(access_token, access_token_secret,
                 consumer_key, consumer_secret)
