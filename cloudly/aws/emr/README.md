Bootstraping an EMR jobflow
===========================

EMR instances run Debian 5.0 and are old. The best way to run our code (and the
most predictable) is to compile python from source and build a virtualenv
before launching a streaming job.

You'll find scripts in here to help in doing so. Two archives will be created.
The first will have a compiled python executable and associated libraries and
the second will hold our virtualenv.

The above is inspired from this [post](http://goo.gl/BS3uDl).

binaries-build.sh
-----------------

This is the main script in which python is compiled and a virtualenv is
created. This script will call another user-provided script called
*venv-build.sh* in which your commands for installing python packages should
be (e.g. `pip install` commands).

We generally want Python compiled with SSL support and that's why we make sure
libssl-dev is installed. Also, we want the UCS-4 internal unicode
representation. That's why we explicitly set the compile flag
*--enable-unicode=ucs4*.

bootstrap.sh
------------

This script is the bootstrap action given to Hadoop. It will fetch our two
archives, install python and the virtualenv.


jobrunner.sh
------------

Helper script to source a virtualenv before calling a python module. The first
argument to this script should be a python module.  It will be called like so:

    python -m myapp.mymodule
