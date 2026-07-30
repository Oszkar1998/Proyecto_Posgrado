from flask import Blueprint, render_template, request, url_for, send_file, abort, redirect, flash, jsonify
import io
from datetime import datetime
from auth import permission_required
from config import direccionBase, direccionImagen, direccionPDF
from db import get_connection

actas_grado_bp = Blueprint('actas_grado', __name__, template_folder='../templates')

#################################################################################################################################
@actas_grado_bp.route("/", methods=["GET", "POST"])
@permission_required("actas_grado")
def index():

    resultados = []
    mensaje = None

    if request.method == "POST":
        numDeCuenta = request.form.get("numDeCuenta", "").strip()
        folio = request.form.get("folio", "").strip()
        sinodal = request.form.get("sinodal", "").strip()
        fecha_inicio = request.form.get("fechaInicio", "").strip()
        fecha_fin = request.form.get("fechaFin", "").strip()
        nombreAlumno = request.form.get("nombreAlumno", "").strip()

        with get_connection() as conn:
            cursor = conn.cursor()

            if numDeCuenta and not folio and not sinodal:
                cursor.execute("SELECT folio, numCuenta, nombreCompleto FROM actasGrado WHERE numCuenta = ?", (numDeCuenta,))
                resultados = cursor.fetchall()
                if not resultados:
                    mensaje = "No se encontraron resultados para el número de cuenta proporcionado."

            elif folio and not numDeCuenta and not sinodal:
                cursor.execute("SELECT folio, numCuenta, nombreCompleto FROM actasGrado WHERE folio = ?", (folio,))
                resultados = cursor.fetchall()
                if not resultados:
                    mensaje = "No se encontraron resultados para el folio proporcionado."

            elif folio and numDeCuenta and not sinodal:
                cursor.execute("SELECT folio, numCuenta, nombreCompleto FROM actasGrado WHERE folio = ? AND numCuenta = ?", (folio, numDeCuenta))
                resultado = cursor.fetchone()
                if resultado:
                    pdf_url = url_for('actas_grado.ver_pdf', num_cuenta=resultado[1], folio=resultado[0])
                    return f"""
                        <script>
                            window.open('{pdf_url}', '_blank');
                            window.location.href = '{url_for('actas_grado.index')}';
                        </script>
                    """
                else:
                    mensaje = "No se encontró ninguna acta con ese folio y número de cuenta."

            if sinodal:
                nombre_buscar = sinodal.lower()
                rango_fechas_valido = False
                f_ini = f_fin = None
                if fecha_inicio and fecha_fin:
                    try:
                        f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                        rango_fechas_valido = True
                    except ValueError:
                        mensaje = "Formato de fecha no válido. Usa el calendario."

                cursor.execute("SELECT * FROM actasGrado")
                filas = cursor.fetchall()
                columnas = [d[0] for d in cursor.description]

                try:
                    i_folio = columnas.index("folio")
                    i_cuenta = columnas.index("numCuenta")
                    i_nombre = columnas.index("nombreCompleto")
                except ValueError:
                    return render_template("actasGrado.html", resultados=[], mensaje="Estructura de la base no esperada (faltan columnas básicas).")

                claves = ["sinodal", "presidente", "secretario", "vocal", "jurado", "asesor", "director", "tutor"]
                idx_jurado = [i for i, c in enumerate(columnas) if any(k in c.lower() for k in claves)]

                i_anio = columnas.index("anio") if "anio" in columnas else None
                i_mes  = columnas.index("mes")  if "mes"  in columnas else None
                i_dia  = columnas.index("dia")  if "dia"  in columnas else None

                for fila in filas:
                    if not idx_jurado:
                        continue
                    textos_jurado = [str(fila[i] or "").lower() for i in idx_jurado]
                    if any(nombre_buscar in t for t in textos_jurado):
                        if rango_fechas_valido and (i_anio is not None and i_mes is not None and i_dia is not None):
                            try:
                                f_acta = datetime(int(fila[i_anio]), int(fila[i_mes]), int(fila[i_dia]))
                                if not (f_ini <= f_acta <= f_fin):
                                    continue
                            except Exception:
                                continue
                        resultados.append((fila[i_folio], fila[i_cuenta], fila[i_nombre]))

                if not resultados and not mensaje:
                    mensaje = "No se encontraron actas con ese sinodal."

            if not sinodal and fecha_inicio and fecha_fin:
                try:
                    f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                    f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

                    cursor.execute("""
                        SELECT folio, numCuenta, nombreCompleto, anio, mes, dia
                        FROM actasGrado
                    """)
                    todas = cursor.fetchall()
                    for folio_x, cuenta_x, nombre_x, anio_x, mes_x, dia_x in todas:
                        try:
                            f_acta = datetime(int(anio_x), int(mes_x), int(dia_x))
                            if f_ini <= f_acta <= f_fin:
                                resultados.append((folio_x, cuenta_x, nombre_x))
                        except Exception:
                            continue

                    if not resultados:
                        mensaje = "No se encontraron resultados en el rango de fechas proporcionado."
                except ValueError:
                    mensaje = "Formato de fecha no válido. Usa el calendario."

            if nombreAlumno and not (folio and numDeCuenta):
                nombre_buscar = nombreAlumno.strip().upper()
                rango_fechas_valido = False
                f_ini = f_fin = None
                if fecha_inicio and fecha_fin:
                    try:
                        f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                        rango_fechas_valido = True
                    except ValueError:
                        mensaje = "Formato de fecha no válido. Usa el calendario."

                cursor.execute("SELECT folio, numCuenta, nombreCompleto, anio, mes, dia FROM actasGrado")
                filas = cursor.fetchall()

                for folio_x, cuenta_x, nombre_x, anio_x, mes_x, dia_x in filas:
                    if nombre_x and (nombre_buscar in nombre_x.upper()):
                        if rango_fechas_valido:
                            try:
                                f_acta = datetime(int(anio_x), int(mes_x), int(dia_x))
                                if not (f_ini <= f_acta <= f_fin):
                                    continue
                            except Exception:
                                continue
                        resultados.append((folio_x, cuenta_x, nombre_x))

                if not resultados and not mensaje:
                    mensaje = "No se encontraron actas con ese nombre."

    return render_template("actasGrado.html", resultados=resultados, mensaje=mensaje)

