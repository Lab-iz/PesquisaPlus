from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*roles):
    allowed = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role_slug not in allowed:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def user_can_access_project(user, project):
    if user.role_slug == "admin":
        return True
    if user.role_slug == "student":
        return project.student_id == user.id
    if user.role_slug == "advisor":
        return project.advisor_id == user.id
    return False
