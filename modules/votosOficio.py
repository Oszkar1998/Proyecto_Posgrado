from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory, session, send_file
import uuid
import os
import glob
import time
from fpdf import FPDF
from io import BytesIO
from auth import permission_required
from config import direccionBase, direccionImagen, direccionPDF
from db import get_connection

votos_Oficio_PUEI_bp = Blueprint('votosOficio', __name__, template_folder='../templates')

# --------------------------- UTILIDADES ---------------------------
def _etiqueta_genero(s):
    return {"M": "el alumno", "F": "la alumna", "X": "elle alumne"}.get(s or "", "el alumno")

def _validar_rango_plan(plan_int: int) -> bool:
    return 3000 <= plan_int <= 5999

def _limpiar_votos_antiguos():
    """Elimina PDFs de votos con más de 10 minutos de antigüedad."""
    patron = direccionPDF + "Votos_*.pdf"
    ahora = time.time()
    for archivo in glob.glob(patron):
        if ahora - os.path.getmtime(archivo) > 600:
            try:
                os.remove(archivo)
            except Exception:
                pass

# --------------------------- PDF ---------------------------
def programaEspecializacion(pdf, nombreCompleto, planEstudios, especializacion, trabajo, persona, genero):
    pdf.set_left_margin(25)
    pdf.set_right_margin(25)
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    pdf.set_font("Times", size=12)

    pdf.image(direccionImagen + "Logo_Unam.jpeg", x=15, y=15, w=35)

    pdf.set_xy(70, 25)
    pdf.set_font("Times", "B", 12)
    pdf.cell(110, 6, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", ln=True, align="C")
    pdf.set_xy(70, 35)
    pdf.cell(110, 6, "PROGRAMA ÚNICO DE ESPECIALIZACIONES DE INGENIERÍA", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Times", size=12)
    pdf.ln(20)
    pdf.multi_cell(0, 6,
        "DRA. AIDA HUERTA BARRIENTOS\n"
        "Coordinadora del Programa\n"
        "Presente", align="J")

    pdf.ln(20)
    pdf.multi_cell(0, 6,
        f"Por este medio comunico a usted que he leído la tesina titulada: "
        f"\"{trabajo}\" "
        f"para obtener el grado de ESPECIALISTA EN {especializacion} plan 11-{planEstudios}, que presenta {genero} "
        f"{nombreCompleto}.", align="J")

    pdf.ln(4)
    pdf.multi_cell(0, 6,
        "Considero que la mencionada tesina ______ es satisfactoria por lo que ______ la apruebo sin otorgarle créditos académicos.", align="J")

    pdf.ln(4)
    pdf.multi_cell(0, 6,
        "Quedo enterado de que formaré parte del jurado en la fecha y hora que se me comunicará posteriormente.", align="J")

    pdf.ln(15)
    pdf.multi_cell(0, 6, "Atentamente,", align="L")

    pdf.ln(35)
    pdf.set_x(25)
    pdf.multi_cell(0, 6, persona, align="L")

    pdf.set_y(-40)
    pdf.set_font("Times", "B", 12)
    pdf.set_x(120)
    pdf.cell(20, 6, "Fecha: _____________________", align="L")

def _pdf_response(pdf, filename):
    data = pdf.output(dest='S')
    if isinstance(data, str):
        data = data.encode('latin-1')
    return send_file(BytesIO(data), mimetype="application/pdf", as_attachment=False, download_name=filename)

# --------------------------- RUTAS ---------------------------
@votos_Oficio_PUEI_bp.route("/", methods=["GET", "POST"])
@permission_required("votos_puei")
def index():
    if request.method == "POST":
        numDeCuenta = request.form["numeroDeCuenta"].strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                    tituloTesina, tutor, presidente, secretario, vocal1, vocal2, vocal3, sexo, modalidad, sexoTutor
                FROM posgrado
                WHERE numeroCuenta = ?
                ORDER BY planEstudios
            """, (numDeCuenta,))
            filas = cursor.fetchall()

        if not filas:
            return jsonify({"success": False, "error": "No existe esa cuenta en la base."})

        if len(filas) > 1:
            opciones = []
            for (id_, _, nombre, plan, espec, *_resto) in filas:
                opciones.append({
                    "id": id_,
                    "planEstudios": int(plan),
                    "especializacion": espec or "",
                    "nombreCompleto": nombre
                })
            return jsonify({"success": True, "multiples": opciones})

        # Un solo registro → generar con nombre único para evitar sobreescritura
        (id_, numeroCuenta, nombre, plan, espec, trabajo, tutor, presidente, secretario,
        v1, v2, v3, sexo, modalidad, sexoTutor) = filas[0]

        genero = _etiqueta_genero(sexo)
        trabajo = (trabajo or "").replace("Δ", "Delta")

        pdf_votos = FPDF()
        for persona in [presidente, secretario, v1, v2, v3]:
            programaEspecializacion(pdf_votos, nombre, plan, espec, trabajo, persona, genero)

        # Nombre único por sesión para evitar sobreescritura entre usuarios simultáneos
        votos_filename = f"Votos_{uuid.uuid4().hex[:8]}.pdf"
        pdf_votos.output(direccionPDF + votos_filename, "F")

        # Limpiar PDFs antiguos (más de 10 minutos)
        _limpiar_votos_antiguos()

        return jsonify({
            "success": True,
            "votos_url": f"/votosOficio/ver_pdf/{votos_filename}",
            "nombre": nombre,
            "especializacion": espec or "",
            "modalidad": modalidad or ""
        })

    return render_template("votosOficio.html")

@votos_Oficio_PUEI_bp.route("/guardar_datos", methods=["POST"])
def guardar_datos():
    data = request.get_json()

    numero_cuenta = (data["numeroDeCuenta"] or "").strip()
    nombre = (data.get("nombreCompleto") or "").strip()
    plan = int(data["planEstudios"])
    especializacion = (data.get("especializacion") or "").strip()
    titulo = (data.get("tituloOtesina") or "").strip()
    tutor = (data.get("tutor") or "").strip()
    sexoTutor = (data.get("sexoTutor") or "").strip()
    presidente = (data.get("presidente") or "").strip()
    secretario = (data.get("secretario") or "").strip()
    vocal1 = (data.get("vocal1") or "").strip()
    vocal2 = (data.get("vocal2") or "").strip()
    vocal3 = (data.get("vocal3") or "").strip()
    sexo = (data.get("sexo") or "").strip()
    modalidad = (data.get("modalidad") or "").strip()

    if not _validar_rango_plan(plan):
        return jsonify({"success": False, "error": "El plan de estudios debe estar entre 3000 y 5999."})

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM posgrado
            WHERE numeroCuenta=? AND planEstudios=? LIMIT 1
        """, (numero_cuenta, plan))
        if cur.fetchone():
            return jsonify({"success": False, "error": "Ya existe ese número de cuenta en ese plan de estudios."})

        cur.execute("""
            INSERT INTO posgrado (
                numeroCuenta, nombreCompleto, planEstudios, especializacion, tituloTesina,
                tutor, presidente, secretario, vocal1, vocal2, vocal3, sexo, modalidad, sexoTutor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (numero_cuenta, nombre, plan, especializacion, titulo,
            tutor, presidente, secretario, vocal1, vocal2, vocal3, sexo, modalidad, sexoTutor))
        conn.commit()
    
    return jsonify({"success": True})

# --------- BÚSQUEDAS ---------
@votos_Oficio_PUEI_bp.route("/buscar_cuenta", methods=["POST"])
def buscar_por_cuenta():
    data = request.get_json()
    cuenta = data.get("numeroCuenta")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, numeroCuenta, nombreCompleto, especializacion, modalidad
            FROM posgrado WHERE numeroCuenta = ? ORDER BY planEstudios
        """, (cuenta,))
        resultados = cursor.fetchall()

    respuesta = [{"id": r[0], "numeroCuenta": r[1], "nombreCompleto": r[2],
                  "especializacion": r[3], "modalidad": r[4]} for r in resultados]
    return jsonify(respuesta)

@votos_Oficio_PUEI_bp.route('/buscar_nombre', methods=['POST'])
def buscar_nombre():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, numeroCuenta, nombreCompleto, especializacion, modalidad
            FROM posgrado WHERE nombreCompleto LIKE ? ORDER BY planEstudios
        """, ('%' + nombre + '%',))
        resultados = cursor.fetchall()

    respuesta = [{"id": r[0], "numeroCuenta": r[1], "nombreCompleto": r[2],
                  "especializacion": r[3], "modalidad": r[4]} for r in resultados]
    return jsonify(respuesta)

# --------- GENERAR VOTOS POR ID ---------
@votos_Oficio_PUEI_bp.route("/votos_id/<int:id>")
def generar_votos_por_id(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombreCompleto, planEstudios, especializacion, tituloTesina,
                presidente, secretario, vocal1, vocal2, vocal3, sexo
            FROM posgrado WHERE id = ?
        """, (id,))
        datos = cursor.fetchone()

    if not datos:
        return "Alumno no encontrado", 404

    nombre, plan, espec, trabajo, pres, sec, v1, v2, v3, sexo = datos
    genero = _etiqueta_genero(sexo)
    trabajo = (trabajo or "").replace("Δ", "Delta")

    pdf = FPDF()
    for persona in [pres, sec, v1, v2, v3]:
        programaEspecializacion(pdf, nombre, plan, espec, trabajo, persona, genero)

    return _pdf_response(pdf, "Votos.pdf")

