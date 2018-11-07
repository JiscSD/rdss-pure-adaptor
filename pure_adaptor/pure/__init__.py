import logging
from collections import namedtuple
from . import v59, v512

logger = logging.getLogger(__name__)

PureInterface = namedtuple(
    'PureInterface',
    [
        'API',
        'Dataset',
        'DownloadManager'
    ]
)

API_VERSION_MAPPINGS = {
    'v59': PureInterface(
        API=v59.PureAPI,
        Dataset=v59.PureDataset,
        DownloadManager=v59.PureDownloadManager,
    ),
    'v512': PureInterface(
        API=v512.PureAPI,
        Dataset=v512.PureDataset,
        DownloadManager=v512.PureDownloadManager,
    )
}


def versioned_pure_interface(api_version_tag):
    try:
        return API_VERSION_MAPPINGS[api_version_tag]
    except KeyError:
        logging.exception(
            'The provided Pure API version tag must be one of: %s',
            ', '.join(API_VERSION_MAPPINGS.keys())
        )


__all__ = ['versioned_pure_interface']
