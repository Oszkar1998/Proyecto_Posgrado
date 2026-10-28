from flask import Flask, abort, render_template, request, redirect, url_for, session, g
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
from auth import permission_required

import logging
logging.basicConfig(level=logging.DEBUG)


# Importar los Blueprints de los módulos
from modules.actasGrado import actas_grado_bp
from modules.revision import revision_bp
from modules.examen import examen_bp
from modules.dgae import dgae_bp
from modules.dgaeGrado import dgaeGrado_bp
from modules.votosOficio import votos_Oficio_PUEI_bp
from modules.candidatura import candidatura_bp
from modules.captura import captura_bp
from modules.pagoExamen import pagoExamen_bp
from modules.actasCandidatura import actas_candidatura_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-cambiar-en-produccion")

# ── Manejadores de error ──────────────────────────────
@app.errorhandler(400)
def error_400(e):
    return render_template("error.html", codigo=400, mensaje="Solicitud inválida."), 400

@app.errorhandler(401)
def error_401(e):
    return render_template("error.html", codigo=401, mensaje="Sesión expirada. Inicia sesión de nuevo."), 401

@app.errorhandler(403)
def error_403(e):
    return render_template("error.html", codigo=403, mensaje="No tienes permiso para realizar esta acción."), 403

@app.errorhandler(404)
def error_404(e):
    return render_template("error.html", codigo=404, mensaje="La página que buscas no existe."), 404

@app.errorhandler(500)
def error_500(e):
    return render_template("error.html", codigo=500, mensaje="Error interno del servidor. Intenta de nuevo."), 500
# ─────────────────────────────────────────────────────
 
# Registrar Blueprints
app.register_blueprint(actas_grado_bp, url_prefix='/actasGrado')
app.register_blueprint(revision_bp, url_prefix='/revision')
app.register_blueprint(examen_bp, url_prefix='/examen')
app.register_blueprint(dgae_bp, url_prefix='/dgae')
app.register_blueprint(dgaeGrado_bp, url_prefix='/dgaeGrado')
app.register_blueprint(votos_Oficio_PUEI_bp, url_prefix='/votosOficio')
app.register_blueprint(candidatura_bp, url_prefix="/candidatura")
app.register_blueprint(captura_bp, url_prefix="/captura")
app.register_blueprint(pagoExamen_bp, url_prefix="/pagoExamen")
app.register_blueprint(actas_candidatura_bp, url_prefix='/actasCandidatura')


from config import direccionBase as DATABASE


def get_user_roles(user_id):
    db = get_db()
    cursor = db.execute("""
        SELECT r.name
        FROM roles r
        INNER JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = ?
    """, (user_id,))
    return [row["name"] for row in cursor.fetchall()]

def get_user_permissions(user_id):
    db = get_db()
    cursor = db.execute("""
        SELECT p.name
        FROM permissions p
        INNER JOIN user_permissions up ON p.id = up.permission_id
        WHERE up.user_id = ?
    """, (user_id,))
    return [row["name"] for row in cursor.fetchall()]

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("index"))

        roles = session.get("roles", [])
        if "superadmin" not in roles:
            return abort(403)

        return f(*args, **kwargs)
    return decorated_function


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        db.commit()

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = request.args.get("mensaje")
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        db = get_db()

        cursor = db.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["roles"] = get_user_roles(user["id"])
            session["permissions"] = get_user_permissions(user["id"])
            return redirect(url_for("home"))
        else:
            return render_template("index.html", error="Credenciales incorrectas.")

    return render_template(
        "index.html",
        message="Registro exitoso. Ahora puedes iniciar sesión." if mensaje == "registro_exitoso" else None
    )

