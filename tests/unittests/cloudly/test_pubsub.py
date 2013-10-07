from cloudly import pubsub


def test_pusher():
    provider = pubsub.Pusher("test")
    provider.publish("test", "event")


def test_pubnub():
    provider = pubsub.Pubnub("test")
    provider.publish("test")
