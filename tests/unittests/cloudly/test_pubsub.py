from cloudly import pubsub


def test_pusher():
    provider = pubsub.Pusher.open("test")
    provider.publish("test", "event")


def test_pubnub():
    provider = pubsub.Pubnub.open("test")
    provider.publish("test")
