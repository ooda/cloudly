from os.path import join, dirname

from setuptools import setup, find_packages

import cloudly

setup(
    name='cloudly',
    version=cloudly.__version__,
    description='A helper library for everything cloud.',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='Hugues Demers',
    author_email='hugues.demers@ooda.ca',
    url='https://github.com/ooda/cloudly',
    license="Proprietary",
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
        'pusher==0.7'
    ]
)
