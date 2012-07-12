from rq import Worker, Queue, Connection
from rq.job import Job

from cloudly.cache import redis
from cloudly.memoized import Memoized

def enqueue(function, *args):
    return _get_queue().enqueue(function, *args)


def fetch_job(job_id):
    return Job.fetch(job_id, redis)


@Memoized
def _get_queue():
    return Queue(connection=redis)


if __name__ == '__main__':
    listen = ['high', 'default', 'low']
    with Connection(redis):
        worker = Worker(map(Queue, listen))
        worker.work()
