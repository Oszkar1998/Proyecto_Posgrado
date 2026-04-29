from functools import wraps
from flask import session, redirect, url_for, abort

def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("index"))

            roles = session.get("roles", [])
            permissions = session.get("permissions", [])

            if "superadmin" in roles or "admin" in roles:
                return f(*args, **kwargs)

            if permission_name not in permissions:
                return abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator