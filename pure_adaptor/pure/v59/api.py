from ..base import BasePureAPI
from .models import PureDataset


class PureAPI(BasePureAPI):
    """Abstraction over the Pure API v5.9"""

    API_VERSION = 'v5.9'
    DATASET_CLASS = PureDataset
