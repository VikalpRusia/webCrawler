"""Custom logger"""
import logging

from config.constants import OP_PATH


class HealthCheckFilter(logging.Filter):
    # pylint: disable=too-few-public-methods
    """Remove health apis logs"""

    def filter(self, record):
        """
        ignore health api logging
        :param record:
        :return:
        """
        return record.__dict__.get(OP_PATH).find("health") == -1
