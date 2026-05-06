import sqlite3
from flask import Blueprint, render_template, request, url_for, send_file, abort, redirect, flash
import io
from datetime import datetime
from auth import permission_required

actas_grado_bp = Blueprint('actas_grado', __name__, template_folder='../templates')

direccionBase = "static/BaseDeDatos/basePosgrado.db"  


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

        conn = sqlite3.connect(direccionBase)
        cursor = conn.cursor()

        # 1) Casos directos por cuenta/folio (igual que antes)
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
                conn.close()
                pdf_url = url_for('actas_grado.ver_pdf', num_cuenta=resultado[1], folio=resultado[0])
                return f"""
                    <script>
                        window.open('{pdf_url}', '_blank');
                        window.location.href = '{url_for('actas_grado.index')}';
                    </script>
                """
            else:
                mensaje = "No se encontró ninguna acta con ese folio y número de cuenta."
        
        # 2) Búsqueda por SINODAL (opcionalmente combinada con fechas)
        if sinodal:
            nombre_buscar = sinodal.lower()

            # Convertir fechas si vienen
            rango_fechas_valido = False
            f_ini = f_fin = None
            if fecha_inicio and fecha_fin:
                try:
                    f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                    f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                    rango_fechas_valido = True
                except ValueError:
                    mensaje = "Formato de fecha no válido. Usa el calendario."

            # Traer toda la tabla y filtrar en Python (uno por uno)
            cursor.execute("SELECT * FROM actasGrado")
            filas = cursor.fetchall()
            columnas = [d[0] for d in cursor.description]

            # Índices de columnas clave
            try:
                i_folio = columnas.index("folio")
                i_cuenta = columnas.index("numCuenta")
                i_nombre = columnas.index("nombreCompleto")
            except ValueError:
                conn.close()
                return render_template("actasGrado.html", resultados=[], mensaje="Estructura de la base no esperada (faltan columnas básicas).")

            # Posibles columnas de jurado/sinodales (si no existen, la lista queda vacía)
            claves = ["sinodal", "presidente", "secretario", "vocal", "jurado", "asesor", "director", "tutor"]
            idx_jurado = [i for i, c in enumerate(columnas) if any(k in c.lower() for k in claves)]

            # También índices de fecha, por si se combinan
            i_anio = columnas.index("anio") if "anio" in columnas else None
            i_mes  = columnas.index("mes")  if "mes"  in columnas else None
            i_dia  = columnas.index("dia")  if "dia"  in columnas else None

            for fila in filas:
                # Si no hay columnas de jurado, no hay de dónde buscar nombres
                if not idx_jurado:
                    continue

                textos_jurado = [str(fila[i] or "").lower() for i in idx_jurado]
                if any(nombre_buscar in t for t in textos_jurado):
                    # Filtro por fechas si corresponde
                    if rango_fechas_valido and (i_anio is not None and i_mes is not None and i_dia is not None):
                        try:
                            f_acta = datetime(int(fila[i_anio]), int(fila[i_mes]), int(fila[i_dia]))
                            if not (f_ini <= f_acta <= f_fin):
                                continue
                        except Exception:
                            # Si la fecha está mal cargada, la saltamos cuando se pidió rango
                            continue
                    resultados.append((fila[i_folio], fila[i_cuenta], fila[i_nombre]))

            if not resultados and not mensaje:
                mensaje = "No se encontraron actas con ese sinodal."

        # 3) Búsqueda por rango de fechas (cuando NO se usa sinodal arriba)
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

            # Si quieres permitir fechas aquí también:
            rango_fechas_valido = False
            f_ini = f_fin = None
            if fecha_inicio and fecha_fin:
                try:
                    f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                    f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                    rango_fechas_valido = True
                except ValueError:
                    mensaje = "Formato de fecha no válido. Usa el calendario."

            # Igual que sinodal: traes todo y filtras en Python
            cursor.execute("SELECT folio, numCuenta, nombreCompleto, anio, mes, dia FROM actasGrado")
            filas = cursor.fetchall()

            for folio_x, cuenta_x, nombre_x, anio_x, mes_x, dia_x in filas:
                if nombre_x and (nombre_buscar in nombre_x.upper()):

                    # si hay rango de fechas, filtramos
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


        conn.close()

    return render_template("actasGrado.html", resultados=resultados, mensaje=mensaje)

