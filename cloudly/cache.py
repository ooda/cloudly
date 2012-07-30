import os

import redis as pyredis

from cloudly.aws import ec2
from cloudly.memoized import Memoized
import cloudly.logger as logger

log = logger.init(__name__)


@Memoized
def get_conn():
    ip_address = (os.environ.get("REDIS_HOST") or
                  ec2.find_service_ip('redis')[0] or 
                  "127.0.0.1")

    redis_url = os.getenv('REDISTOGO_URL',  # Set when on Heroku.
                          'redis://{}:6379'.format(ip_address))

    log.info("Connecting to Redis server at {}".format(redis_url))
    return pyredis.from_url(redis_url)


redis = get_conn()
