"""Various decorators, in no particular order and without any theme.

You might be interested in this decorator *cheat sheet*:
    https://gist.github.com/hdemers/5357602
"""
from functools import wraps, partial


class Memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    Tips & trips with this memoize:

        1. Do not use with functions that take any sort of mutable value as an
        argument, like lists, sets or dicts, or else the underlying function
        will always get called.

        2. Memoized should work with keyword values, but even then, for the
        function:

            def f(x, y=None)

        the calls f(x, None), f(x) and f(x, y=None) are *NOT* equivalent and
        will lead to f being called 3 times, so be carefull.

    Cf. http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        cache_key = (args, frozenset(kwargs.items()))  # frozenset is cacheable
        try:
            return self.cache[cache_key]
        except KeyError:
            value = self.func(*args, **kwargs)
            self.cache[cache_key] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **kwargs)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return partial(self.__call__, obj)


def burst(nbursts=2):
    """Wait `nbursts` calls before calling the wrapped function with a list of
    accumulated arguments.

    Note: the return value of the wrapped function will be None when it's not
    actually called, i.e. in between bursts.
    """
    def decorator(fn):
        cache = []

        @wraps(fn)
        def wrapped_fn(*args, **kwargs):
            cache.extend(args[0])
            result = None
            if len(cache) >= nbursts:
                result = fn(cache, *args[1:], **kwargs)
                del cache[:]
            return result
        return wrapped_fn
    return decorator
