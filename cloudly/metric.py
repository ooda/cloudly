import os
import json
import socket
from datetime import datetime

import isodate

from cloudly import logger
from cloudly.aws import ec2
from cloudly.memoized import Memoized

CUBE_UDP_PORT = 1180
CUBE_EVALUATOR_PORT = 1081

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
log = logger.init(__name__)


def event(evt_type, data=None):
    event = {
        'type': evt_type,
        'time': isodate.datetime_isoformat(datetime.utcnow()),
    }
    if data:
        event.update({'data': data})
    _send(event)


@Memoized
def get_cube_host():
    host = os.environ.get("CUBE_HOST")
    if not host:
        try:
            service_ips = ec2.find_service_ip('cube')
            host = service_ips[0]
        except Exception, exception:
            log.warning(exception)
            raise Exception("Cannot connect to Cube service.")
    return host


def _send(data):
    try:
        udp_sock.sendto(json.dumps(data), (get_cube_host(), CUBE_UDP_PORT))
    except Exception, exception:
        log.error(exception)
