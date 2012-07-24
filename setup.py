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
    install_requires=['distribute', 'boto', 'redis', 'rq']
)
