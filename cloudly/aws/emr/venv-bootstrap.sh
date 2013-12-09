#!/bin/bash
 
set -e 

# Set your bucket name here.
S3_BUCKET=YOUR_BUCKET_NAME

ARCH=`uname -m`
VENV=venv
PYTHON_BINARIES=Python-2.7.binaries.$ARCH.tar.gz

echo "** Building for $ARCH"
echo "** Using bucket $S3_BUCKET"

cd
hadoop fs -get s3n://$S3_BUCKET/$PYTHON_BINARIES ./
tar -xzf $PYTHON_BINARIES
cd Python-2.7.3
sudo make install
 
curl http://python-distribute.org/distribute_setup.py | sudo python
 
cd
hadoop fs -get s3n://$S3_BUCKET/$VENV-virtualenv.binaries.$ARCH.tar.gz ~/
tar -xzf $VENV-virtualenv.binaries.$ARCH.tar.gz

echo "** Finished bootstraping."
