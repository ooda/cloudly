"""Metrics logged to a [Cube](http://square.github.io/cube/) server.
"""
import os
import json
import socket
from datetime import datetime

import isodate

from cloudly import logger
from cloudly.aws import ec2
from cloudly.decorators import Memoized

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
def get_cube_host(hostname=None):
    """Get the hostname for the Cube server. These are tried, in order:
        - an environment variable CUBE_HOST;
        - an EC2 hosted server offering the service 'cube';
        - 127.0.0.1.
    """
    return (
        hostname or
        os.environ.get("CUBE_HOST") or
        ec2.get_hostname("cube") or
        "127.0.0.1"
    )


def _send(data):
    try:
        udp_sock.sendto(json.dumps(data), (get_cube_host(), CUBE_UDP_PORT))
    except Exception, exception:
        log.error(exception)
