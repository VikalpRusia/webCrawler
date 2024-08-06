"""Time taken middleware"""

import logging
import time

logger = logging.getLogger(__name__)


class TimeTakenMiddleware:
    # pylint: disable=too-few-public-methods
    """Time taken to serve request"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        start_time = time.time()
        await self.app(scope, receive, send)
        end_time = time.time()
        logger.info(f"Time taken: {end_time - start_time}")
