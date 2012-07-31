import os

import redis as pyredis

from cloudly.aws import ec2
from cloudly.memoized import Memoized
import cloudly.logger as logger

log = logger.init(__name__)


@Memoized
def get_conn():
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


redis = get_conn()