@actas_grado_bp.route("/ver_pdf/<num_cuenta>/<folio>")
def ver_pdf(num_cuenta, folio):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT actaPDF FROM actasGrado WHERE numCuenta=? AND folio=?", (num_cuenta, folio))
        archivo = cursor.fetchone()

    if archivo and archivo[0]:
        return send_file(io.BytesIO(archivo[0]), mimetype='application/pdf')
    else:
        return abort(404)

@actas_grado_bp.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@actas_grado_bp.route("/guardar", methods=["POST"])
def guardar_acta():
    folio = (request.form.get("folio") or "").strip()
    numCuenta = (request.form.get("numCuenta") or "").strip()
    nombreCompleto = (request.form.get("nombreCompleto") or "").strip()
    grado = (request.form.get("grado") or "").strip()
    semestreIngreso = (request.form.get("semestreIngreso") or "").strip()
    semestreEgreso = (request.form.get("semestreEgreso") or "").strip()
    promedio = (request.form.get("promedio") or "").strip()
    planEstudios = (request.form.get("planEstudios") or "").strip()
    dia = (request.form.get("dia") or "").strip()
    mes = (request.form.get("mes") or "").strip()
    anio = (request.form.get("anio") or "").strip()
    nacionalidad = (request.form.get("nacionalidad") or "").strip()
    resultado = (request.form.get("resultado") or "").strip()
    presidente = (request.form.get("presidente") or "").strip()
    secretario = (request.form.get("secretario") or "").strip()
    vocal1 = (request.form.get("vocal1") or "").strip()
    vocal2 = (request.form.get("vocal2") or "").strip()
    vocal3 = (request.form.get("vocal3") or "").strip()
    sexo = (request.form.get("sexo") or "").strip()

    required = [folio, numCuenta, nombreCompleto, grado, semestreIngreso, semestreEgreso,
                dia, mes, anio, resultado, presidente, secretario, vocal1, sexo]
    if any(not x for x in required):
        return render_template("actasGrado.html", resultados=[], mensaje="Faltan campos obligatorios (*) para guardar.")

    f = request.files.get("actaPDF")
    if not f or f.filename == "":
        return render_template("actasGrado.html", resultados=[], mensaje="Debes adjuntar el PDF del acta.")
    pdf_bytes = f.read()

    if not pdf_bytes.startswith(b"%PDF"):
        return render_template("actasGrado.html", resultados=[], mensaje="El archivo adjunto no parece ser un PDF válido.")

    if len(pdf_bytes) > 15 * 1024 * 1024:
        return render_template("actasGrado.html", resultados=[], mensaje="El PDF excede 15MB. Comprime o reduce el archivo.")

    try:
        numCuenta_int = int(numCuenta)
        dia_int = int(dia); mes_int = int(mes); anio_int = int(anio)
    except ValueError:
        return render_template("actasGrado.html", resultados=[], mensaje="NumCuenta/Día/Mes/Año deben ser numéricos.")

    prom_val = None
    if promedio != "":
        try:
            prom_val = float(promedio)
        except ValueError:
            return render_template("actasGrado.html", resultados=[], mensaje="Promedio debe ser numérico (ej: 9.3).")

    plan_val = None
    if planEstudios != "":
        try:
            plan_val = float(planEstudios)
        except ValueError:
            return render_template("actasGrado.html", resultados=[], mensaje="Plan de estudios debe ser numérico (según tu BD).")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM actasGrado WHERE numCuenta=? AND folio=? LIMIT 1", (numCuenta_int, folio))
        if cursor.fetchone():
            return render_template("actasGrado.html", resultados=[], mensaje="Ya existe un registro con ese Folio y Número de Cuenta (duplicado).")

        cursor.execute("""
            SELECT 1 FROM actasGrado
            WHERE nombreCompleto=? AND anio=? AND mes=? AND dia=? AND presidente=? AND secretario=? AND vocal1=? LIMIT 1
        """, (nombreCompleto, anio_int, mes_int, dia_int, presidente, secretario, vocal1))
        if cursor.fetchone():
            return render_template("actasGrado.html", resultados=[], mensaje="Parece duplicado: ya existe un acta con mismo alumno/fecha/jurado.")

        cursor.execute("""
            INSERT INTO actasGrado (
              folio, numCuenta, nombreCompleto, grado, semestreIngreso, semestreEgreso,
              promedio, planEstudios, dia, mes, anio, nacionalidad, resultado,
              presidente, secretario, vocal1, vocal2, vocal3, sexo, actaPDF
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folio, numCuenta_int, nombreCompleto, grado, semestreIngreso, semestreEgreso,
            prom_val, plan_val, dia_int, mes_int, anio_int, nacionalidad, resultado,
            presidente, secretario, vocal1, vocal2, vocal3, sexo, bytes(pdf_bytes)
        ))
        conn.commit()

    flash("✅ Se guardaron correctamente los datos del acta.", "success")
    return redirect(url_for("actas_grado.index"))

@actas_grado_bp.route("/get_acta", methods=["POST"])
def get_acta_json():
    data = request.get_json(silent=True) or {}
    numCuenta = (data.get("numCuenta") or "").strip()
    folio = (data.get("folio") or "").strip()

    if not numCuenta or not folio:
        return {"error": "Faltan numCuenta y folio."}, 400

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT folio, numCuenta, nombreCompleto, grado, semestreIngreso, semestreEgreso,
                   promedio, planEstudios, dia, mes, anio, nacionalidad, resultado,
                   presidente, secretario, vocal1, vocal2, vocal3, sexo
            FROM actasGrado
            WHERE numCuenta=? AND folio=?
            LIMIT 1
        """, (numCuenta, folio))
        row = cursor.fetchone()

    if not row:
        return {"error": "Acta no encontrada."}, 404

    keys = ["folio","numCuenta","nombreCompleto","grado","semestreIngreso","semestreEgreso",
            "promedio","planEstudios","dia","mes","anio","nacionalidad","resultado",
            "presidente","secretario","vocal1","vocal2","vocal3","sexo"]
    return dict(zip(keys, row)), 200