@actas_grado_bp.route("/ver_pdf/<num_cuenta>/<folio>")
def ver_pdf(num_cuenta, folio): 
    conn = sqlite3.connect(direccionBase)
    cursor = conn.cursor()
    cursor.execute("SELECT actaPDF FROM actasGrado WHERE numCuenta=? AND folio=?", (num_cuenta, folio))
    archivo = cursor.fetchone()
    conn.close()

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

    # 1) Leer campos
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

    # 2) Validación mínima
    required = [folio, numCuenta, nombreCompleto, grado, semestreIngreso, semestreEgreso,
                dia, mes, anio, resultado, presidente, secretario, vocal1, sexo]
    if any(not x for x in required):
        return render_template("actasGrado.html", resultados=[], mensaje="Faltan campos obligatorios (*) para guardar.")

    # 3) PDF
    f = request.files.get("actaPDF")
    if not f or f.filename == "":
        return render_template("actasGrado.html", resultados=[], mensaje="Debes adjuntar el PDF del acta.")
    pdf_bytes = f.read()

    # Validar firma PDF (rápido)
    if not pdf_bytes.startswith(b"%PDF"):
        return render_template("actasGrado.html", resultados=[], mensaje="El archivo adjunto no parece ser un PDF válido.")

    # Límite de tamaño (ej: 15 MB)
    if len(pdf_bytes) > 15 * 1024 * 1024:
        return render_template("actasGrado.html", resultados=[], mensaje="El PDF excede 15MB. Comprime o reduce el archivo.")

    # 4) Cast de números
    try:
        numCuenta_int = int(numCuenta)
        dia_int = int(dia); mes_int = int(mes); anio_int = int(anio)
    except ValueError:
        return render_template("actasGrado.html", resultados=[], mensaje="NumCuenta/Día/Mes/Año deben ser numéricos.")

    # promedio y planEstudios son opcionales
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
            # si lo quieres permitir como texto, dime y lo cambiamos
            return render_template("actasGrado.html", resultados=[], mensaje="Plan de estudios debe ser numérico (según tu BD).")

    # 5) Anti-duplicados (lo más importante)
    conn = sqlite3.connect(direccionBase)
    cursor = conn.cursor()

    # A) Duplicado por llave lógica: (numCuenta, folio)
    cursor.execute("SELECT 1 FROM actasGrado WHERE numCuenta=? AND folio=? LIMIT 1", (numCuenta_int, folio))
    if cursor.fetchone():
        conn.close()
        return render_template("actasGrado.html", resultados=[], mensaje="Ya existe un registro con ese Folio y Número de Cuenta (duplicado).")

    # B) (Opcional) Duplicado “full” por coincidencia fuerte (sin comparar PDF)
    # Esto evita repetidos aunque cambien folio por error, ajustable si quieres.
    cursor.execute("""
        SELECT 1 FROM actasGrado
        WHERE nombreCompleto=? AND anio=? AND mes=? AND dia=? AND presidente=? AND secretario=? AND vocal1=? LIMIT 1
    """, (nombreCompleto, anio_int, mes_int, dia_int, presidente, secretario, vocal1))
    if cursor.fetchone():
        conn.close()
        return render_template("actasGrado.html", resultados=[], mensaje="Parece duplicado: ya existe un acta con mismo alumno/fecha/jurado (validar antes de guardar).")

    # 6) INSERT
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
        presidente, secretario, vocal1, vocal2, vocal3, sexo, sqlite3.Binary(pdf_bytes)
    ))

    conn.commit()
    conn.close()

    flash("✅ Se guardaron correctamente los datos del acta.", "success")
    return redirect(url_for("actas_grado.index"))

@actas_grado_bp.route("/get_acta", methods=["POST"])
def get_acta_json():
    data = request.get_json(silent=True) or {}
    numCuenta = (data.get("numCuenta") or "").strip()
    folio = (data.get("folio") or "").strip()

    if not numCuenta or not folio:
        return {"error": "Faltan numCuenta y folio."}, 400

    conn = sqlite3.connect(direccionBase)
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
    conn.close()

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

    # Validación básica
    required = [old_num, old_fol, folio, numCuenta, nombreCompleto, grado, semestreIngreso, semestreEgreso,
                dia, mes, anio, resultado, presidente, secretario, vocal1, sexo]
    if any(not x for x in required):
        flash("❌ Faltan campos obligatorios para actualizar.", "error")
        return redirect(url_for("actas_grado.index", open="modificar"))

    # Cast
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

    # PDF opcional
    new_pdf_bytes = None
    f = request.files.get("actaPDF")
    if f and f.filename:
        new_pdf_bytes = f.read()
        if not new_pdf_bytes.startswith(b"%PDF"):
            flash("❌ El archivo adjunto no es PDF válido.", "error")
            return redirect(url_for("actas_grado.index", open="modificar"))

    conn = sqlite3.connect(direccionBase)
    cursor = conn.cursor()

    # Verificar que el registro original exista
    cursor.execute("SELECT 1 FROM actasGrado WHERE numCuenta=? AND folio=? LIMIT 1", (old_num_int, old_fol))
    if not cursor.fetchone():
        conn.close()
        flash("❌ No se encontró el registro original para actualizar.", "error")
        return redirect(url_for("actas_grado.index", open="modificar"))

    # Anti-duplicado si cambiaron llave (numCuenta, folio)
    if (old_num_int != numCuenta_int) or (old_fol != folio):
        cursor.execute("SELECT 1 FROM actasGrado WHERE numCuenta=? AND folio=? LIMIT 1", (numCuenta_int, folio))
        if cursor.fetchone():
            conn.close()
            flash("❌ Ya existe otro registro con ese Folio y Número de Cuenta.", "error")
            return redirect(url_for("actas_grado.index", open="modificar"))

    # UPDATE (con/sin PDF)
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
            presidente, secretario, vocal1, vocal2, vocal3, sexo, sqlite3.Binary(new_pdf_bytes),
            old_num_int, old_fol
        ))

    conn.commit()
    conn.close()

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

    conn = sqlite3.connect(direccionBase)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombreCompleto
        FROM actasGrado
        WHERE numCuenta = ? AND folio = ?
        LIMIT 1
    """, (numCuenta_int, folio))

    acta = cursor.fetchone()

    if not acta:
        conn.close()
        flash("❌ No se encontró ningún registro con ese número de cuenta y folio.", "error")
        return redirect(url_for("actas_grado.index", open=campo))

    if campo == "pagoSinodales":
        cursor.execute("""
            UPDATE actasGrado
            SET pagoSinodales = ?
            WHERE numCuenta = ? AND folio = ?
        """, (fecha, numCuenta_int, folio))
        mensaje = "✅ Fecha de pago de sinodales guardada correctamente."

    else:
        cursor.execute("""
            UPDATE actasGrado
            SET dgaeEntregaCarpeta = ?
            WHERE numCuenta = ? AND folio = ?
        """, (fecha, numCuenta_int, folio))
        mensaje = "✅ Fecha de entrega de carpeta DGAE guardada correctamente."

    conn.commit()
    conn.close()

    flash(mensaje, "success")
    return redirect(url_for("actas_grado.index"))