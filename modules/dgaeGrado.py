
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
import os
from auth import permission_required
from config import direccionBase, direccionImagen,direccionPDF
from db import get_connection

dgaeGrado_bp = Blueprint('dgaeGrado', __name__, template_folder='../templates')

os.makedirs(direccionPDF, exist_ok=True)

#################################################################################################################################
def fecha_texto():
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    hoy = datetime.now()
    return f"Ciudad Universitaria, Cd. Mx., a {hoy.day} de {meses[hoy.month]} de {hoy.year}."

def buscar_alumno(numero_cuenta):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT numeroCuenta, nombreCompleto, planEstudios, especializacion, modalidad
            FROM posgrado
            WHERE numeroCuenta = ?
            ORDER BY id DESC
            LIMIT 1
        """, (numero_cuenta,))
        return cur.fetchone()

def listar_registros_grado(numero_cuenta):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion, modalidad
            FROM posgrado
            WHERE numeroCuenta = ?
            ORDER BY planEstudios
        """, (numero_cuenta,))
        return cur.fetchall()

def buscar_alumno_por_id(registro_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion, modalidad
            FROM posgrado
            WHERE id = ?
            LIMIT 1
        """, (registro_id,))
        return cur.fetchone()

def inferir_programa_grado(plan):
    plan = int(plan)

    if 3000 <= plan <= 3999:
        return "Especialidad"

    if 4000 <= plan <= 4999:
        return "Maestría"

    if 5000 <= plan <= 5999:
        return "Doctorado"

    return "Desconocido"

def limpiar_texto(valor):
    return str(valor).strip() if valor is not None else ""

def resolver_programa_y_plan(plan_estudios, especializacion):
    plan = limpiar_texto(plan_estudios)
    esp = limpiar_texto(especializacion).upper()

    programa = "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
    clave_programa = "125"
    clave_plan = plan if plan else "----"
    nombre_plan = "MAESTRÍA EN INGENIERÍA"

    if not plan.isdigit():
        return programa, clave_programa, nombre_plan, clave_plan

    plan_num = int(plan)

    if 3000 <= plan_num <= 3999:
        programa = "PROGRAMA ÚNICO DE ESPECIALIZACIONES DE INGENIERÍA"
        nombre_plan = "ESPECIALIZACIÓN EN " + (especializacion if especializacion else "----")

    elif 4000 <= plan_num <= 4999:
        programa = "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
        nombre_plan = "MAESTRÍA EN INGENIERÍA"

    elif 5000 <= plan_num <= 5999:
        programa = "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
        nombre_plan = "DOCTORADO EN INGENIERÍA"

    return programa, clave_programa, nombre_plan, clave_plan

def obtener_marcas_documentos(tipo_doc):
    """
    Regresa las X de la columna Programa.
    7 posiciones = documentos 1 al 7.
    En presencial, el documento 7 no se usa, pero mantenemos la lista completa
    para trabajar más fácil y luego recortamos la tabla.
    """

    marcas_por_tipo = {
        "presencial_todas_x": ["X", "X", "X", "X", "X", "X"],
        "presencial_sin_mencion_honorifica": ["X", "X", " ", "X", "X", "X"],
        "presencial_sin_medalla_alfonso_caso": ["X", "X", "X", " ", "X", "X"],
        "presencial_sin_mencion_y_medalla": ["X", "X", " ", " ", "X", "X"],

        "virtual_todas_x": ["X", "X", "X", "X", "X", "X", "X"],
        "virtual_sin_mencion_honorifica": ["X", "X", " ", "X", "X", "X", "X"],
        "virtual_sin_medalla_alfonso_caso": ["X", "X", "X", " ", "X", "X", "X"],
        "virtual_sin_mencion_y_medalla": ["X", "X", " ", " ", "X", "X", "X"],
    }

    return marcas_por_tipo.get(tipo_doc, ["X", "X", "X", "X", "X", "X", "X"])

def es_presencial(tipo_doc):
    return tipo_doc.startswith("presencial_")

def es_virtual(tipo_doc):
    return tipo_doc.startswith("virtual_")

def nombre_archivo_por_tipo(tipo_doc, numero_cuenta):
    nombres = {
        "presencial_todas_x": f"dgae_grado_presencial_todas_x_{numero_cuenta}.pdf",
        "presencial_sin_mencion_honorifica": f"dgae_grado_presencial_sin_mencion_honorifica_{numero_cuenta}.pdf",
        "presencial_sin_medalla_alfonso_caso": f"dgae_grado_presencial_sin_medalla_alfonso_caso_{numero_cuenta}.pdf",
        "presencial_sin_mencion_y_medalla": f"dgae_grado_presencial_sin_mencion_y_medalla_{numero_cuenta}.pdf",

        "virtual_todas_x": f"dgae_grado_virtual_todas_x_{numero_cuenta}.pdf",
        "virtual_sin_mencion_honorifica": f"dgae_grado_virtual_sin_mencion_honorifica_{numero_cuenta}.pdf",
        "virtual_sin_medalla_alfonso_caso": f"dgae_grado_virtual_sin_medalla_alfonso_caso_{numero_cuenta}.pdf",
        "virtual_sin_mencion_y_medalla": f"dgae_grado_virtual_sin_mencion_y_medalla_{numero_cuenta}.pdf",
    }
    return nombres.get(tipo_doc, f"dgae_grado_{numero_cuenta}.pdf")

def generar_acuse_graduacion(tipo_doc, numero_cuenta, nombre_alumno, plan_estudios, especializacion, modalidad):
    programa, clave_programa, nombre_plan, clave_plan = resolver_programa_y_plan(plan_estudios, especializacion)
    marcas = obtener_marcas_documentos(tipo_doc)

    pdf = FPDF(unit="mm", format="Letter")
    pdf.set_auto_page_break(False)
    pdf.add_page()

    # ========= LOGOS =========
    logo_unam = os.path.join(direccionImagen, "UNAM_SinTexto.jpeg")
    logo_dgae = os.path.join(direccionImagen, "LogoDGAE.PNG")

    if os.path.exists(logo_unam):
        pdf.image(logo_unam, x=12, y=9, w=22, h=24)

    if os.path.exists(logo_dgae):
        pdf.image(logo_dgae, x=170, y=14, w=28, h=16)

    # ========= ENCABEZADO =========
    pdf.set_draw_color(120, 120, 120)
    pdf.set_line_width(0.2)

    pdf.set_xy(0, 12)
    pdf.set_font("Arial", size=11)
    pdf.cell(216, 6, "Universidad Nacional Autónoma de México", ln=1, align="C")
    pdf.set_x(0)
    pdf.cell(216, 6, "Secretaría General", ln=1, align="C")
    pdf.set_x(0)
    pdf.cell(216, 6, "Dirección General de Administración Escolar", ln=1, align="C")
    pdf.set_x(0)
    pdf.cell(216, 6, "Dirección de Certificación y Control Documental", ln=1, align="C")

    pdf.line(14, 36, 202, 36)

    pdf.set_xy(0, 39)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(216, 8, "Formato de acuse de carpeta de graduación", ln=1, align="C")

    pdf.line(14, 49, 202, 49)

    # ========= TABLA SUPERIOR =========
    x0 = 14
    y0 = 58
    w_total = 174

    h1 = 12
    h3 = 14

    c1 = 44
    c2 = 80
    c3 = 16
    c4 = 34

    # -------- calcular altura dinámica de fila 2 --------
    linea_h_plan = 5
    w_plan = c2 - 6

    pdf.set_font("Arial", size=10)

    def contar_lineas_aprox(pdf, texto, ancho):
        texto = str(texto).strip()
        if not texto:
            return 1

        palabras = texto.split()
        lineas = 1
        actual = ""

        for palabra in palabras:
            prueba = palabra if actual == "" else actual + " " + palabra
            if pdf.get_string_width(prueba) <= ancho:
                actual = prueba
            else:
                lineas += 1
                actual = palabra

        return lineas

    lineas_plan = contar_lineas_aprox(pdf, nombre_plan, w_plan)
    h2 = max(12, lineas_plan * linea_h_plan + 4)

    pdf.rect(x0, y0, w_total, h1 + h2 + h3)
    pdf.line(x0, y0 + h1, x0 + w_total, y0 + h1)
    pdf.line(x0, y0 + h1 + h2, x0 + w_total, y0 + h1 + h2)

    pdf.line(x0 + c1, y0, x0 + c1, y0 + h1 + h2 + h3)
    pdf.line(x0 + c1 + c2, y0, x0 + c1 + c2, y0 + h1 + h2 + h3)
    pdf.line(x0 + c1 + c2 + c3, y0, x0 + c1 + c2 + c3, y0 + h1 + h2 + h3)

    pdf.set_font("Arial", size=10)

    # fila 1
    pdf.set_xy(x0 + 2, y0 + 3)
    pdf.cell(c1 - 4, 5, "Programa:", 0, 0, "L")

    pdf.set_xy(x0 + c1 + 1, y0 + 2)
    pdf.multi_cell(c2 - 2, 4.8, programa, 0, "L")

    pdf.set_xy(x0 + c1 + c2 + 2, y0 + 3)
    pdf.cell(c3 - 4, 5, "Clave:", 0, 0, "L")

    pdf.set_xy(x0 + c1 + c2 + c3 + 1, y0 + 3)
    pdf.cell(c4 - 2, 5, clave_programa, 0, 0, "L")

    # fila 2
    pdf.set_xy(x0 + 2, y0 + h1 + 3)
    pdf.cell(c1 - 4, 5, "Plan de estudios:", 0, 0, "L")

    x_plan = x0 + c1 + 1
    y_plan = y0 + h1 + 3

    pdf.set_xy(x_plan, y_plan)
    pdf.multi_cell(w_plan, linea_h_plan, nombre_plan, 0, "L")

    # clave
    pdf.set_xy(x0 + c1 + c2 + 2, y0 + h1 + 3)
    pdf.cell(c3 - 4, 5, "Clave:", 0, 0, "L")

    pdf.set_xy(x0 + c1 + c2 + c3 + 1, y0 + h1 + 3)
    pdf.cell(c4 - 2, 5, clave_plan, 0, 0, "L")

    # fila 3
    pdf.set_xy(x0 + 2, y0 + h1 + h2 + 3)
    pdf.multi_cell(c1 - 4, 5, "Nombre de la o del\nalumno:", 0, "L")

    x_alumno = x0 + c1 + 1
    y_alumno = y0 + h1 + h2 + 4
    w_alumno = c2 - 2

    pdf.set_xy(x_alumno, y_alumno)
    pdf.multi_cell(w_alumno, 5, nombre_alumno, 0, "L")

    
    # guardamos posición base de la fila
    y_base = y0 + h1 + h2 + 3

    # CUENTA (lado derecho, fijo arriba)
    pdf.set_xy(x0 + c1 + c2 + 2, y_base)
    pdf.cell(c3 - 4, 5, "Cuenta:", 0, 0, "L")

    pdf.set_xy(x0 + c1 + c2 + c3 + 1, y_base + 1)
    pdf.cell(c4 - 2, 5, numero_cuenta, 0, 0, "L")


    # ========= TABLA DE DOCUMENTOS =========
    y_tab = y0 + h1 + h2 + h3 + 5
    x_tab = 14
    w_num = 14
    w_desc = 121
    w_prog = 22
    w_dgae = 15
    total_w = w_num + w_desc + w_prog + w_dgae

    if es_presencial(tipo_doc):
        filas = [
            ("1", "Original del acta de grado debidamente requisitada (FEU)", marcas[0], ""),
            ("2", "Copia del acta de grado", marcas[1], ""),
            ("3", "Oficio de Mención Honorífica (en caso de ser otorgada)", marcas[2], ""),
            ("4", "Oficio de recomendación como candidata/o a la medalla Alfonso Caso\n(de ser considerada/o)", marcas[3], ""),
            ("5", "Original de citatorio", marcas[4], ""),
            ("6", "Autorización de examen de grado firmada por la/el secretaria/o del\njurado", marcas[5], ""),
        ]
    else:
        filas = [
            ("1", "Original del acta de grado debidamente requisitada (FEU)", marcas[0], ""),
            ("2", "Copia del acta de grado", marcas[1], ""),
            ("3", "Oficio de Mención Honorífica (en caso de ser otorgada)", marcas[2], ""),
            ("4", "Oficio de recomendación como candidata/o a la medalla Alfonso Caso\n(de ser considerada/o)", marcas[3], ""),
            ("5", "Original de citatorio", marcas[4], ""),
            ("6", "Autorización de examen de grado firmada por la/el secretaria/o del\njurado", marcas[5], ""),
            ("7", "Formatos de autorización examen virtual (solicitud alumno, oficio\nde autorización, cartas de confidencialidad)", marcas[6], ""),
        ]

    if es_presencial(tipo_doc):
        altos = [12, 12, 14, 18, 12, 18]
    else:
        altos = [12, 12, 14, 18, 12, 18, 18]

    header_h = 12
    total_h = header_h + sum(altos)

    pdf.rect(x_tab, y_tab, total_w, total_h)
    pdf.line(x_tab + w_num, y_tab, x_tab + w_num, y_tab + total_h)
    pdf.line(x_tab + w_num + w_desc, y_tab, x_tab + w_num + w_desc, y_tab + total_h)
    pdf.line(x_tab + w_num + w_desc + w_prog, y_tab, x_tab + w_num + w_desc + w_prog, y_tab + total_h)
    pdf.line(x_tab, y_tab + header_h, x_tab + total_w, y_tab + header_h)

    pdf.set_font("Arial", "B", 9)
    pdf.set_xy(x_tab + 1, y_tab + 3)
    pdf.cell(w_num - 2, 5, "Num.", 0, 0, "C")
    pdf.set_xy(x_tab + w_num + 2, y_tab + 3)
    pdf.cell(w_desc - 4, 5, "Listado de documentos", 0, 0, "L")
    pdf.set_xy(x_tab + w_num + w_desc + 1, y_tab + 3)
    pdf.multi_cell(w_prog - 2, 5, "Programa", 0, "C")
    pdf.set_xy(x_tab + w_num + w_desc + w_prog + 1, y_tab + 3)
    pdf.multi_cell(w_dgae - 2, 5, "DGAE\nRecibe", 0, "C")

    y_cursor = y_tab + header_h
    pdf.set_font("Arial", size=8.5)

    for i, fila in enumerate(filas):
        h = altos[i]
        pdf.line(x_tab, y_cursor + h, x_tab + total_w, y_cursor + h)

        num, desc, marca, dgae = fila

        pdf.set_xy(x_tab + 1, y_cursor + 3)
        pdf.cell(w_num - 2, 5, num, 0, 0, "C")

        pdf.set_xy(x_tab + w_num + 2, y_cursor + 2)
        pdf.multi_cell(w_desc - 4, 4.8, desc)

        pdf.set_xy(x_tab + w_num + w_desc, y_cursor + 3)
        pdf.cell(w_prog, 5, marca, 0, 0, "C")

        pdf.set_xy(x_tab + w_num + w_desc + w_prog, y_cursor + 3)
        pdf.cell(w_dgae, 5, dgae, 0, 0, "C")

        y_cursor += h

    # ========= FECHA =========
    if es_presencial(tipo_doc):
        pdf.set_font("Arial", "B", 10)
        pdf.set_xy(14, 213)
        pdf.cell(150, 6, fecha_texto(), 0, 0, "L")
    else:
        pdf.set_font("Arial", "B", 10)
        pdf.set_xy(14, 228)
        pdf.cell(150, 6, fecha_texto(), 0, 0, "L")

    # ========= FIRMAS =========
    if es_presencial(tipo_doc):
        x_f = 14
        y_f = 226
        w_f = 174
        h_f = 28

        pdf.rect(x_f, y_f, w_f, h_f)
        pdf.line(x_f + 87, y_f, x_f + 87, y_f + h_f)

        pdf.set_font("Arial", "B", 10)
        pdf.set_xy(x_f, y_f + 2)
        pdf.cell(87, 6, "Entrega", 0, 0, "C")
        pdf.set_xy(x_f + 87, y_f + 2)
        pdf.cell(87, 6, "Recibe", 0, 0, "C")

        pdf.line(x_f + 10, y_f + 20, x_f + 77, y_f + 20)
        pdf.line(x_f + 97, y_f + 20, x_f + 164, y_f + 20)

        pdf.set_font("Arial", size=9)
        pdf.set_xy(x_f + 10, y_f + 21)
        pdf.cell(67, 5, "Nombre y firma", 0, 0, "C")
        pdf.set_xy(x_f + 10, y_f + 15)
        pdf.cell(67, 5, "M.I. BRISIA JON SERRANO", 0, 0, "C")
        pdf.set_xy(x_f + 97, y_f + 21)
        pdf.cell(67, 5, "Nombre y firma", 0, 0, "C")

    else:
        x_f = 14
        y_f = 236
        w_f = 174
        h_f = 28

        pdf.rect(x_f, y_f, w_f, h_f)
        pdf.line(x_f + 87, y_f, x_f + 87, y_f + h_f)

        pdf.set_font("Arial", "B", 10)
        pdf.set_xy(x_f, y_f + 2)
        pdf.cell(87, 6, "Entrega", 0, 0, "C")
        pdf.set_xy(x_f + 87, y_f + 2)
        pdf.cell(87, 6, "Recibe", 0, 0, "C")

        pdf.line(x_f + 10, y_f + 20, x_f + 77, y_f + 20)
        pdf.line(x_f + 97, y_f + 20, x_f + 164, y_f + 20)

        pdf.set_font("Arial", size=9)
        pdf.set_xy(x_f + 10, y_f + 21)
        pdf.cell(67, 5, "Nombre y firma", 0, 0, "C")
        pdf.set_xy(x_f + 10, y_f + 15)
        pdf.cell(67, 5, "M.I. BRISIA JON SERRANO", 0, 0, "C")
        pdf.set_xy(x_f + 97, y_f + 21)
        pdf.cell(67, 5, "Nombre y firma", 0, 0, "C")

    # ========= PIE =========
    pdf.set_font("Arial", size=8.5)
    pdf.set_xy(148, 271)
    pdf.cell(30, 5, "Rev. Octubre_2024", 0, 0, "L")

    logo_UniversidadNacion = os.path.join(direccionImagen, "Nacion.PNG")
    if os.path.exists(logo_UniversidadNacion):
        pdf.image(logo_UniversidadNacion, x=178, y=265, w=10, h=10)

    salida_pdf = pdf.output(dest="S")

    if isinstance(salida_pdf, str):
        pdf_bytes = salida_pdf.encode("latin1")
    else:
        pdf_bytes = bytes(salida_pdf)

    return BytesIO(pdf_bytes)


@dgaeGrado_bp.route("/", methods=["GET", "POST"])
@permission_required("dgae_grado")
def index():
    if "user_id" not in session:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("dgaeGrado.html")

    numero = (request.form.get("numeroDeCuenta") or "").strip()
    tipo_doc = (request.form.get("tipoDocumento") or "").strip()
    seleccion_id = request.form.get("seleccion_id")

    if not numero or not numero.isdigit() or len(numero) != 9:
        return jsonify(success=False, error="Número de cuenta inválido. Debe tener 9 dígitos."), 400

    tipos_validos = {
        "presencial_todas_x",
        "presencial_sin_mencion_honorifica",
        "presencial_sin_medalla_alfonso_caso",
        "presencial_sin_mencion_y_medalla",
        "virtual_todas_x",
        "virtual_sin_mencion_honorifica",
        "virtual_sin_medalla_alfonso_caso",
        "virtual_sin_mencion_y_medalla",
    }

    if seleccion_id:
        alumno = buscar_alumno_por_id(int(seleccion_id))

        if not alumno:
            return jsonify(success=False, error="Selección inválida."), 404

        _id, numero_cuenta, nombre_completo, plan_estudios, especializacion, modalidad = alumno

    else:
        filas = listar_registros_grado(numero)

        if not filas:
            return jsonify(success=False, error="No se encontró el número de cuenta en la base de datos."), 404

        if len(filas) > 1:
            opciones = []

            for rid, cuenta, nombre, plan, espec, modalidad in filas:
                opciones.append({
                    "id": rid,
                    "numeroCuenta": cuenta,
                    "nombre": nombre,
                    "planEstudios": int(plan),
                    "programa": inferir_programa_grado(plan),
                    "especializacion": espec or ""
                })

            return jsonify({
                "success": True,
                "multiples": opciones,
                "resumen": "Este alumno tiene más de un plan. Selecciona cuál usar para DGAE Grado."
            })

        _id, numero_cuenta, nombre_completo, plan_estudios, especializacion, modalidad = filas[0]

    if not tipo_doc:
        return jsonify(success=True, msg="Cuenta válida.")

    if tipo_doc not in tipos_validos:
        return jsonify(success=False, error="Tipo de documento no reconocido."), 400

    return jsonify(
        success=True,
        documento=url_for(
            "dgaeGrado.ver_documento",
            numeroDeCuenta=numero,
            tipoDocumento=tipo_doc,
            seleccion_id=seleccion_id or _id
        )
    )

@dgaeGrado_bp.route("/documento")
@permission_required("dgae_grado")
def ver_documento():
    numero = (request.args.get("numeroDeCuenta") or "").strip()
    tipo_doc = (request.args.get("tipoDocumento") or "").strip()
    seleccion_id = request.args.get("seleccion_id")

    if not numero or not numero.isdigit() or len(numero) != 9:
        return "Número de cuenta inválido.", 400

    tipos_validos = {
        "presencial_todas_x",
        "presencial_sin_mencion_honorifica",
        "presencial_sin_medalla_alfonso_caso",
        "presencial_sin_mencion_y_medalla",
        "virtual_todas_x",
        "virtual_sin_mencion_honorifica",
        "virtual_sin_medalla_alfonso_caso",
        "virtual_sin_mencion_y_medalla",
    }

    if tipo_doc not in tipos_validos:
        return "Tipo de documento no reconocido.", 400

    if seleccion_id:
        alumno = buscar_alumno_por_id(int(seleccion_id))

        if not alumno:
            return "Selección inválida.", 404

        _id, numero_cuenta, nombre_completo, plan_estudios, especializacion, modalidad = alumno

    else:
        filas = listar_registros_grado(numero)

        if not filas:
            return "No se encontró el número de cuenta.", 404

        if len(filas) > 1:
            return "Esta cuenta tiene más de un plan. Selecciona uno primero.", 400

        _id, numero_cuenta, nombre_completo, plan_estudios, especializacion, modalidad = filas[0]

    pdf_buffer = generar_acuse_graduacion(
        tipo_doc=tipo_doc,
        numero_cuenta=limpiar_texto(numero_cuenta),
        nombre_alumno=limpiar_texto(nombre_completo),
        plan_estudios=limpiar_texto(plan_estudios),
        especializacion=limpiar_texto(especializacion),
        modalidad=limpiar_texto(modalidad)
    )

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name="acuse_graduacion.pdf"
    )

@dgaeGrado_bp.after_request
@permission_required("dgae_grado")
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