@actas_grado_bp.route("/actualizar", methods=["POST"])
def actualizar_acta():
    old_num = (request.form.get("old_numCuenta") or "").strip()
    old_fol = (request.form.get("old_folio") or "").strip()

    folio = (request.form.get("folio") or "").strip()
    numCuenta = (request.form.get("numCuenta") or "").strip()
    nombreCompleto = (request.form.get("nombreCompleto") or "").strip()
    grado = (request.form.get("grado") or "").strip()
    semestreIngreso = (request.form.get("semestreIngreso") or "").strip()
    semestreEgreso = (request.form.get("semestreEgreso") or "").strip()
    promedio = (request.form.get("promedio") or "").strip()
    planEstudios = (request.form.get("planEstudios") or "").strip()
    dia = (request.form.get("dia") or "").strip()
    mes = (request.form.get("mes") or "").strip()
    anio = (request.form.get("anio") or "").strip()
    nacionalidad = (request.form.get("nacionalidad") or "").strip()
    resultado = (request.form.get("resultado") or "").strip()
    presidente = (request.form.get("presidente") or "").strip()
    secretario = (request.form.get("secretario") or "").strip()
    vocal1 = (request.form.get("vocal1") or "").strip()
    vocal2 = (request.form.get("vocal2") or "").strip()
    vocal3 = (request.form.get("vocal3") or "").strip()
    sexo = (request.form.get("sexo") or "").strip()

    required = [old_num, old_fol, folio, numCuenta, nombreCompleto, grado, semestreIngreso, semestreEgreso,
                dia, mes, anio, resultado, presidente, secretario, vocal1, sexo]
    if any(not x for x in required):
        flash("❌ Faltan campos obligatorios para actualizar.", "error")
        return redirect(url_for("actas_grado.index", open="modificar"))

    try:
        numCuenta_int = int(numCuenta)
        old_num_int = int(old_num)
        dia_int = int(dia); mes_int = int(mes); anio_int = int(anio)
    except ValueError:
        flash("❌ NumCuenta/Día/Mes/Año deben ser numéricos.", "error")
        return redirect(url_for("actas_grado.index", open="modificar"))

    prom_val = None
    if promedio != "":
        try: prom_val = float(promedio)
        except ValueError:
            flash("❌ Promedio inválido.", "error")
            return redirect(url_for("actas_grado.index", open="modificar"))

    plan_val = None
    if planEstudios != "":
        try: plan_val = float(planEstudios)
        except ValueError:
            flash("❌ Plan de estudios inválido.", "error")
            return redirect(url_for("actas_grado.index", open="modificar"))

    new_pdf_bytes = None
    f = request.files.get("actaPDF")
    if f and f.filename:
        new_pdf_bytes = f.read()
        if not new_pdf_bytes.startswith(b"%PDF"):
            flash("❌ El archivo adjunto no es PDF válido.", "error")
            return redirect(url_for("actas_grado.index", open="modificar"))

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM actasGrado WHERE numCuenta=? AND folio=? LIMIT 1", (old_num_int, old_fol))
        if not cursor.fetchone():
            flash("❌ No se encontró el registro original para actualizar.", "error")
            return redirect(url_for("actas_grado.index", open="modificar"))

        if (old_num_int != numCuenta_int) or (old_fol != folio):
            cursor.execute("SELECT 1 FROM actasGrado WHERE numCuenta=? AND folio=? LIMIT 1", (numCuenta_int, folio))
            if cursor.fetchone():
                flash("❌ Ya existe otro registro con ese Folio y Número de Cuenta.", "error")
                return redirect(url_for("actas_grado.index", open="modificar"))

        if new_pdf_bytes is None:
            cursor.execute("""
                UPDATE actasGrado
                SET folio=?, numCuenta=?, nombreCompleto=?, grado=?, semestreIngreso=?, semestreEgreso=?,
                    promedio=?, planEstudios=?, dia=?, mes=?, anio=?, nacionalidad=?, resultado=?,
                    presidente=?, secretario=?, vocal1=?, vocal2=?, vocal3=?, sexo=?
                WHERE numCuenta=? AND folio=?
            """, (
                folio, numCuenta_int, nombreCompleto, grado, semestreIngreso, semestreEgreso,
                prom_val, plan_val, dia_int, mes_int, anio_int, nacionalidad, resultado,
                presidente, secretario, vocal1, vocal2, vocal3, sexo,
                old_num_int, old_fol
            ))
        else:
            cursor.execute("""
                UPDATE actasGrado
                SET folio=?, numCuenta=?, nombreCompleto=?, grado=?, semestreIngreso=?, semestreEgreso=?,
                    promedio=?, planEstudios=?, dia=?, mes=?, anio=?, nacionalidad=?, resultado=?,
                    presidente=?, secretario=?, vocal1=?, vocal2=?, vocal3=?, sexo=?, actaPDF=?
                WHERE numCuenta=? AND folio=?
            """, (
                folio, numCuenta_int, nombreCompleto, grado, semestreIngreso, semestreEgreso,
                prom_val, plan_val, dia_int, mes_int, anio_int, nacionalidad, resultado,
                presidente, secretario, vocal1, vocal2, vocal3, sexo, bytes(new_pdf_bytes),
                old_num_int, old_fol
            ))
        conn.commit()

    flash("✅ Cambios guardados correctamente.", "success")
    return redirect(url_for("actas_grado.index"))

