import os

import couchdb

from cloudly.memoized import Memoized
import cloudly.logger as logger

log = logger.init(__name__)


@Memoized
def get_server(hostname=None, port=5984, username=None, password=None):
    port = 5984
    host = hostname or os.environ.get("COUCHDB_HOST", "127.0.0.1")
    url = "http://{host}:{port}".format(
        host=host,
        port=port
    )

    if username is not None and password is not None:
        url = "http://{username}:{password}@{host}:{port}".format(
            host=host,
            port=port,
            username=username,
            password=password
        )

    log.info("Connecting to CouchDB server at {}".format(url))
    return couchdb.Server(url)
