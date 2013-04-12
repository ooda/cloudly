"""Publish to [Pusher](http://pusher.com/).
"""
import os
import pusher

APP_ID = os.environ.get("PUSHER_APP_ID")
KEY = os.environ.get("PUSHER_KEY")
SECRET = os.environ.get("PUSHER_SECRET")

p = pusher.Pusher(app_id=APP_ID, key=KEY, secret=SECRET)


def publish(channel, event, message):
    result = p[channel].trigger(event, message)
    if not result:
        raise Exception("Could not publish to Pusher.")
