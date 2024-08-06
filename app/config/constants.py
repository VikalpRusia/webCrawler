"""Holds constants for the project"""

OP_ID = "op_id"
OP_PATH = "op_path"

EXTENSIONS_TO_FILTER = (".png", ".css", ".xml", ".ico", ".woff2", ".asp")

# Redis config
CACHE_EXPIRY = 3500
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
