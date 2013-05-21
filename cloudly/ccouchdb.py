"""
Provide CouchDB utility functions.

"""
import os
import yaml

import couchdb

from cloudly.decorators import Memoized
import cloudly.logger as logger
from cloudly.aws import ec2

log = logger.init(__name__)


@Memoized
def get_server(hostname=None, port=None, username=None, password=None):
    """Return a server instance.

    The following heuristic is used to find the server:
        - function arguments take precedence over all else,
        - environment variable COUCHDB_HOST is used otherwise,
        - use the service finder of cloudly.aws.ec2 to look up a couchdb
          server if none was found so far,
        - else use 127.0.0.1
    """
    host = (
        hostname or
        os.environ.get("COUCHDB_HOST") or
        ec2.get_hostname("couchdb") or
        "127.0.0.1"
    )
    port = port or os.environ.get("COUCHDB_PORT", 5984)
    username = username or os.environ.get("COUCHDB_USERNAME", None)
    password = password or os.environ.get("COUCHDB_PASSWORD", None)

    if username is not None and password is not None:
        url = "http://{username}:{password}@{host}:{port}".format(
            host=host,
            port=port,
            username=username,
            password=password
        )
        log.info("{} port {}, authenticated".format(host, port))
    else:
        url = "http://{host}:{port}".format(
            host=host,
            port=port
        )
        log.info("{} port {}".format(host, port))

    return couchdb.Server(url)


def get_or_create(server, database_name):
    try:
        database = server[database_name]
    except couchdb.http.ResourceNotFound:
        database = server.create(database_name)
    return database


def sync_design_doc(database, design_filename):
    """Sync a design document written as a YAML file."""
    with open(design_filename) as design_file:
        design_doc = yaml.load(design_file)
    # Delete old document, to avoid ResourceConflict exceptions.
    old = database.get(design_doc['_id'])
    if old:
        database.delete(old)
    database.save(design_doc)


def update_feed(database_name, include_docs=False):
    """Return a continuous feed of updates to the database.
    The most recent changes are returned.
    """
    db = get_server()[database_name]
    since = db.info()['update_seq']
    return db.changes(feed='continuous',
                      include_docs=include_docs,
                      since=since)