# --------- AUTOCOMPLETE SINODALES ---------
@votos_Oficio_PUEI_bp.route("/sinodales", methods=["GET"])
def sinodales_autocomplete():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])

    pat_contains = f"%{q}%"
    pat_prefix   = f"{q}%"

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT nombre_completo FROM sinodales
            WHERE nombre_completo LIKE ? COLLATE NOCASE
            ORDER BY
            CASE WHEN nombre_completo LIKE ? COLLATE NOCASE THEN 0 ELSE 1 END,
            nombre_completo
            LIMIT 20
        """, (pat_contains, pat_prefix))
        rows = [r[0] for r in cur.fetchall()]

    return jsonify(rows)

# --------- MODIFICAR ---------
@votos_Oficio_PUEI_bp.route("/obtener_datos", methods=["POST"])
def obtener_datos():
    datos = request.get_json()
    cuenta = (datos.get("numeroCuenta") or "").strip()
    seleccion_id = datos.get("id")

    with get_connection() as conn:
        cursor = conn.cursor()
        if seleccion_id:
            cursor.execute("""
                SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion, tituloTesina, tutor, presidente,
                    secretario, vocal1, vocal2, vocal3, sexo, modalidad, sexoTutor
                FROM posgrado WHERE id = ? LIMIT 1
            """, (seleccion_id,))
        else:
            cursor.execute("""
                SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion, tituloTesina, tutor, presidente,
                    secretario, vocal1, vocal2, vocal3, sexo, modalidad, sexoTutor
                FROM posgrado WHERE numeroCuenta = ? ORDER BY planEstudios
            """, (cuenta,))
        filas = cursor.fetchall()

    if not filas:
        return jsonify({"success": False, "error": "No se encontraron datos."})

    if not seleccion_id and len(filas) > 1:
        opciones = []
        for row in filas:
            opciones.append({
                "id": row[0],
                "numeroCuenta": row[1],
                "nombreCompleto": row[2],
                "planEstudios": row[3],
                "especializacion": row[4],
                "modalidad": row[13]
            })
        return jsonify({"success": True, "multiples": opciones})

    row = filas[0]

    return jsonify({
        "success": True,
        "id": row[0],
        "numeroCuenta": row[1],
        "nombreCompleto": row[2],
        "planEstudios": row[3],
        "especializacion": row[4],
        "tituloTesina": row[5],
        "tutor": row[6],
        "presidente": row[7],
        "secretario": row[8],
        "vocal1": row[9],
        "vocal2": row[10],
        "vocal3": row[11],
        "sexo": row[12],
        "modalidad": row[13],
        "sexoTutor": row[14],
    })

@votos_Oficio_PUEI_bp.route("/modificar_datos", methods=["POST"])
def modificar_datos():
    datos = request.get_json()
    plan = int(datos["planEstudios"])
    
    if not _validar_rango_plan(plan):
        return jsonify({"success": False, "error": "Plan fuera de rango (3000–5999)."})
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE posgrado
            SET nombreCompleto=?, planEstudios=?, especializacion=?, tituloTesina=?,
                tutor=?, presidente=?, secretario=?, vocal1=?, vocal2=?, vocal3=?,
                sexo=?, modalidad=?, sexoTutor=?
            WHERE id=?
        """, (
            datos["nombre"], plan, datos["especializacion"], datos["tituloTesina"],
            datos["tutor"], datos["presidente"], datos["secretario"], datos["vocal1"],
            datos["vocal2"], datos["vocal3"], datos["sexo"], datos["modalidad"], datos["sexoTutor"], datos["id"]
        ))
        conn.commit()

    return jsonify({"success": True})

# --------- PDFs ---------
@votos_Oficio_PUEI_bp.route("/ver_pdf/<filename>")
def ver_pdf(filename):
    return send_from_directory("static/Documentos", filename, mimetype="application/pdf", as_attachment=False)

@votos_Oficio_PUEI_bp.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
