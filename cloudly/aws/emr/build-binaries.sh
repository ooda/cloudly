#!/bin/bash

# This script is based on the instruction provided here: http://goo.gl/BS3uDl
#
# Its purpose is to build from source Python 2.7, build a relocatable
# virtualenv and upload both to S3 for later bootstraping an EMR jobflow.
#
# You'll need two scripts for this:
#
# - bin-build.sh: this script.
# - venv-build.sh: contains the instructions for building your customized
#   virtualenv.
#
# The following scripts will be used to build the python binaries and
# virtualenv and to install them on new nodes. 
# 
# - emr-venv-build.sh: the master script. This should be executed on a typical
#   EMR node into which you ssh'ed.
# - emr-venv-bootstrap.sh: the script to be run whenever you start a new EMR
#   jobflow.


set -e

# Set your bucket name here. This will receive the two archives created below.
S3_BUCKET=YOUR_BUCKET_NAME

ARCH=`uname -m`
VENV=venv

# Install python 2.7 with SSL support
starttime=`date +%s`
sudo apt-get install libssl-dev
cd
wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz
tar -xzf Python-2.7.3.tgz
cd Python-2.7.3
sudo ./configure --enable-shared --prefix=/usr --enable-unicode=ucs4
sudo make && sudo make install

python --version
echo "** Installed python in $((`date +%s` - $starttime)) sec"

starttime=`date +%s`
# Installed updated version of setuptools
curl http://python-distribute.org/distribute_setup.py | sudo python
# Install virtualenv
sudo easy_install virtualenv

cd
virtualenv $VENV
source $VENV/bin/activate

# The following script is specific to your virtualenv.
source venv-build.sh

echo "** Installed python libraries in $((`date +%s` - $starttime)) sec"

# Make the virtualenv relocatable, this isn't strictly necessary I think.
# virtualenv is all you need as long as you always deploy it to the right place
virtualenv --relocatable $VENV

# Zip up tarballs and send them to s3
tar -czf Python-2.7.binaries.$ARCH.tar.gz Python-2.7.3
hadoop fs -put Python-2.7.binaries.$ARCH.tar.gz s3n://$S3_BUCKET/Python-2.7.binaries.$ARCH.tar.gz
tar -czf $VENV-virtualenv.binaries.$ARCH.tar.gz $VENV
hadoop fs -put $VENV-virtualenv.binaries.$ARCH.tar.gz s3n://$S3_BUCKET/$VENV-virtualenv.binaries.$ARCH.tar.gz
