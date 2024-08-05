import logging

from filters.health_check_filter import HealthCheckFilter
from filters.op_filter import OpFilter

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


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
