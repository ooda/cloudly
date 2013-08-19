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
    scripts=['bin/sshaws', 'bin/launch', 'bin/s3get'],
    install_requires=[
        'boto',
        'redis',
        'rq',
        'couchdb',
        'python-memcached',
        'isodate',
        'cuisine',
        'pusher',
        'twitter',
        'pubnub',
        'pyyaml'
    ]
)
