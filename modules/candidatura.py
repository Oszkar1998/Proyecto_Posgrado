# Libreria Necesaria para conectar PYTHON con HTMLX, y con la Base de Datos
from flask import Blueprint , render_template, request, jsonify, session, redirect, url_for, send_from_directory
import sqlite3
from datetime import datetime
from fpdf import FPDF
from auth import permission_required

candidatura_bp = Blueprint('candidatura', __name__, template_folder='../templates')

# Variables Globales 
direccionBase = 'static/BaseDeDatos/basePosgrado.db'
direccionImagen = "static/Imagenes/"
direccionPDF = "static/Documentos/"

def generar_acta_candidatura(pdf: FPDF, fila_pos, programa: str, folio_acta: int) -> str:

    filename = "ActaCandidatura.pdf"
    
    idPos, nombreCompletoPos, numeroCuentaPos, especializacionPos, tituloProyectoPos, semestreIngresoPos, semestrePresentadoPos, evaluacionPos, presidentePos, secretarioPos, vocal1Pos, vocal2Pos, vocal3Pos, sexoPos, modalidadSedepos, fechaExamenPos, horaExamenPos = obtenerDatosCandidatura(fila_pos[2])

    dia, mes, año = fechaActual()
    diaExa, mesExa, anoExa = fecha(fechaExamenPos)

    if sexoPos == "F":
        grado = "DOCTORA"
    elif sexoPos == "M":
        grado = "DOCTOR"
    else:
        raise ValueError("Sexo no reconocido.")
    
    nombreCompletoPos = limpiar_texto(nombreCompletoPos)
    tituloProyectoPos = limpiar_texto(tituloProyectoPos)
    presidentePos = limpiar_texto(presidentePos)
    secretarioPos = limpiar_texto(secretarioPos)
    vocal1Pos = limpiar_texto(vocal1Pos)
    vocal2Pos = limpiar_texto(vocal2Pos)
    vocal3Pos = limpiar_texto(vocal3Pos)

    # Agregar una página
    pdf.add_page()

    # Imagen 
    pdf.image(direccionImagen + "Avotos.jpeg", x=15, y=20, w=25, h=27)  # Agregar imagen
    pdf.image(direccionImagen + "EscudoPosgrado.png", x=168, y=20, w=30, h=10)  # Agregar imagen

    # Encabezado del documento
    pdf.set_font("Arial", size=14, style="B")
    pdf.set_xy(40, 22)
    pdf.multi_cell(130, 5, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="C")

    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(40, 28)
    pdf.multi_cell(130, 5, "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA", align="C")

    pdf.set_font("Arial", size=12.5, style="B")
    pdf.set_xy(29, 40)
    pdf.multi_cell(150, 5, "ACTA DE CANDIDATURA AL GRADO DE " + grado, align="C")
    

    parrafo_html = (
        f"<p>{modalidadSedepos} de la Universidad Nacional Autónoma de México, siendo las "
        f"<b>{horaExamenPos} horas</b> del dia <b>{diaExa} de {mesExa} de {anoExa},</b> se presentó:</p>"
    )
    pdf.set_font("Arial", size=12)
    pdf.set_xy(15, 50)
    pdf.write_html(parrafo_html)

    semestrePresentadoPos = formatoNombre(semestrePresentadoPos)
    evaluacionPos = formatoNombre(evaluacionPos)


    parrafo_html = (
        f"<p>Nombre Completo: <b>{nombreCompletoPos}</b><br>"
        f"Número de cuenta: <b>{numeroCuentaPos}</b><br>"
        f"Título del proyecto: <b>{tituloProyectoPos.strip().lower().capitalize()}.</b><br>"
        f"Semestre de ingreso: <b>{semestreIngresoPos}</b><br>"
        f"Semestre en que se está presentando el examen de candidatura: <b>{semestrePresentadoPos} semestre</b><br>"
        f"Evaluación: <b>{evaluacionPos}</b></p>"
    )
    pdf.set_font("Arial", size=12)
    pdf.ln(2)
    pdf.set_x(15)
    pdf.write_html(parrafo_html)


    parrafo_html = (
        f"<p>El jurado de examen de candidatura al grado de doctorado, nombrado por el Comité Académico de este programa de posgrado, está integrado por las y/o los siguientes:</p>"
    )
    pdf.set_font("Arial", size=12)
    pdf.ln(2)
    pdf.set_x(15)
    pdf.write_html(parrafo_html)


    # SINODALES 
    parrafo_html = (
        f"<p><b>1.  {presidentePos}</b> (Presidente)<br>"
        f"<b>2.  {secretarioPos}</b> (Secretario)<br>"
        f"<b>3.  {vocal1Pos}</b> (Vocal)<br>"
        f"<b>4.  {vocal2Pos}</b> (Vocal)<br>"
        f"<b>5.  {vocal3Pos}</b> (Vocal)</p>"
    )
    pdf.set_font("Arial", size=12)
    pdf.ln(8)
    pdf.set_x(30)
    pdf.write_html(parrafo_html)


    parrafo_html = (
        f"<p>De acuerdo con el artículo 45 del Reglamento General de Estudios de Posgrado de 2018, el resultado del examen fue:</p>"
    )
    pdf.set_font("Arial", size=12)
    pdf.ln(2)
    pdf.set_x(15)
    pdf.write_html(parrafo_html)


    pdf.set_font("Arial", size=12, style="BU")
    pdf.ln(8)
    pdf.set_x(40)
    pdf.multi_cell(100, 5, "                                                           ", align="R")


    parrafo_html = (
        f"<p>Dando por concluido el examen de candidatura al grado de doctorado, el jurado firma al calce.</p>"
    )
    pdf.set_font("Arial", size=12)
    pdf.ln(6)
    pdf.set_x(15)
    pdf.write_html(parrafo_html)


    # SINODALES 
    #///////////////////////////////////////////////////////////////
    pdf.set_font("Arial", size=11.8, style="BU")
    pdf.set_xy(12,205)# Izquierda
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(76,205)# Centro 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(139,205)# Derecha 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    
    pdf.set_xy(12,210)
    pdf.set_font("Arial", size=11.8)
    pdf.multi_cell(60, 5, "Presidente", align="C")
    pdf.set_xy(76,210)
    pdf.multi_cell(60, 5, "Secretario", align="C")
    pdf.set_xy(139,210)
    pdf.multi_cell(60, 5, "Primer Vocal", align="C")
    
    pdf.set_font("Arial", size=11.8, style="BU")
    pdf.set_xy(42,230)# Izquierda
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(106,230)# Centro 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    
    pdf.set_font("Arial", size=11.8)
    pdf.set_xy(42,235)
    pdf.multi_cell(60, 5, "Segundo Vocal", align="C")
    pdf.set_xy(106,235)
    pdf.multi_cell(60, 5, "Tercer Vocal", align="C")

    # CONTADOR 
    folio_acta = str(folio_acta)
    if len(folio_acta) == 1:
        folio_acta = "00" + folio_acta
    elif len(folio_acta) == 2:
        folio_acta = "0" + folio_acta

    parrafo_html = (
        f"<p>No. Folio del Programa<br>"
        f"PMDI/AOPP/AC/{folio_acta}/2026</p>"
    )
    pdf.set_font("Arial", size=9)
    pdf.set_xy(15, 249)
    pdf.write_html(parrafo_html)


    pdf.output(direccionPDF + filename, "F")
    return filename