@actas_grado_bp.route("/guardar_fecha_extra", methods=["POST"])
def guardar_fecha_extra():
    numCuenta = (request.form.get("numCuenta") or "").strip()
    folio = (request.form.get("folio") or "").strip()
    fecha = (request.form.get("fecha") or "").strip()
    campo = (request.form.get("campo") or "").strip()

    if not numCuenta or not folio or not fecha or not campo:
        flash("❌ Debes ingresar número de cuenta, folio y fecha.", "error")
        return redirect(url_for("actas_grado.index"))

    if campo not in ["pagoSinodales", "dgaeEntregaCarpeta"]:
        flash("❌ Campo no válido.", "error")
        return redirect(url_for("actas_grado.index"))

    try:
        numCuenta_int = int(numCuenta)
    except ValueError:
        flash("❌ El número de cuenta debe ser numérico.", "error")
        return redirect(url_for("actas_grado.index", open=campo))

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT nombreCompleto FROM actasGrado
            WHERE numCuenta = ? AND folio = ? LIMIT 1
        """, (numCuenta_int, folio))
        acta = cursor.fetchone()

        if not acta:
            flash("❌ No se encontró ningún registro con ese número de cuenta y folio.", "error")
            return redirect(url_for("actas_grado.index", open=campo))

        if campo == "pagoSinodales":
            cursor.execute("""
                UPDATE actasGrado SET pagoSinodales = ?
                WHERE numCuenta = ? AND folio = ?
            """, (fecha, numCuenta_int, folio))
            mensaje = "✅ Fecha de pago de sinodales guardada correctamente."
        else:
            cursor.execute("""
                UPDATE actasGrado SET dgaeEntregaCarpeta = ?
                WHERE numCuenta = ? AND folio = ?
            """, (fecha, numCuenta_int, folio))
            mensaje = "✅ Fecha de entrega de carpeta DGAE guardada correctamente."

        conn.commit()

    flash(mensaje, "success")
    return redirect(url_for("actas_grado.index"))

@actas_grado_bp.route("/buscar_pago_sinodales", methods=["POST"])
def buscar_pago_sinodales():
    data = request.get_json(silent=True) or {}

    sinodal = (data.get("sinodal") or "").strip().lower()
    fecha_inicio = (data.get("fechaInicio") or "").strip()
    fecha_fin = (data.get("fechaFin") or "").strip()

    if not sinodal:
        return jsonify({"ok": False, "error": "Ingresa el nombre del sinodal."}), 400

    f_ini = f_fin = None
    if fecha_inicio and fecha_fin:
        try:
            f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            return jsonify({"ok": False, "error": "Formato de fecha inválido."}), 400

    with get_connection() as conn:
        conn.row_factory = __import__('sqlite3').Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT folio, numCuenta, nombreCompleto, dia, mes, anio,
                   presidente, secretario, vocal1, vocal2, vocal3,
                   pagoSinodales, dgaeEntregaCarpeta
            FROM actasGrado
        """)
        filas = cursor.fetchall()

    resultados = []
    for fila in filas:
        jurado = [fila["presidente"], fila["secretario"], fila["vocal1"], fila["vocal2"], fila["vocal3"]]
        coincide_sinodal = any(sinodal in str(nombre or "").lower() for nombre in jurado)

        if not coincide_sinodal:
            continue

        if f_ini and f_fin:
            try:
                fecha_acta = datetime(int(fila["anio"]), int(fila["mes"]), int(fila["dia"]))
                if not (f_ini <= fecha_acta <= f_fin):
                    continue
            except Exception:
                continue

        if not fila["pagoSinodales"]:
            continue

        resultados.append({
            "folio": fila["folio"],
            "numCuenta": fila["numCuenta"],
            "nombreCompleto": fila["nombreCompleto"],
            "fechaActa": f'{fila["dia"]}/{fila["mes"]}/{fila["anio"]}',
            "pagoSinodales": fila["pagoSinodales"],
            "dgaeEntregaCarpeta": fila["dgaeEntregaCarpeta"],
        })

    return jsonify({"ok": True, "resultados": resultados})