@app.route("/register", methods=["GET", "POST"])
@superadmin_required
def register():
    db = get_db()

    def get_permissions():
        return db.execute("SELECT name, description FROM permissions ORDER BY name").fetchall()

    if request.method == "GET":
        return render_template("register.html", permissions=get_permissions())

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    is_admin = request.form.get("is_admin")
    selected_permissions = request.form.getlist("permissions")

    if not email or not password:
        return render_template("register.html", permissions=get_permissions(),
                               error="Correo y contraseña son obligatorios.")

    if len(password) < 6:
        return render_template("register.html", permissions=get_permissions(),
                               error="La contraseña debe tener al menos 6 caracteres.")

    if is_admin != "1" and not selected_permissions:
        return render_template("register.html", permissions=get_permissions(),
                               error="Debes seleccionar al menos un permiso o marcar como administrador.")

    try:
        hashed_password = generate_password_hash(password)
        cursor = db.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                            (email, hashed_password))
        db.commit()
        user_id = cursor.lastrowid

        if is_admin == "1":
            db.execute("""
                INSERT OR IGNORE INTO user_roles (user_id, role_id)
                SELECT ?, id FROM roles WHERE name = 'admin'
            """, (user_id,))
        else:
            for permission_name in selected_permissions:
                db.execute("""
                    INSERT OR IGNORE INTO user_permissions (user_id, permission_id)
                    SELECT ?, id FROM permissions WHERE name = ?
                """, (user_id, permission_name))

        db.commit()
        return render_template("register.html", permissions=get_permissions(),
                               message="Usuario creado y permisos asignados correctamente.")

    except sqlite3.IntegrityError:
        return render_template("register.html", permissions=get_permissions(),
                               error="El correo ya está registrado.")

@app.route("/manage_users")
@superadmin_required
def manage_users():
    db = get_db()
    cursor = db.execute("""
        SELECT id, email
        FROM users
        ORDER BY id
    """)
    users = cursor.fetchall()
    return render_template(
        "manage_users.html",
        users=users,
        current_user_id=session["user_id"]
    )

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@superadmin_required
def edit_user(user_id):
    db = get_db()

    user = db.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        return abort(404)

    if user_id == session["user_id"]:
        return abort(403)

    if request.method == "GET":
        all_permissions = db.execute("""
            SELECT id, name, description
            FROM permissions
            ORDER BY name
        """).fetchall()

        user_permissions = db.execute("""
            SELECT p.name
            FROM permissions p
            INNER JOIN user_permissions up ON p.id = up.permission_id
            WHERE up.user_id = ?
        """, (user_id,)).fetchall()

        user_roles = db.execute("""
            SELECT r.name
            FROM roles r
            INNER JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = ?
        """, (user_id,)).fetchall()

        current_permissions = [row["name"] for row in user_permissions]
        current_roles = [row["name"] for row in user_roles]

        return render_template(
            "edit_user.html",
            user=user,
            all_permissions=all_permissions,
            current_permissions=current_permissions,
            current_roles=current_roles
        )

    is_admin = request.form.get("is_admin")
    selected_permissions = request.form.getlist("permissions")

    db.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
    db.execute("DELETE FROM user_permissions WHERE user_id = ?", (user_id,))

    if is_admin == "1":
        db.execute("""
            INSERT OR IGNORE INTO user_roles (user_id, role_id)
            SELECT ?, id FROM roles WHERE name = 'admin'
        """, (user_id,))
    else:
        if not selected_permissions:
            all_permissions = db.execute("""
                SELECT id, name, description
                FROM permissions
                ORDER BY name
            """).fetchall()

            return render_template(
                "edit_user.html",
                user=user,
                all_permissions=all_permissions,
                current_permissions=[],
                current_roles=[],
                error="Debes seleccionar al menos un permiso o marcar como administrador."
            )

        for permission_name in selected_permissions:
            db.execute("""
                INSERT OR IGNORE INTO user_permissions (user_id, permission_id)
                SELECT ?, id FROM permissions WHERE name = ?
            """, (user_id, permission_name))

    db.commit()
    return redirect(url_for("manage_users"))


@app.route("/delete_user/<int:user_id>", methods=["POST"])
@superadmin_required
def delete_user(user_id):
    # No puede eliminarse a sí mismo
    if user_id == session["user_id"]:
        return abort(403)

    db = get_db()

    user = db.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return abort(404)

    # Eliminar permisos, roles y usuario
    db.execute("DELETE FROM user_permissions WHERE user_id = ?", (user_id,))
    db.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()

    return redirect(url_for("manage_users"))


@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template(
        "home.html",
        roles=session.get("roles", []),
        permissions=session.get("permissions", [])
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
    