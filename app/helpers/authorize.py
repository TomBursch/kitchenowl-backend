from flask import request
from app.helpers.db_model_mixin import DbModelMixin
from app.helpers.access_type import AccessType
from functools import wraps
from app.errors import UnauthorizedRequest


def authorizeFor(model: DbModelMixin, access: AccessType) -> any:
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if not model.authorized(access, kwargs):
                raise UnauthorizedRequest()

            return func(*args, **kwargs)

        return decorator
    return wrapper
