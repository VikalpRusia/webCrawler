"""Custom logger"""
import logging

from config.constants import OP_ID, OP_PATH
from middlewares.uuid_middleware import get_key


class OpFilter(logging.Filter):
    # pylint: disable=too-few-public-methods
    """Filter class to apply filer to health api"""

    def filter(self, record):
        """
        ignore health api logging
        :param record:
        :return:
        """
        op_id = get_key(OP_ID)
        op_path = get_key(OP_PATH)
        if op_id:
            record.__dict__.update(op_id=op_id)
        else:
            record.__dict__.setdefault(OP_ID, "???")

        if op_path:
            record.__dict__.update(op_path=op_path)
        else:
            record.__dict__.setdefault(OP_PATH, "???")

        return True
