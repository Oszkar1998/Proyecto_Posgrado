import io
from flask import Blueprint, render_template, request, url_for, send_file, abort, redirect, flash, jsonify
from datetime import datetime
from auth import permission_required
from db import get_connection

actas_candidatura_bp = Blueprint('actas_candidatura', __name__, template_folder='../templates')

EVALUACIONES_VALIDAS = ["PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                        "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"]
RESULTADOS_VALIDOS = ["Aprobado", "No aprobado"]


@actas_candidatura_bp.route("/", methods=["GET", "POST"])
@permission_required("actas_candidatura")
def index():
    resultados = []
    mensaje = None

    if request.method == "POST":
        numeroCuenta  = request.form.get("numeroCuenta", "").strip()
        nombreAlumno  = request.form.get("nombreAlumno", "").strip()
        sinodal       = request.form.get("sinodal", "").strip()
        fecha_inicio  = request.form.get("fechaInicio", "").strip()
        fecha_fin     = request.form.get("fechaFin", "").strip()

        with get_connection() as conn:
            cursor = conn.cursor()

            if numeroCuenta and not nombreAlumno and not sinodal:
                cursor.execute("""
                    SELECT id, numeroCuenta, nombre, fecha, evaluacion, resultadoExamen
                    FROM actasCandidatura
                    WHERE numeroCuenta = ?
                    ORDER BY fecha DESC
                """, (numeroCuenta,))
                resultados = cursor.fetchall()
                if not resultados:
                    mensaje = "No se encontraron resultados para ese número de cuenta."

            elif nombreAlumno and not sinodal:
                nombre_buscar = nombreAlumno.upper()
                f_ini = f_fin = None
                rango_valido = False
                if fecha_inicio and fecha_fin:
                    try:
                        f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                        rango_valido = True
                    except ValueError:
                        mensaje = "Formato de fecha no válido."

                cursor.execute("""
                    SELECT id, numeroCuenta, nombre, fecha, evaluacion, resultadoExamen
                    FROM actasCandidatura
                """)
                filas = cursor.fetchall()
                for fila in filas:
                    if fila[2] and nombre_buscar in fila[2].upper():
                        if rango_valido:
                            try:
                                f_acta = datetime.strptime(fila[3], "%Y-%m-%d")
                                if not (f_ini <= f_acta <= f_fin):
                                    continue
                            except Exception:
                                continue
                        resultados.append(fila)
                if not resultados and not mensaje:
                    mensaje = "No se encontraron actas con ese nombre."

            elif sinodal:
                sinodal_buscar = sinodal.lower()
                f_ini = f_fin = None
                rango_valido = False
                if fecha_inicio and fecha_fin:
                    try:
                        f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                        rango_valido = True
                    except ValueError:
                        mensaje = "Formato de fecha no válido."

                cursor.execute("""
                    SELECT id, numeroCuenta, nombre, fecha, evaluacion, resultadoExamen,
                           presidente, secretario, vocal1, vocal2, vocal3
                    FROM actasCandidatura
                """)
                filas = cursor.fetchall()
                for fila in filas:
                    jurado = [str(fila[i] or "").lower() for i in range(6, 11)]
                    if any(sinodal_buscar in j for j in jurado):
                        if rango_valido:
                            try:
                                f_acta = datetime.strptime(fila[3], "%Y-%m-%d")
                                if not (f_ini <= f_acta <= f_fin):
                                    continue
                            except Exception:
                                continue
                        resultados.append(fila[:6])
                if not resultados and not mensaje:
                    mensaje = "No se encontraron actas con ese sinodal."

            elif fecha_inicio and fecha_fin:
                try:
                    f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                    f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                    cursor.execute("""
                        SELECT id, numeroCuenta, nombre, fecha, evaluacion, resultadoExamen
                        FROM actasCandidatura
                    """)
                    filas = cursor.fetchall()
                    for fila in filas:
                        try:
                            f_acta = datetime.strptime(fila[3], "%Y-%m-%d")
                            if f_ini <= f_acta <= f_fin:
                                resultados.append(fila)
                        except Exception:
                            continue
                    if not resultados:
                        mensaje = "No se encontraron resultados en ese rango de fechas."
                except ValueError:
                    mensaje = "Formato de fecha no válido."

    return render_template("actasCandidatura.html", resultados=resultados, mensaje=mensaje)


@actas_candidatura_bp.route("/ver_pdf/<int:registro_id>")
def ver_pdf(registro_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT actaPDF FROM actasCandidatura WHERE id=?", (registro_id,))
        archivo = cursor.fetchone()

    if archivo and archivo[0]:
        return send_file(io.BytesIO(archivo[0]), mimetype='application/pdf')
    else:
        return abort(404)


@actas_candidatura_bp.route("/guardar", methods=["POST"])
def guardar_acta():
    numeroCuenta       = (request.form.get("numeroCuenta") or "").strip()
    nombre             = (request.form.get("nombre") or "").strip()
    semestreIngreso    = (request.form.get("semestreIngreso") or "").strip()
    semestrePresentado = (request.form.get("semestrePresentado") or "").strip()
    evaluacion         = (request.form.get("evaluacion") or "").strip().upper()
    fecha              = (request.form.get("fecha") or "").strip()
    hora               = (request.form.get("hora") or "").strip()
    resultadoExamen    = (request.form.get("resultadoExamen") or "").strip()
    presidente         = (request.form.get("presidente") or "").strip()
    secretario         = (request.form.get("secretario") or "").strip()
    vocal1             = (request.form.get("vocal1") or "").strip()
    vocal2             = (request.form.get("vocal2") or "").strip()
    vocal3             = (request.form.get("vocal3") or "").strip()

    required = [numeroCuenta, nombre, semestreIngreso, semestrePresentado,
                evaluacion, fecha, hora, resultadoExamen]
    if any(not x for x in required):
        flash("Faltan campos obligatorios para guardar el registro.", "error")
        return redirect(url_for("actas_candidatura.index", open="capturar"))

    if evaluacion not in EVALUACIONES_VALIDAS:
        flash("La evaluación debe ser PRIMERA o SEGUNDA.", "error")
        return redirect(url_for("actas_candidatura.index", open="capturar"))

    if resultadoExamen not in RESULTADOS_VALIDOS:
        flash("El resultado debe ser Aprobado o No aprobado.", "error")
        return redirect(url_for("actas_candidatura.index", open="capturar"))

    if not numeroCuenta.isdigit() or len(numeroCuenta) != 9:
        flash("El número de cuenta debe tener 9 dígitos numéricos.", "error")
        return redirect(url_for("actas_candidatura.index", open="capturar"))

    f = request.files.get("actaPDF")
    if not f or f.filename == "":
        flash("Debes adjuntar el PDF escaneado del acta.", "error")
        return redirect(url_for("actas_candidatura.index", open="capturar"))

    pdf_bytes = f.read()

    if not pdf_bytes.startswith(b"%PDF"):
        flash("El archivo adjunto no parece ser un PDF válido.", "error")
        return redirect(url_for("actas_candidatura.index", open="capturar"))

    if len(pdf_bytes) > 15 * 1024 * 1024:
        flash("El PDF excede 15MB. Comprime o reduce el archivo.", "error")
        return redirect(url_for("actas_candidatura.index", open="capturar"))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO actasCandidatura (
                numeroCuenta, nombre, semestreIngreso, semestrePresentado,
                evaluacion, fecha, hora, resultadoExamen,
                presidente, secretario, vocal1, vocal2, vocal3, actaPDF
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            numeroCuenta, nombre, semestreIngreso, semestrePresentado,
            evaluacion, fecha, hora, resultadoExamen,
            presidente, secretario, vocal1, vocal2, vocal3,
            bytes(pdf_bytes)
        ))
        conn.commit()

    flash("Se guardó correctamente el registro.", "success")
    return redirect(url_for("actas_candidatura.index"))


@actas_candidatura_bp.route("/get_acta", methods=["POST"])
def get_acta_json():
    data = request.get_json(silent=True) or {}
    registro_id = data.get("id")

    if not registro_id:
        return {"error": "Falta el id del registro."}, 400

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, numeroCuenta, nombre, semestreIngreso, semestrePresentado,
                   evaluacion, fecha, hora, resultadoExamen,
                   presidente, secretario, vocal1, vocal2, vocal3
            FROM actasCandidatura WHERE id=? LIMIT 1
        """, (registro_id,))
        row = cursor.fetchone()

    if not row:
        return {"error": "Registro no encontrado."}, 404

    keys = ["id", "numeroCuenta", "nombre", "semestreIngreso", "semestrePresentado",
            "evaluacion", "fecha", "hora", "resultadoExamen",
            "presidente", "secretario", "vocal1", "vocal2", "vocal3"]
    return dict(zip(keys, row)), 200


@actas_candidatura_bp.route("/buscar_por_cuenta", methods=["POST"])
def buscar_por_cuenta():
    data = request.get_json(silent=True) or {}
    numeroCuenta = (data.get("numeroCuenta") or "").strip()

    if not numeroCuenta:
        return jsonify({"success": False, "error": "Ingresa el número de cuenta."})

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, numeroCuenta, nombre, fecha, evaluacion, resultadoExamen
            FROM actasCandidatura WHERE numeroCuenta = ? ORDER BY fecha DESC
        """, (numeroCuenta,))
        filas = cursor.fetchall()

    if not filas:
        return jsonify({"success": False, "error": "No se encontraron registros."})

    registros = [{"id": f[0], "numeroCuenta": f[1], "nombre": f[2],
                  "fecha": f[3], "evaluacion": f[4], "resultadoExamen": f[5]} for f in filas]
    return jsonify({"success": True, "registros": registros})


