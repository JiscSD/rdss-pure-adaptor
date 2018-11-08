from ..base import BasePureAPI
from .models import PureDataset


class PureAPI(BasePureAPI):
    """Abstraction over the Pure API v5.12"""

    API_VERSION = 'v5.12'
    DATASET_CLASS = PureDataset
