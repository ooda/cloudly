import os

import redis as pyredis

from cloudly.aws import ec2
from cloudly.memoized import Memoized

@Memoized
def get_conn():
    hosts = filter(lambda h: 'redis-server' in h.services, ec2.all())
    if hosts:
        redis_server = ec2.get_best_ip_addresse(hosts[0])
    else:
        redis_server = "localhost"
    redis_url = os.getenv('REDISTOGO_URL',  # Set when on Heroku.
                          'redis://{}:6379'.format(redis_server))
    return pyredis.from_url(redis_url)


redis = get_conn()
