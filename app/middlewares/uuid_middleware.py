"""Middleware module"""
from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request

from config.constants import OP_ID, OP_PATH

_mapping = {
    OP_ID: ContextVar(OP_ID, default="???"),
    OP_PATH: ContextVar(OP_PATH, default="???"),
}


def get_key(key):
    """get _op_id"""
    return _mapping[key].get()


def set_key(key, value):
    """set _op_id"""
    return _mapping[key].set(value)


def reset_key(key, value):
    """reset op_id"""
    _mapping[key].reset(value)


class UUIDMiddleware:
    # pylint: disable=too-few-public-methods
    """Add op_id to log"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        op_id = set_key(OP_ID, str(uuid4()))
        if scope["type"] == "lifespan":
            op_path = set_key(OP_PATH, "lifespan")
        else:
            request = Request(scope)
            op_path = set_key(OP_PATH, request.scope["path"])
        await self.app(scope, receive, send)
        reset_key(OP_ID, op_id)
        reset_key(OP_PATH, op_path)
