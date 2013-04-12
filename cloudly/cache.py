"""This module provide access to redis and memcache servers with some sugar
coating.
"""

import os
import json

import memcache
import redis

from cloudly.aws import ec2
from cloudly.memoized import Memoized
import cloudly.logger as logger

log = logger.init(__name__)


@Memoized
def get_redis_connection(hostname=None, port=None):
    """ Get a connection to a Redis server. The priority is:
        - look for an environment variable REDISTOGO_URL (Heroku), else
        - look for an environment variable REDIS_HOST, else
        - look for an EC2 hosted server offering the service 'redis', else
        - use localhost, 127.0.0.1.
    """

    host = (
        hostname or
        os.environ.get("REDIS_HOST") or
        ec2.get_hostname("redis") or
        "127.0.0.1"
    )
    port = port or os.environ.get("REDIS_PORT", 6379)
    url = os.environ.get('REDISTOGO_URL',  # Set when on Heroku.
                         'redis://{}:{}'.format(host, port))

    log.info("Connecting to Redis server at {}".format(url))
    server = redis.from_url(url)

    # Add some utility function. These functions first
    # serialize to/from JSON the given object, then call redis get/set.
    def redis_jget(key):
        value = server.get(key)
        return json.loads(value) if value else None

    server.jset = lambda key, obj: server.set(key, json.dumps(obj))
    server.jget = redis_jget
    return server


@Memoized
def get_memcache_connection():
    return memcache.Client(['127.0.0.1:11211'], debug=0)


class MemProxy(object):
    def __init__(self):
        self.cache = get_memcache_connection()

    def set(self, key, obj, time=0):
        if key.find(" ") > -1:
            raise ValueError("A memcached key cannot contain spaces.")
        return self.cache.set(key.encode("utf-8"), obj, time=time,
                              min_compress_len=1024)

    def get(self, key):
        return self.cache.get(key.encode("utf-8"))

    def set_multi(self, mapping, time=0):
        return self.cache.set_multi(mapping, time, min_compress_len=1024)

    def get_multi(self, keys):
        return self.cache.get_multi(keys)

    def delete(self, key):
        self.cache.delete(key)


memcache = MemProxy()  # noqa
