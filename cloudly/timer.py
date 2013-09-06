import time


class Timer:
    """Timer to be used with the `with` statement.
    Inspired from
    http://preshing.com/20110924/timing-your-code-using-pythons-with-statement

    To use time.clock() set clock=True when instantiating. The elasped time in
    seconds in available as self.interval.

    """
    def __init__(self, clock=False):
        self.time_fct = time.clock if clock else time.time

    def __enter__(self):
        self.start = self.time_fct()
        return self

    def __exit__(self, *args):
        self.end = self.time_fct()
        # The elapsed time in seconds.
        self.interval = self.end - self.start
