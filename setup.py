from os.path import join, dirname

from setuptools import setup, find_packages

from cloudly import __title__, __version__, __author__, __email__, __license__

setup(
    name='cloudly',
    version=__version__,
    description=__title__,
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author=__author__,
    author_email=__email__,
    url='https://github.com/ooda/cloudly',
    license=__license__,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['bin/sshaws', 'bin/launch'],
    install_requires=[
        'boto==2.8.0',
        'redis==2.7.2',
        'rq==0.3.7',
        'couchdb==0.8',
        'python-memcached==1.48',
        'isodate==0.4.9',
        'cuisine==0.5.6',
        'pusher==0.7',
        'tweepy==2.0',
    ]
)
