"""UTC time conversion functions.
"""
from calendar import timegm
from datetime import datetime


def utcdt2epoch(utcdatetime):
    """Convert a datetime object expressed in UTC to a Unix timestamp expressed
    in seconds since the epoch (Jan 1st 1970).
    """
    return timegm(utcdatetime.timetuple())


def epoch2utcdt(epoch):
    """Convert a Unix timestamp expressed in seconds since the epoch (Jan 1st
    1970) to a datetime object expressed in UTC.
    """
    return datetime.utcfromtimestamp(epoch)
