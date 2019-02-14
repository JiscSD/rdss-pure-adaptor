import os
import logging
from ..base import BasePureDataset

logger = logging.getLogger(__name__)


class PureDataset(BasePureDataset):

    MAPPING_FILE_PATH = os.path.join(os.path.dirname(
        __file__), 'research_object_mapping.txt')
