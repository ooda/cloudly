import boto
import json

from cloudly.memoized import Memoized


def publish(topic_arn, message, subject=None):
    if message:
        _get_conn().publish(topic_arn, json.dumps(message), subject)


def subscribe(topic_arn, protocol, endpoint):
    _get_conn().subscribe(topic_arn, protocol, endpoint)



@Memoized
def _get_conn():
    return boto.connect_sns()
