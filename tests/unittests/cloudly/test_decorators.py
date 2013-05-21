from time import sleep
from datetime import datetime, timedelta

from cloudly.decorators import burst, throttle


def test_burst():
    nbursts = 3

    # Decorate a function
    @burst(nbursts)
    def func(args):
        print "function called with {}".format(args)
        return len(args)

    # Decorate a method
    class Foo(object):
        @burst(nbursts)
        def method(self, args):
            print "method called with {}".format(args)
            return len(args)
    foo = Foo()

    for n in range(1, nbursts * 2 + 1):
        result_function = func([1])
        result_method = foo.method([1])

        assert result_function == result_method
        result = result_function

        print "({}) function result: {}".format(n, result)
        if n % nbursts == 0:
            assert(result == nbursts)
        else:
            assert(result is None)


def test_throttle():
    milliseconds = 200

    # Decorate a function
    @throttle(milliseconds)
    def func(arg):
        print "function called with {}".format(arg)
        return arg

    # Decorate a method
    class Foo(object):
        @throttle(milliseconds)
        def method(self, arg):
            print "method called with {}".format(arg)
            return arg
    foo = Foo()

    interval = 0.015  # in seconds
    last_call = datetime.now()
    for n in range(0, 100):
        now = datetime.now()
        delta = now - last_call
        print "since last call: {}".format(delta)

        result = func(1)
        result = foo.method(1)
        if delta > timedelta(milliseconds=milliseconds):
            assert result
            last_call = datetime.now()
        else:
            assert result is None
        sleep(interval)
