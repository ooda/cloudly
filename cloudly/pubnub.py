"""Publish to [PubNub](http://www.pubnub.com/).
"""
import os
import logging

import Pubnub

PUBLISH_KEY = os.environ.get("PUBNUB_PUBLISH_KEY")
SUBSCRIBE_KEY = os.environ.get("PUBNUB_SUBSCRIBE_KEY")

pubnub = Pubnub(PUBLISH_KEY, SUBSCRIBE_KEY, secret_key=None, ssl_on=False)


def publish(channel, message):
    if not message:
        return
    if not isinstance(message, list):
        message = [message]
    _pubnub_publish(channel, message)


def _pubnub_publish(channel, message):
    result = pubnub.publish({
        'channel': channel,
        'message': message
    })

    if result[0] == 0:
        logging.error(result[1])
