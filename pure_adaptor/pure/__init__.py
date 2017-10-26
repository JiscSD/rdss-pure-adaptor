from collections import namedtuple
from . import base
from . import v59

PureInterface = namedtuple(
    'PureInterface',
    [
        'API',
        'Dataset',
        'DownloadManager'
    ]
)

api_version_mappings = {
    'base': PureInterface(
        API=base.BasePureAPI,
        Dataset=base.BasePureDataset,
        DownloadManager=base.BasePureDownloadManager,
    ),
    'v59': PureInterface(
        API=v59.PureAPI,
        Dataset=v59.PureDataset,
        DownloadManager=v59.PureDownloadManager,
    )
}


def versioned_pure_interface(api_version_tag):
    """TODO: Docstring for get_pure_interface.

    :api_version_tag: TODO
    :returns: PureInterface

    """
    return api_version_mappings.get(api_version_tag)


__all__ = ['versioned_pure_interface']
