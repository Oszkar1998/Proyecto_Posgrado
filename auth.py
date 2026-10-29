from functools import wraps
from flask import session, redirect, url_for, abort, request, jsonify


def _espera_json():
    """True cuando la petición viene del JavaScript de la página (fetch con JSON
    o ruta /api/), no de navegar a una página. En ese caso conviene responder
    con un mensaje que la pantalla pueda mostrar, en vez de una redirección."""
    return (
        request.is_json
        or "/api/" in request.path
        or request.accept_mimetypes.best == "application/json"
    )


def permission_required(*permission_names):
    """Exige sesión iniciada y al menos UNO de los permisos indicados.

    Uso:
        @permission_required("votos_puei")
        @permission_required("candidatura", "captura_candidatura")

    superadmin y admin pasan siempre.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                if _espera_json():
                    return jsonify(success=False,
                                   error="Tu sesión expiró. Vuelve a iniciar sesión."), 401
                return redirect(url_for("index"))

            roles = session.get("roles", [])
            permissions = session.get("permissions", [])

            if "superadmin" in roles or "admin" in roles:
                return f(*args, **kwargs)

            if not any(p in permissions for p in permission_names):
                if _espera_json():
                    return jsonify(success=False,
                                   error="No tienes permiso para esta acción."), 403
                return abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
