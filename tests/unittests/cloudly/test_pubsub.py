from time import sleep

from mock import Mock

from cloudly import pubsub

provider = pubsub.RedisWebSocket("test")


def setup():
    provider.spawn()


def test_pusher():
    provider = pubsub.Pusher("test")
    provider.publish("test", "event")


def test_pubnub():
    provider = pubsub.Pubnub("test")
    provider.publish("test")


def test_redis():
    websocket = Mock()
    provider.register(websocket)

    provider.publish(['test-1', 'test-2'])

    sleep(10)
    print websocket.send.called
    assert(websocket.send.called)
