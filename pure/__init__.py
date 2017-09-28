from collections import namedtuple
import pure.base
import pure.v59

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
                API             = pure.base.BasePureAPI,
                Dataset         = pure.base.BasePureDataset,
                DownloadManager = pure.base.BasePureDownloadManager,
                ), 
            'v59': PureInterface(
                API             = pure.v59.PureAPI,
                Dataset         = pure.v59.PureDataset,
                DownloadManager = pure.v59.PureDownloadManager,
                )
            }

def versioned_pure_interface(api_version_tag):
    """TODO: Docstring for get_pure_interface.

    :api_version_tag: TODO
    :returns: PureInterface

    """
    return api_version_mappings.get(api_version_tag)

__all__ = ['versioned_pure_interface']
