Cloudly
=======

We use a lot of cloud stuff here at OODA Technologies. This library
contains all sort of small helper modules from quickly launching an EC2 instance
and configuring it according to our taste to wrappers around pub/sub providers,
to easy connection to a CouchDB.

Currently, this includes wrappers and tools for:

 - AWS
 - Redis
 - Redis queues using [RQ](http://python-rq.org/)
 - CouchDB
 - memoization
 - metrics using [Cube](http://square.github.com/cube/)
 - logging
 - notification using SNS
 - publish/subscribe using [PubNub](http://www.pubnub.com/) or
   [Pusher](http://pusher.com/)

Installation instructions are below. Contribution instructions are in
[CONTRIBUTING.md](CONTRIBUTING.md). 


Installation
------------

You'll need:

 - a redis server
 - AWS EC2 API tools

On Ubuntu do:

    sudo apt-get install redis-server ec2-api-tools

Then clone this repository:

    git clone git@github.com:ooda/cloudly.git

And install all requirements:

    pip install -r requirements.txt
