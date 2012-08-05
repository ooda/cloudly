"""This module provide access to redis and memcache servers with some sugar
coating.
"""

import os
import json

import memcache
import redis as pyredis

from cloudly.aws import ec2
from cloudly.memoized import Memoized
import cloudly.logger as logger

log = logger.init(__name__)


@Memoized
def get_redis_connection():
    """ Get a connection to a Redis server. The priority is:
        - look for an environment variable REDIS_HOST, else
        - look for an EC2 hosted server offering the service 'redis', else
        - use localhost, 127.0.0.1.
    """
    try:
        service_ips = ec2.find_service_ip('redis')
    except Exception, exception:
        log.warning(exception)
        service_ips = []

    ip_address = (os.environ.get("REDIS_HOST") or
                  service_ips[0] if service_ips else None or
                  "127.0.0.1")

    redis_url = os.getenv('REDISTOGO_URL',  # Set when on Heroku.
                          'redis://{}:6379'.format(ip_address))

    log.info("Connecting to Redis server at {}".format(redis_url))
    return pyredis.from_url(redis_url)


redis = get_redis_connection()


# Add some utility function to module redis. These function first serialize
# to/from JSON the given object.
def redis_jget(key):
    value = redis.get(key)
    return json.loads(value) if value else None

redis.jset = lambda key, obj: redis.set(key, json.dumps(obj))
redis.jget = redis_jget


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


memcache = MemProxy()