def generar_citatorio_candidatura(pdf: FPDF, fila_pos, programa: str) -> str:

    idPos, nombreCompletoPos, numeroCuentaPos, especializacionPos, tituloProyectoPos, semestreIngresoPos, semestrePresentadoPos, evaluacionPos, presidentePos, secretarioPos, vocal1Pos, vocal2Pos, vocal3Pos, sexoPos, modalidadSedepos, fechaExamenPos, horaExamenPos = obtenerDatosCandidatura(fila_pos[2])

    dia, mes, año = fechaActual()
    diaExa, mesExa, anoExa = fecha(fechaExamenPos)

    filename = "CitatorioCandidatura.pdf"

    if sexoPos == "F":
        grado = "DOCTORA"
    elif sexoPos == "M":
        grado = "DOCTOR"
    else:
        raise ValueError("Sexo no reconocido.")
    
    # Agregar una página
    pdf.add_page()

    # Imagen 
    pdf.image(direccionImagen + "EscudoPosgrado.png", x=15, y=20, w=40, h=20)  # Agregar imagen

    # Encabezado del documento
    pdf.set_font("Arial", size=14.5, style="B")
    pdf.set_xy(56, 22)
    pdf.multi_cell(130, 5, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="C")

    pdf.set_font("Arial", size=12.5, style="B")
    pdf.set_xy(56, 28)
    pdf.multi_cell(130, 5, "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA", align="C")

    pdf.set_font("Arial", size=13, style="B")
    pdf.set_xy(42, 40)
    pdf.multi_cell(150, 5, "CITATORIO PARA EXAMEN DE CANDIDATURA AL GRADO DE " + grado, align="C")
    

    parrafo_html = (
        f"<p>Por medio de la presente se les cita al examen de candidatura para obtener el grado de <b>{grado} EN INGENIERÍA </b>"
        f"del alumno(a) <b>{nombreCompletoPos},</b> C. de Conocimiento: <b>{especializacionPos}.</b></p>"
    )
    pdf.set_font("Arial", size=12)
    pdf.set_xy(15, 56)
    pdf.write_html(parrafo_html)

    if modalidadSedepos == "En la Facultad de Ingeniería":
        modalidadSedepos = "Facultad de Ingeniería"
    elif modalidadSedepos == "En la Aula Virtual Universitaria":
        modalidadSedepos = "Aula Virtual Universitaria"
    elif modalidadSedepos == "En el Instituto de Ingeniería":
        modalidadSedepos = "Instituto de Ingeniería"
    elif modalidadSedepos == "En el Instituto de Ciencias Aplicadas y Tecnología":
        modalidadSedepos = "Instituto de Ciencias Aplicadas y Tecnología"
    elif modalidadSedepos == "En el Instituto de Energías Renovables":
        modalidadSedepos = "Instituto de Energías Renovables"


    # ETIQUETA
    pdf.set_font("Arial", size=12)
    pdf.set_xy(18, 80)
    pdf.cell(25, 5, "Lugar:")
    # VALOR
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(32, 80)
    pdf.multi_cell(140, 5, modalidadSedepos, align="L")


    fechaHora = f"{diaExa} de {mesExa} de {anoExa}, a las {horaExamenPos} hrs."
    # ETIQUETA
    pdf.set_font("Arial", size=12)
    pdf.set_xy(18, 92)
    pdf.cell(40, 5, "Fecha y Hora:")
    # VALOR
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(47, 92)
    pdf.multi_cell(120, 5, fechaHora, align="L")

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(100, 5, "El examen se realizará con el siguiente jurado: ", align="C")

    pdf.set_font("Arial", size=12, style="B")
    pdf.ln(7)
    pdf.multi_cell(30, 5, "Jurado ", align="C")

    # JURADO 
    pdf.set_font("Arial", size=12, style="BU")

    # Etiquetas del jurado
    pdf.set_font("Arial", size=12, style="U")
    pdf.set_xy(20, 128)
    pdf.multi_cell(0, 5, "Presidente:", align="L")
    pdf.set_xy(20, 138)
    pdf.multi_cell(0, 5, "Secretario:", align="L")
    pdf.set_xy(20, 148)
    pdf.multi_cell(0, 5, "Primer Vocal:", align="L")
    pdf.set_xy(20, 158)
    pdf.multi_cell(0, 5, "Segundo Vocal:", align="L")
    pdf.set_xy(20, 168)
    pdf.multi_cell(0, 5, "Tercer Vocal:", align="L")

    # Nombres del jurado
    pdf.set_font("Arial", size=12)
    pdf.set_xy(53, 128)
    presidentePos = formatoNombre(presidentePos)
    pdf.multi_cell(0, 5, presidentePos, align="L")
    pdf.set_xy(53, 138)
    secretarioPos = formatoNombre(secretarioPos)
    pdf.multi_cell(0, 5, secretarioPos, align="L")
    pdf.set_xy(53, 148)
    vocal1Pos = formatoNombre(vocal1Pos)
    pdf.multi_cell(0, 5, vocal1Pos, align="L")
    pdf.set_xy(53, 158)
    vocal2Pos = formatoNombre(vocal2Pos)
    pdf.multi_cell(0, 5, vocal2Pos, align="L")
    pdf.set_xy(53, 168)
    vocal3Pos = formatoNombre(vocal3Pos)
    pdf.multi_cell(0, 5, vocal3Pos, align="L")

    # Firma
    pdf.set_xy(156.5, 113)
    pdf.multi_cell(40, 5, "Firma", align="C")

    # Líneas para firma
    pdf.set_font("Arial", size=12, style="BU")
    pdf.set_xy(102, 128)
    pdf.multi_cell(0, 5, "                                    ", align="R")
    pdf.set_xy(102, 138)
    pdf.multi_cell(0, 5, "                                    ", align="R")
    pdf.set_xy(102, 148)
    pdf.multi_cell(0, 5, "                                    ", align="R")
    pdf.set_xy(102, 158)
    pdf.multi_cell(0, 5, "                                    ", align="R")
    pdf.set_xy(102, 168)
    pdf.multi_cell(0, 5, "                                    ", align="R")

    # Pie de página
    pdf.set_font("Arial", size=12)
    pdf.set_xy(17, 203)
    pdf.multi_cell(40, 5, "A t e n t a m e n t e", align="C")
    pdf.set_font("Arial", size=12)
    pdf.set_xy(9, 210)
    pdf.multi_cell(100, 5, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", align="C")
    pdf.set_font("Arial", size=12)
    pdf.set_xy(11, 217)
    pdf.multi_cell(100, 5, "Ciudad Universitaria, a " + dia + " de " + mes + " de " + año, align="C")

    # Firma de la Coordinadora
    pdf.set_font("Arial", size=12, style="BU")
    pdf.set_xy(8, 240)
    pdf.multi_cell(110, 5, "                                                                          ", align="C")
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(8, 247)
    pdf.multi_cell(100, 5, "Dr. Gabriel Eduardo Sandoval Romero", align="C")
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(6, 254)
    pdf.multi_cell(80, 5, "Coordinador del Programa", align="C")

    pdf.output(direccionPDF + filename, "F")
    
    return filename

#################################################################################################################################
def obtenerDatosCandidatura(numero_cuenta: str):
    conn = sqlite3.connect(direccionBase)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM candidatura
        WHERE numero_cuenta = ?
        LIMIT 1
    """, (numero_cuenta,))

    fila = cur.fetchone()
    conn.close()
    return fila

def fechaActual():

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    año = fecha_actual[0:4] 
    mes = fecha_actual[5:7]
    dia = fecha_actual[8:10]

    if mes == '01':
        mes = 'enero'
    elif mes == '02':
        mes = 'febrero'
    elif mes == '03':
        mes = 'marzo'
    elif mes == '04':
        mes = 'abril'
    elif mes == '05':
        mes = 'mayo'
    elif mes == '06':
        mes = 'junio'
    elif mes == '07':
        mes = 'julio'
    elif mes == '08':
        mes = 'agosto'
    elif mes == '09':
        mes = 'septiembre'
    elif mes == '10':
        mes = 'octubre'
    elif mes == '11':
        mes = 'noviembre'
    elif mes == '12':
        mes = 'diciembre'

    return dia,mes,año

def fecha(fecha):

    año = fecha[0:4] 
    mes = fecha[5:7]
    dia = fecha[8:10]

    if mes == '01':
        mes = 'enero'
    elif mes == '02':
        mes = 'febrero'
    elif mes == '03':
        mes = 'marzo'
    elif mes == '04':
        mes = 'abril'
    elif mes == '05':
        mes = 'mayo'
    elif mes == '06':
        mes = 'junio'
    elif mes == '07':
        mes = 'julio'
    elif mes == '08':
        mes = 'agosto'
    elif mes == '09':
        mes = 'septiembre'
    elif mes == '10':
        mes = 'octubre'
    elif mes == '11':
        mes = 'noviembre'
    elif mes == '12':
        mes = 'diciembre'

    return dia,mes,año

def formatoNombre(nombre: str) -> str:
   
    if not nombre:
        return ""

    return nombre.strip().lower().title()


# =========================
# CONTADOR ACTA (FOLIO) id=2
# =========================
CONTADOR_ACTA_ID = 2

def _ensure_contador_acta(conn):
    cur = conn.cursor()
    cur.execute("SELECT valor FROM contador WHERE id = ?", (CONTADOR_ACTA_ID,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO contador (id, valor) VALUES (?, ?)", (CONTADOR_ACTA_ID, 1))
        conn.commit()

def obtener_folio_acta() -> int:
    conn = sqlite3.connect(direccionBase)
    cur = conn.cursor()
    _ensure_contador_acta(conn)
    cur.execute("SELECT valor FROM contador WHERE id = ?", (CONTADOR_ACTA_ID,))
    val = cur.fetchone()[0]
    conn.close()
    return int(val)

def actualizar_folio_acta(nuevo_valor: int) -> int:
    if not isinstance(nuevo_valor, int) or nuevo_valor < 1:
        raise ValueError("Valor inválido")
    conn = sqlite3.connect(direccionBase)
    cur = conn.cursor()
    _ensure_contador_acta(conn)
    cur.execute("UPDATE contador SET valor = ? WHERE id = ?", (nuevo_valor, CONTADOR_ACTA_ID))
    conn.commit()
    conn.close()
    return nuevo_valor

def incrementar_folio_acta() -> int:
    # Incremento atómico (evita carreras si 2 usuarios generan a la vez)
    conn = sqlite3.connect(direccionBase)
    cur = conn.cursor()
    _ensure_contador_acta(conn)
    cur.execute("BEGIN IMMEDIATE")
    cur.execute("SELECT valor FROM contador WHERE id = ?", (CONTADOR_ACTA_ID,))
    actual = int(cur.fetchone()[0])
    nuevo = actual + 1
    cur.execute("UPDATE contador SET valor = ? WHERE id = ?", (nuevo, CONTADOR_ACTA_ID))
    conn.commit()
    conn.close()
    return nuevo

def folio_3_digitos(n: int) -> str:
    return str(int(n)).zfill(3)

def limpiar_texto(texto):
    if not texto:
        return ""
        
    return (texto
            .replace("–", "-")
            .replace("—", "-")
            .replace("“", '"')
            .replace("”", '"')
            .replace("’", "'")
            .replace("á","a")
            .replace("é","e")
            .replace("í","i")
            .replace("ó","o")
            .replace("ú","u")
            )

#################################################################################################################################
@candidatura_bp.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect(url_for("index"))

    roles = session.get("roles", [])
    permissions = session.get("permissions", [])
    open_mode = request.args.get("open")

    # superadmin/admin pasan siempre
    if "superadmin" in roles or "admin" in roles:
        return render_template("candidatura.html")

    # si viene desde captura
    if open_mode == "capturar":
        if "captura_candidatura" not in permissions:
            return redirect(url_for("home"))
    else:
        # acceso normal desde menú principal
        if "candidatura" not in permissions:
            return redirect(url_for("home"))

    return render_template("candidatura.html")

@candidatura_bp.route("/consultar", methods=["POST"])
def consultar():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Sesión expirada. Inicia sesión de nuevo."}), 401

    num = (request.form.get("numeroDeCuenta") or "").strip()

    if not num.isdigit() or len(num) != 9:
        return jsonify({"success": False, "error": "Número de cuenta inválido (deben ser 9 dígitos)."}), 400

    fila = obtenerDatosCandidatura(num)

    if not fila:
        return jsonify({"success": False, "error": "No se encontró ese número de cuenta."}), 404

    # ejemplo: fila[2] es nombreCompleto según tu SELECT
    nombre = fila[1]

    # Aquí todavía NO generas PDF (o sí, cuando quieras).
    return jsonify({
        "success": True,
        "numeroCuenta": num,
        "nombre": nombre
        # "pdf_url": "/candidatura/ver_pdf/DocumentoCandidatura.pdf"  # cuando lo tengas
    })

@candidatura_bp.route("/generar_pdf", methods=["POST"])
def generar_pdf():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "error": "Sesión expirada."}), 401

        num = (request.form.get("numeroDeCuenta") or "").strip()
        tipo = (request.form.get("tipo") or "").strip().lower()

        if not num.isdigit() or len(num) != 9:
            return jsonify({"success": False, "error": "Número de cuenta inválido."}), 400

        fila = obtenerDatosCandidatura(num)
        if not fila:
            return jsonify({"success": False, "error": "No existe ese número de cuenta."}), 404

        pdf = FPDF(orientation='P', unit='mm', format='letter')

        if tipo == "acta":
            folio_actual = obtener_folio_acta()
            # pásalo al PDF (ver punto 4)
            filename = generar_acta_candidatura(pdf, fila, "Doctorado", folio_actual)
            incrementar_folio_acta()
        else:
            filename = generar_citatorio_candidatura(pdf, fila, "Doctorado")
    
        return jsonify({"success": True, "pdf_url": f"/candidatura/ver_pdf/" + filename})

    except Exception as e:
        # Esto evita el error HTML que te tronaba el JSON
        return jsonify({"success": False, "error": f"Error al generar PDF: {str(e)}"}), 500 

@candidatura_bp.route("/ver_pdf/<filename>")
def ver_pdf(filename):
    return send_from_directory("static/Documentos", filename, mimetype="application/pdf", as_attachment=False)

@candidatura_bp.route("/api/obtener")
def obtener_por_cuenta():
    num = request.args.get("numero_cuenta","").strip()
    conn = sqlite3.connect(direccionBase)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidatura WHERE numero_cuenta = ?", (num,))
    row = cur.fetchone()
    conn.close()
    return jsonify(dict(row) if row else {})

@candidatura_bp.route("/api/actualizar", methods=["POST"])
def actualizar_por_cuenta():
    data = request.get_json(force=True)
    conn = sqlite3.connect(direccionBase)
    cur = conn.cursor()
    cur.execute("""
      UPDATE candidatura SET
        nombre_completo=?, especialidad=?, titulo_proyecto=?, semestre_ingreso=?,
        semestre_presentado=?, evaluacion=?, presidente=?, secretario=?,
        vocal1=?, vocal2=?, vocal3=?, sexo=?, modalidad_sede=?,
        fecha_examen=?, hora_examen=?
      WHERE numero_cuenta=?
    """, (
      data["nombre_completo"], data["especialidad"], data["titulo_proyecto"],
      data["semestre_ingreso"], data["semestre_presentado"], data["evaluacion"],
      data["presidente"], data["secretario"], data["vocal1"], data["vocal2"],
      data["vocal3"], data["sexo"], data["modalidad_sede"],
      data["fecha_examen"], data["hora_examen"],
      data["numero_cuenta"]
    ))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@candidatura_bp.route("/api/crear", methods=["POST"])
def crear_registro():
    data = request.get_json(force=True)

    # validación mínima
    numero_cuenta = (data.get("numero_cuenta") or "").strip()
    if not numero_cuenta.isdigit() or len(numero_cuenta) != 9:
        return jsonify({"ok": False, "error": "Número de cuenta inválido (9 dígitos)."}), 400

    try:
        conn = sqlite3.connect(direccionBase)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO candidatura (
                nombre_completo, numero_cuenta, especialidad, titulo_proyecto,
                semestre_ingreso, semestre_presentado, evaluacion,
                presidente, secretario, vocal1, vocal2, vocal3,
                sexo, modalidad_sede, fecha_examen, hora_examen
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("nombre_completo","").strip(),
            numero_cuenta,
            data.get("especialidad","").strip(),
            data.get("titulo_proyecto","").strip(),
            data.get("semestre_ingreso","").strip(),
            data.get("semestre_presentado","").strip(),
            data.get("evaluacion","").strip(),
            data.get("presidente","").strip(),
            data.get("secretario","").strip(),
            data.get("vocal1","").strip(),
            data.get("vocal2","").strip(),
            data.get("vocal3","").strip(),
            data.get("sexo","").strip(),
            data.get("modalidad_sede","").strip(),
            data.get("fecha_examen","").strip(),
            data.get("hora_examen","").strip()
        ))

        conn.commit()
        conn.close()
        return jsonify({"ok": True})

    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "error": "Ese número de cuenta ya existe."}), 409
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@candidatura_bp.route("/api/buscar")
def buscar_por_nombre():
    nombre = (request.args.get("nombre") or "").strip()

    if not nombre:
        return jsonify([])

    conn = sqlite3.connect(direccionBase)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Buscar por nombre (LIKE) - trae varios
    cur.execute("""
        SELECT id, nombre_completo, numero_cuenta
        FROM candidatura
        WHERE nombre_completo LIKE ?
        ORDER BY nombre_completo ASC
        LIMIT 20
    """, (f"%{nombre}%",))

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])

@candidatura_bp.route("/obtener_folio_acta", methods=["GET"])
def obtener_folio_acta_api():
    try:
        folio = obtener_folio_acta()
        return jsonify({"folio": folio})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@candidatura_bp.route("/actualizar_folio_acta", methods=["POST"])
def actualizar_folio_acta_api():
    try:
        nuevo = request.json.get("nuevoFolio")
        if not isinstance(nuevo, int) or nuevo < 1:
            return jsonify({"success": False, "error": "Valor inválido"}), 400

        folio = actualizar_folio_acta(nuevo)
        return jsonify({"success": True, "folio": folio})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

