#!/bin/bash

# Set your bucket name here.
S3_BUCKET=YOUR_BUCKET_NAME

HOME=/home/hadoop
VENV=venv

source $HOME/$VENV/bin/activate

hadoop fs -get s3n://$S3_BUCKET/env.sh $HOME
if [ $? -eq 0 ] ; then
    source $HOME/env.sh
fi

python -m $*
