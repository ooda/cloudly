"""Publish to a pubsub service.

Currently available:
    - [Pusher](http://pusher.com/).
    - [PubNub](http://www.pubnub.com/)
"""
import os

import pusher
import Pubnub as pubnub

from cloudly.decorators import Memoized


class Pubsub(object):
    """Encapsulate a connection to pubsub service provider.
    An instance of this class should be bound to a specific channel. If no
    credential are provided at initialization, they shall be taken from the
    environment.
    """

    def __init__(self, channel):
        self.channel = channel
        self.pubsub = None

    def publish(self, message, event):
        raise NotImplementedError("Use a subclass of this one.")

    @classmethod
    def open(cls):
        """Return an instance of this class with provided credentials."""
        raise NotImplementedError


class Pusher(Pubsub):
    """A pubsub service provider, inherit from Pubsub.

    If no credentials are provided, they're taken from the environment
    variables `PUSHER_APP_ID, `PUSHER_KEY` and `PUSHER_SECRET`.
    """

    provider_name = "pusher"
    client_key = None

    def __init__(self, channel):
        super(Pusher, self).__init__(channel)

    def publish(self, message, event):
        if not message:
            return

        self.pubsub[self.channel].trigger(event, message)

    @classmethod
    @Memoized
    def open(cls, channel, app_id=None, key=None, secret=None):
        if not (app_id and key and secret):
            app_id = os.environ.get("PUSHER_APP_ID")
            key = os.environ.get("PUSHER_KEY")
            secret = os.environ.get("PUSHER_SECRET")

        obj = cls(channel)
        obj.pubsub = pusher.Pusher(app_id=app_id, key=key, secret=secret)

        cls.client_key = key
        return obj


class Pubnub(Pubsub):
    """A pubsub service provider, inherit from Pubsub.

    If no credentials are provided, they're taken from the environment
    variables `PUBNUB_PUBLISH_KEY` and `PUBNUB_SUBSCRIBE_KEY`.
    """

    provider_name = "pubnub"

    def __init__(self, channel):
        super(Pubnub, self).__init__(channel)

    def publish(self, message, event=None):
        """Parameter event is not used by Pubnub"""
        if not message:
            return

        result = self.pubsub.publish({
            'channel': self.channel,
            'message': message,
        })

        if result[0] == 0:
            raise Exception(result[1])

    @classmethod
    @Memoized
    def open(cls, channel, publish_key=None, subscribe_key=None,
             secret_key=None, ssl_on=False):

        if not (publish_key and subscribe_key):
            publish_key = os.environ.get("PUBNUB_PUBLISH_KEY")
            subscribe_key = os.environ.get("PUBNUB_SUBSCRIBE_KEY")
            secret_key = os.environ.get("PUBNUB_SECRET_KEY")

        obj = cls(channel)
        obj.pubsub = pubnub.Pubnub(publish_key, subscribe_key,
                                   secret_key=secret_key, ssl_on=ssl_on)
        return obj
