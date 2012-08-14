from rq import Worker, Queue, Connection
from rq.job import Job

from cloudly.cache import redis
from cloudly.memoized import Memoized


def enqueue(function, *args, **kwargs):
    return _get_queue().enqueue(function, *args, **kwargs)


def fetch_job(job_id):
    return Job.fetch(job_id, redis)


@Memoized
def _get_queue():
    return Queue(connection=redis)


def work(setup_fct=None):
    if setup_fct:
        setup_fct()
    listen = ['high', 'default', 'low']
    with Connection(redis):
        worker = Worker(map(Queue, listen))
        worker.work()


if __name__ == '__main__':
    work()
