import boto
import json


def publish(topic_arn, message, subject=None):
    if message:
        connection = boto.connect_sns()
        connection.publish(topic_arn, json.dumps(message), subject)


def subscribe(topic_arn, protocol, endpoint):
    connection = boto.connect_sns()
    connection.subscribe(topic_arn, protocol, endpoint)
