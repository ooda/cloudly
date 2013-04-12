"""
Utilities around [RQ](http://python-rq.org/) workers and jobs.

"""

import logging

from rq import Worker, Queue, Connection
from rq.job import Job

from cloudly.cache import get_redis_connection
from cloudly.decorators import Memoized
from cloudly.logger import configure_logger
from cloudly import logger

log = logger.init(__name__)


def enqueue(function, *args, **kwargs):
    return get_queue().enqueue(function, *args, **kwargs)


def fetch_job(job_id):
    return Job.fetch(job_id, get_redis_connection())


@Memoized
def get_queue():
    return Queue(connection=get_redis_connection())


def work(setup_fct=None, exc_handler=None, log_level=logging.WARN):
    if setup_fct:
        setup_fct()
    listen = ['high', 'default', 'low']
    with Connection(get_redis_connection()):
        worker = Worker(map(Queue, listen))
        configure_logger(worker.log, log_level=log_level)
        if exc_handler:
            worker.push_exc_handler(exc_handler)
        log.info("Starting work.")
        worker.work()


def count():
    return get_queue().count

if __name__ == '__main__':
    work()
