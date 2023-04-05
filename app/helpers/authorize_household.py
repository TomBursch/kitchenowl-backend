from flask import request
from functools import wraps

from flask_jwt_extended import current_user
from app.errors import UnauthorizedRequest
from app.models import HouseholdMember


def authorize_household(requires_admin=False) -> any:
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if not 'household_id' in kwargs:
                raise Exception("Wrong usage of authorize_household")
            if not current_user:
                raise UnauthorizedRequest()
            member = HouseholdMember.find_by_ids(
                kwargs['household_id'], current_user.id)
            if not current_user.admin:
                if not member or requires_admin and not member.admin:
                    raise UnauthorizedRequest()

            return func(*args, **kwargs)

        return decorator
    return wrapper
