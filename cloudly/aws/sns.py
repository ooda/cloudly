import boto
import json

connection = boto.connect_sns()


def publish(topic_arn, message, subject=None):
    if message:
        connection.publish(topic_arn, json.dumps(message), subject)


def subscribe(topic_arn, protocol, endpoint):
    connection.subscribe(topic_arn, protocol, endpoint)
