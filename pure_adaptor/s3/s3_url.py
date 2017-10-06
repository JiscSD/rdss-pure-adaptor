from collections import namedtuple
from urllib.parse import urlparse

S3Url = namedtuple('S3Url', 'bucket prefix')


def parse(value):
    """ Parse url into bucket and prefix

    :param str value:
    :rtype: tuple of (str, str)
    """
    parts = urlparse(value)
    if parts.scheme != 's3':
        raise ValueError('not a valid s3 scheme')
    return S3Url(parts.netloc, parts.path.lstrip('/'))
