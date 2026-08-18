from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import User


def _role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.role != role:
                raise PermissionDenied("You don't have access to this page.")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


donor_required = _role_required(User.Role.DONOR)
bank_required = _role_required(User.Role.BANK)
