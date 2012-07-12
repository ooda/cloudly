#!/usr/bin/env python
import sys

import boto
import boto.emr
from boto.emr.step import StreamingStep
from boto.emr.bootstrap_action import BootstrapAction

#from pysem.psych import psych_analysis
#from marketsense.models import Tweet

conn = boto.connect_emr()


def start():
    bootstrap = BootstrapAction("marketsense.bootstrap",
        "s3://marketsense.io/bootstrap.sh", None)

    step = StreamingStep(name='Twitter psychological analysis - w/o Idilia',
        mapper='s3n://marketsense.io/emr.py',
        reducer=None,
        input='s3n://marketsense.io/input/april-test.json',
        output='s3n://marketsense.io/output/')

    jobid = conn.run_jobflow(name='jobflow',
        log_uri='s3://marketsense.io/jobflow_logs',
        bootstrap_actions=[bootstrap],
        steps=[step],
        enable_debugging=True)

    jobflow = conn.describe_jobflow(jobid)

    print "Your job ID is %r" % jobid
    return jobid


def stop(jobid):
    conn.terminate_jobflow(jobid)


def mapper():
    """Perform a psychological analysis on all tweets given on stdin, returning
    the result on stdout.
    """
    import json
    for line in sys.stdin:
        tweet = json.loads(line.decode("utf-8"))
        #tweet = Tweet(line.decode("utf-8"))
        #tweet['psych_analysis'] = psych_analysis(tweet.text)
        tweet['psych_analysis'] = {'done': ['yep']}
        sys.stdout.write(json.dumps(tweet).encode("utf-8") + '\n')


if __name__ == "__main__":
    mapper()
