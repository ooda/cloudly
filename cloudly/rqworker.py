from rq import Worker, Queue, Connection
from rq.job import Job

from cloudly.cache import get_redis_connection
from cloudly.memoized import Memoized


def enqueue(function, *args, **kwargs):
    return _get_queue().enqueue(function, *args, **kwargs)


def fetch_job(job_id):
    return Job.fetch(job_id, get_redis_connection())


@Memoized
def _get_queue():
    return Queue(connection=get_redis_connection())


def work(setup_fct=None, exc_handler=None):
    if setup_fct:
        setup_fct()
    listen = ['high', 'default', 'low']
    with Connection(get_redis_connection()):
        worker = Worker(map(Queue, listen))
        if exc_handler:
            worker.push_exc_handler(exc_handler)
        worker.work()


if __name__ == '__main__':
    work()
