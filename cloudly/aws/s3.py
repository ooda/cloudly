from datetime import datetime

import isodate

import boto.s3.connection as s3


# Initialize the connection to S3.
connection = s3.S3Connection()


class S3KeyNotFoundException(Exception):
    """S3 key not found."""


def set(bucket_name, key_name, obj, metadata=None):
    bucket = connection.get_bucket(bucket_name)
    # Check if a particular key exists.
    key = bucket.get_key(key_name)
    if key is None:
        # Create a new key.
        key = s3.Key(bucket)

    # Set key unique name
    key.key = key_name
    # Set metadata if any.
    if metadata:
        for meta, data in metadata.iteritems():
            key.set_metadata(meta, _encode(data))
    # Store the document as a string.
    key.set_contents_from_string(obj)
    return key.key


def get(bucket_name, key_name, metakeys=None):
    key = _get_key(key_name, bucket_name)

    metadata = {}
    if metakeys:
        for meta in metakeys:
            metadata[meta] = key.get_metadata(meta)

    if metadata:
        return key.get_contents_as_string(), metadata
    else:
        return key.get_contents_as_string()


def list_key_names(bucket_name):
    return [key.key for key in connection.get_bucket(bucket_name)]


def delete(key_name, bucket_name="default"):
    key = _get_key(key_name, bucket_name)
    key.delete()


def _get_key(key_name, bucket_name="default"):
    bucket = connection.get_bucket(bucket_name)
    key = bucket.get_key(key_name)
    if key is None:
        raise S3KeyNotFoundException(key_name)
    return key


def _encode(obj):
    if isinstance(obj, datetime):
        string = isodate.datetime_isoformat(obj)
    elif isinstance(obj, list):
        string = _encode(u", ".join(obj))
    else:
        string = unicode(obj).encode("utf-8")
    return string
