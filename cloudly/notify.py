import os

from cloudly.aws.sns import _get_conn

SNS_NOTIFY_TOPIC_ARN = os.environ.get("SNS_NOTIFY_TOPIC_ARN", None)


def notify(subject, message):
    if SNS_NOTIFY_TOPIC_ARN is not None:
        _get_conn().publish(SNS_NOTIFY_TOPIC_ARN, message, subject)