@actas_candidatura_bp.route("/actualizar", methods=["POST"])
def actualizar_acta():
    registro_id        = (request.form.get("id") or "").strip()
    numeroCuenta       = (request.form.get("numeroCuenta") or "").strip()
    nombre             = (request.form.get("nombre") or "").strip()
    semestreIngreso    = (request.form.get("semestreIngreso") or "").strip()
    semestrePresentado = (request.form.get("semestrePresentado") or "").strip()
    evaluacion         = (request.form.get("evaluacion") or "").strip().upper()
    fecha              = (request.form.get("fecha") or "").strip()
    hora               = (request.form.get("hora") or "").strip()
    resultadoExamen    = (request.form.get("resultadoExamen") or "").strip()
    presidente         = (request.form.get("presidente") or "").strip()
    secretario         = (request.form.get("secretario") or "").strip()
    vocal1             = (request.form.get("vocal1") or "").strip()
    vocal2             = (request.form.get("vocal2") or "").strip()
    vocal3             = (request.form.get("vocal3") or "").strip()

    required = [registro_id, numeroCuenta, nombre, semestreIngreso, semestrePresentado,
                evaluacion, fecha, hora, resultadoExamen]
    if any(not x for x in required):
        flash("Faltan campos obligatorios para actualizar.", "error")
        return redirect(url_for("actas_candidatura.index", open="modificar"))

    new_pdf_bytes = None
    f = request.files.get("actaPDF")
    if f and f.filename:
        new_pdf_bytes = f.read()
        if not new_pdf_bytes.startswith(b"%PDF"):
            flash("El archivo adjunto no es un PDF válido.", "error")
            return redirect(url_for("actas_candidatura.index", open="modificar"))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM actasCandidatura WHERE id=? LIMIT 1", (registro_id,))
        if not cursor.fetchone():
            flash("No se encontró el registro para actualizar.", "error")
            return redirect(url_for("actas_candidatura.index", open="modificar"))

        if new_pdf_bytes is None:
            cursor.execute("""
                UPDATE actasCandidatura
                SET numeroCuenta=?, nombre=?, semestreIngreso=?, semestrePresentado=?,
                    evaluacion=?, fecha=?, hora=?, resultadoExamen=?,
                    presidente=?, secretario=?, vocal1=?, vocal2=?, vocal3=?
                WHERE id=?
            """, (numeroCuenta, nombre, semestreIngreso, semestrePresentado,
                  evaluacion, fecha, hora, resultadoExamen,
                  presidente, secretario, vocal1, vocal2, vocal3, registro_id))
        else:
            cursor.execute("""
                UPDATE actasCandidatura
                SET numeroCuenta=?, nombre=?, semestreIngreso=?, semestrePresentado=?,
                    evaluacion=?, fecha=?, hora=?, resultadoExamen=?,
                    presidente=?, secretario=?, vocal1=?, vocal2=?, vocal3=?, actaPDF=?
                WHERE id=?
            """, (numeroCuenta, nombre, semestreIngreso, semestrePresentado,
                  evaluacion, fecha, hora, resultadoExamen,
                  presidente, secretario, vocal1, vocal2, vocal3,
                  bytes(new_pdf_bytes), registro_id))
        conn.commit()

    flash("Cambios guardados correctamente.", "success")
    return redirect(url_for("actas_candidatura.index"))


@actas_candidatura_bp.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
