import os
import json

import tweepy

from cloudly import logger

log = logger.init(__name__)


def filter(wordlist, func, async=False):
    """Retrieve all tweets mentioning the given words. Process each tweet
    through `func`.
    """
    _get_streamer(func).filter(track=wordlist, async=async)


def sample(func):
    """Retrieve all available tweets, really a sample of the firehose. Process
    each tweet through `func`.
    """
    _get_streamer(func).sample()


def follow_list(user_id, slug, func):
    """Prints on the console all tweets from the given list (slug)."""
    follow_list = _get_list_member_ids(user_id, slug)
    _get_streamer(func).filter(follow_list)


def _get_streamer(func):
    listener = StreamProcessor(func)
    return tweepy.Stream(_get_auth(), listener, timeout=None)


def _get_list_member_ids(user_id, slug):
    return [member.id for member in
            tweepy.Cursor(_api().list_members, owner=user_id,
                          slug=slug).items()]


def _api():
    return tweepy.API(_get_auth())


def _get_auth():
    try:
        twitter_consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        twitter_consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
        twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    except KeyError, exception:
        log.error("Please provide Twitter auth keys and tokens: {}".format(
            exception))
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    return auth


class StreamProcessor(tweepy.StreamListener):
    """Listener that process the raw Twitter stream through a function given to
    __init__."""

    def __init__(self, processor_fct):
        super(StreamProcessor, self).__init__()
        self.processor_fct = processor_fct

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            self.processor_fct(tweet)
        except ValueError, exception:
            log.error(exception)

    def on_error(self, status_code):
        log.error('An error has occurred! Status code: {}'.format(
            status_code))
        if status_code == 401:
            log.error("Unauthorized. Please make sure you have correct "
                      "Twitter auth keys and tokens.")
            return False
        return True  # keep stream alive

    def on_timeout(self):
        log.debug('Snoozing Zzzzzz')
