import os

import redis as pyredis

from cloudly.aws import ec2
from cloudly.memoized import Memoized

@Memoized
def get_conn():
    ip_addresses = (os.environ.get("REDIS_SERVER") or
                    ec2.find_service_ip('redis-server') or 
                    ["127.0.0.1"])

    redis_url = os.getenv('REDISTOGO_URL',  # Set when on Heroku.
                          'redis://{}:6379'.format(ip_addresses[0]))
    return pyredis.from_url(redis_url)


redis = get_conn()
