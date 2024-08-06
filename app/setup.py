"""Sets up the logger"""

import contextlib
import logging

from filters.health_check_filter import HealthCheckFilter
from filters.op_filter import OpFilter
from helper.redis_helper import RedisHelper

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(_app):
    """lifespan event"""
    setup_logger()
    async with RedisHelper() as redis:
        logger.info(id(redis))
        yield


def setup_logger():
    """Set's up loggers"""
    logger.info("Setting up loggers")
    for handler in logging.root.handlers + logging.getLogger("uvicorn.access").handlers:
        handler.addFilter(OpFilter())
        handler.addFilter(HealthCheckFilter())
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s: %(levelname)s/%(processName)s] %(op_path)s[%(op_id)s]: %(message)s"
            )
        )
