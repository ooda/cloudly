import os
import yaml

import couchdb

from cloudly.memoized import Memoized
import cloudly.logger as logger

log = logger.init(__name__)


@Memoized
def get_server(hostname=None, port=None, username=None, password=None):
    host = hostname or os.environ.get("COUCHDB_HOST", "127.0.0.1")
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
    else:
        url = "http://{host}:{port}".format(
            host=host,
            port=port
        )

    log.info("{} port {}".format(host, port))
    return couchdb.Server(url)


def sync_design_doc(database, design_filename):
    """Sync a design document written as a YAML file."""
    with open(design_filename) as design_file:
        design_doc = yaml.load(design_file)
    # Delete old document, to avoid ResourceConflict exceptions.
    old = database.get(design_doc['_id'])
    if old:
        database.delete(old)
    database.save(design_doc)
