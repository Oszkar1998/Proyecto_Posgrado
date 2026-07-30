# Libreria Necesaria para conectar PYTHON con HTMLX, y con la Base de Datos
from flask import Blueprint , render_template, request, jsonify, session, redirect, url_for, send_from_directory
from datetime import datetime
from fpdf import FPDF
from auth import permission_required
from config import direccionBase, direccionImagen,direccionPDF
from db import get_connection

dgae_bp = Blueprint('dgae', __name__, template_folder='../templates')

############################## FUNCIONES NORMALES SIN HTML ##############################
def especialidad(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, opcion,tipo, modalidad):
    
    programa="PROGRAMA UNICO DE ESPECIALIZACIONES DE INGENIERIA"
    grado="Especialización"
    gradoAux = "ESPECIALIZACIÓN EN "

    if opcion=="1":
        documentoUnaHoja(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, modalidad, gradoAux)
    elif opcion=="2":
        documentoDosHojas(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, tipo, modalidad, gradoAux)
    else:
        raise ValueError("No se encontró una opción válida para generar el documento.")

def maestria(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, opcion,tipo, modalidad):
    
    programa="PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
    grado="Maestría"
    gradoAux = "MAESTRÍA EN "

    if opcion=="1":
        documentoUnaHoja(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, modalidad, gradoAux)
    elif opcion=="2":
        documentoDosHojas(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, tipo, modalidad, gradoAux)
    else:
        raise ValueError("No se encontró una opción válida para generar el documento.")

def doctorado(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, opcion,tipo, modalidad):
    
    programa="PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
    grado="Doctorado"
    gradoAux = "DOCTORADO EN "
    
    if opcion=="1":
        documentoDOC_UnaHoja(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, gradoAux) 
    elif opcion=="2":
        documentoDOC_DosHojas(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, gradoAux, tipo) 
    else:
        raise ValueError("No se encontró una opción válida para generar el documento.")


########## DOCUMENTOS ##########
def documentoUnaHoja(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, modalidad, gradoAux):
    dia, mes, año = fecha()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # ========= Encabezado =========
    pdf.image(direccionImagen+"UNAM_SinTexto.jpeg", x=12, y=10, w=14, h=15)
    pdf.image(direccionImagen+"LogoDGAE.PNG", x=182, y=16.5, w=18.5, h=9)
    pdf.image(direccionImagen+"Nacion.PNG", x=182, y=255, w=14.5, h=13)
    pdf.set_line_width(0.05)
    pdf.line(10, 27, 200, 27)
    pdf.set_xy(12,10); pdf.set_font("Arial", size=8)
    pdf.multi_cell(185, 4, "Universidad Nacional Autónoma de México", align="C")
    pdf.set_xy(12,14); pdf.multi_cell(185, 4, "Secretaría General", align="C")
    pdf.set_xy(12,18); pdf.multi_cell(185, 4, "Dirección General de Administración Escolar", align="C")
    pdf.set_xy(12,22); pdf.multi_cell(185, 4, "Dirección de Certificación y Control Documental", align="C")
    pdf.set_xy(5,28);  pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(200, 5, f"Relación de documentos para Autorización de Exámenes de Grado ({grado})", align="C")
    pdf.set_line_width(1); pdf.line(10, 34, 200, 34)

    # ===== Caja de datos (dinámica, como en la versión corregida) =====
    # Constantes de columnas
    X_L = 10.0
    X_ETQ = 49.3
    X_PLAN_FIN = 161
    X_CLAVE_ETQ = 161
    X_CLAVE_VAL = 172.5
    X_R = 200.0

    y_top = 36.0
    pdf.set_line_width(0.10)
    pdf.line(X_L, y_top, X_R, y_top)  # línea superior de la caja

    # Fila 1: Programa (altura fija)
    y_prog_top = y_top
    y_prog_bot = y_prog_top + 4.5
    pdf.set_xy(X_L, y_prog_top);       pdf.set_font("Arial", size=8.5); pdf.multi_cell(45, 5, "Programa:", align="J")
    pdf.set_xy(X_ETQ+1.2, y_prog_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(95, 5, programa, align="J")
    pdf.line(X_L, y_prog_bot, X_R, y_prog_bot)

    # Fila 2: Plan de estudios + Clave (altura variable)
    y_plan_top = y_prog_bot
    pdf.set_xy(X_L, y_plan_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(45, 5, "Plan de estudios:", align="J")

    pdf.set_xy(X_ETQ+1.2, y_plan_top); pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(X_PLAN_FIN - (X_ETQ+1.2) - 1, 5, gradoAux + Plan_estudios, align="J")
    y_plan_text_bot = pdf.get_y()

    pdf.set_xy(X_CLAVE_ETQ-0.5, y_plan_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(15, 5, "Clave:", align="J")
    pdf.set_xy(X_CLAVE_VAL,     y_plan_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(25, 5, clave_str, align="J")

    y_plan_bot = max(y_plan_text_bot, y_plan_top + 4.5)
    pdf.line(X_L, y_plan_bot, X_R, y_plan_bot)

    # Fila 3: Nombre + Cuenta
    y_nom_top = y_plan_bot
    pdf.set_xy(X_L, y_nom_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(45, 5, "Nombre de la o del alumno:", align="J")

    pdf.set_xy(X_ETQ+1.2, y_nom_top); pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(X_PLAN_FIN - (X_ETQ+1.2) - 1, 5.3, Nomb_alu, align="J")
    y_nom_text_bot = pdf.get_y()

    pdf.set_xy(X_CLAVE_ETQ-0.5, y_nom_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(15, 5, "Cuenta:", align="J")
    pdf.set_xy(X_CLAVE_VAL,     y_nom_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(25, 5, No_cuenta_str, align="J")

    y_nom_bot = max(y_nom_text_bot, y_nom_top + 5.0)

    # Verticales de la caja
    pdf.line(X_L,          y_top,      X_L,          y_nom_bot)
    pdf.line(X_R,          y_top,      X_R,          y_nom_bot)
    pdf.line(X_ETQ,        y_top,      X_ETQ,        y_nom_bot)
    pdf.line(X_CLAVE_ETQ,  y_plan_top, X_CLAVE_ETQ,  y_nom_bot)
    pdf.line(X_CLAVE_VAL,  y_plan_top, X_CLAVE_VAL,  y_nom_bot)

    # Base de caja
    pdf.line(X_L, y_nom_bot, X_R, y_nom_bot)

    # Título siguiente, ajustado a la altura real
    pdf.set_xy(12, y_nom_bot - 0.5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(185, 5, "Alumnado con antecedente UNAM en el ciclo anterior inmediato", align="C")

    # ========= De aquí hacia abajo con tu maquetado original =========
    # Líneas verticales/horizontales de la gran caja de documentos
    pdf.set_line_width(0.1)
    pdf.line(10, 203, 10, 59.5)
    pdf.line(200, 203, 200, 59.5)
    pdf.line(18.5, 174, 18.5, 59.5)
    pdf.line(157, 174, 157, 59.5)
    pdf.line(163, 174, 163, 65)
    pdf.line(187, 174, 187, 59.5)

    pdf.line(18.5, 203, 18.5, 182)
    pdf.line(157, 203, 157, 182)
    pdf.line(163, 203, 163, 182)
    pdf.line(187, 203, 187, 182)

    pdf.line(10, 59.5, 200, 59.5)
    pdf.line(157, 65, 200, 65)
    pdf.line(10, 73, 200, 73)
    pdf.line(10, 78.5, 200, 78.5)
    pdf.line(10, 89, 200, 89)
    pdf.line(10, 94, 200, 94)
    pdf.line(10, 99, 200, 99)
    pdf.line(10, 109, 200, 109)
    pdf.line(10, 114, 200, 114)
    pdf.line(10, 124, 200, 124)
    pdf.line(10, 129, 200, 129)
    pdf.line(10, 134, 200, 134)
    pdf.line(10, 149, 200, 149)
    pdf.line(10, 159, 200, 159)
    pdf.line(10, 169, 200, 169)
    pdf.line(10, 174, 200, 174)
    pdf.line(10, 182, 200, 182)
    pdf.line(10, 187, 200, 187)
    pdf.line(10, 192, 200, 192)
    pdf.line(10, 203, 200, 203)

    # Caja observaciones
    pdf.line(10, 222, 200, 222)
    pdf.line(10, 235, 200, 235)
    pdf.line(10, 235, 10, 222)
    pdf.line(200, 235, 200, 222)

    # Caja firmas
    pdf.line(10, 249, 180, 249)
    pdf.line(10, 253, 180, 253)
    pdf.line(10, 272.5, 180, 272.5)
    pdf.line(10, 276.5, 180, 276.5)
    pdf.line(10, 276.5, 10, 249)
    pdf.line(90, 276.5, 90, 249)
    pdf.line(180, 276.5, 180, 249)

    # Títulos de la tabla de documentos
    pdf.set_xy(10,64); pdf.set_font("Arial", size=6.5, style="B"); pdf.multi_cell(10, 5, "Núm.", align="J")
    pdf.set_xy(25,64); pdf.set_font("Arial", size=10, style="B"); pdf.multi_cell(130, 5, "Listado de documentos", align="C")
    pdf.set_xy(156,60.5); pdf.set_font("Arial", size=10, style="B"); pdf.multi_cell(35, 5, "Programa", align="C")
    pdf.set_xy(188,60.5); pdf.set_font("Arial", size=10, style="B"); pdf.multi_cell(15, 5, "DGAE", align="J")
    pdf.set_xy(155.5,66); pdf.set_font("Arial", size=7.5, style="B"); pdf.multi_cell(8, 5, "SI", align="C")
    pdf.set_xy(162,64.5); pdf.set_font("Arial", size=6.9, style="B"); pdf.multi_cell(25, 5, "No aplica", align="C")
    pdf.set_xy(162,66.9); pdf.multi_cell(25, 5, "conforme al Plan", align="C")
    pdf.set_xy(188,66); pdf.set_font("Arial", size=7.5, style="B"); pdf.multi_cell(12, 5, "Recibe", align="J")

    # (Resto de tu lista de documentos tal cual)
    pdf.set_font("Arial", size=9.5)
    pdf.set_xy(10,74);     pdf.multi_cell(8, 5, "1", align="C")
    pdf.set_xy(20,74);     pdf.multi_cell(130, 5, "Carta de aceptación o suficiencia académica", align="J")
    pdf.set_xy(156,74);    pdf.multi_cell(8, 5, "X", align="C")

    pdf.set_xy(10,81.5);   pdf.multi_cell(8, 5, "2", align="C")
    pdf.set_xy(156,81.5);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,79);     pdf.multi_cell(130, 5, "Constancia de idioma(s) (si es emitida por la UNAM, solo copia, en caso de ser de otra institución deberá ser original)*", align="J")

    pdf.set_xy(10,89);     pdf.multi_cell(8, 5, "3", align="C")
    pdf.set_xy(156,89);    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,89);     pdf.multi_cell(130, 5, "Oficio de prórroga", align="J")

    pdf.set_xy(10,94);     pdf.multi_cell(8, 5, "4", align="C")
    pdf.set_xy(156,94);    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,94);     pdf.multi_cell(130, 5, "Oficio de designación de jurado (tesis)", align="J")


    if modalidad == "Tesina" or modalidad == "Tesis" or modalidad == "Informe de Trabajo de Investigación":
        pdf.set_xy(10,101.5);  pdf.multi_cell(8, 5, "5", align="C")
        pdf.set_xy(156,101.5); pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,99);     pdf.multi_cell(130, 5, "Cinco votos (podrán ser digitales, siempre y cuando tengan el Vo. Bo. de la o del Coordinador)", align="J")
    else:
        pdf.set_xy(10,101.5);  pdf.multi_cell(8, 5, "5", align="C")
        pdf.set_xy(156,101.5); pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,99);     pdf.multi_cell(130, 5, "Cinco votos (podrán ser digitales, siempre y cuando tengan el Vo. Bo. de la o del Coordinador)", align="J")
    

    pdf.set_xy(10,109);    pdf.multi_cell(8, 5, "6", align="C")
    pdf.set_xy(156,109);   pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,109);    pdf.multi_cell(130, 5, "Hoja de actualización de datos", align="J")

    pdf.set_xy(10,117.5);  pdf.multi_cell(8, 5, "7", align="C")
    pdf.set_xy(156,117.5); pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,114);    pdf.multi_cell(130, 5, "Formato de Autorización de Transferencia de Información a la Dirección General de Profesiones de la Secretaría de Educación Pública (ATI)", align="J")

    pdf.set_xy(10,124);    pdf.multi_cell(8, 5, "8", align="C")
    pdf.set_xy(156,124);   pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,124);    pdf.multi_cell(130, 5, "Formato de no adeudo de bibliotecas", align="J")

    pdf.set_xy(10,129);    pdf.multi_cell(8, 5, "9", align="C")
    pdf.set_xy(156,129);   pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,129);    pdf.multi_cell(130, 5, "Formato de solicitud y elección de grado", align="J")

    pdf.set_xy(10,139);    pdf.multi_cell(8, 5, "10", align="C")
    pdf.set_xy(156,139);   pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,134);    pdf.multi_cell(130, 5, "Comprobante de pago por el tipo de grado y la situación documental (Se debe incluir la ficha referenciada que genera el sistema de pagos y el comprobante expedido por BANXICO, si fue pago digital, excepto para pagos en BBVA Bancomer)", align="J")

    pdf.set_xy(10,151.5);  pdf.multi_cell(8, 5, "11", align="C")
    pdf.set_xy(156,151.5); pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,149);    pdf.multi_cell(130, 5, "Cuatro (4) fotografías (de acuerdo con los requisitos específicos para el tipo de grado que la o el egresado solicitó)", align="J")

    pdf.set_xy(10,161.5);  pdf.multi_cell(8, 5, "12", align="C")
    pdf.set_xy(156,161.5); pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,159);    pdf.multi_cell(130, 5, "Protesta Universitaria de Integridad y Honestidad Académica y Profesional (con la firma original de la o del alumno)", align="J")

    if modalidad == "Tesina" or modalidad == "Tesis" or modalidad == "Informe de Trabajo de Investigación":
        pdf.set_xy(10,169);    pdf.multi_cell(8, 5, "13", align="C")
        pdf.set_xy(156,169);   pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,169);    pdf.multi_cell(130, 5, "Carta aval firmada por la tutora o el tutor (en caso de trabajo escrito)", align="J")
    else:
        pdf.set_xy(10,169);    pdf.multi_cell(8, 5, "13", align="C")
        pdf.set_xy(156,169);   pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,169);    pdf.multi_cell(130, 5, "Carta aval firmada por la tutora o el tutor (en caso de trabajo escrito)", align="J")

    pdf.set_xy(20,176);    pdf.set_font("Arial", size=8, style="B")
    pdf.multi_cell(130, 5, "Para exámenes de grado realizados a distancia:", align="J")
    pdf.set_font("Arial", size=9.5)

    pdf.set_xy(10,182);    pdf.multi_cell(8, 5, "14", align="C")
    pdf.set_xy(20,182);    pdf.multi_cell(130, 5, "Solicitud de la o del alumno para presentar exámenes de grado vía remota", align="J")

    pdf.set_xy(10,187);    pdf.multi_cell(8, 5, "15", align="C")
    pdf.set_xy(20,187);    pdf.multi_cell(130, 5, "Oficio de autorización para presentar examen de grado vía remota.", align="J")

    pdf.set_xy(10,195.5);  pdf.multi_cell(8, 5, "16", align="C")
    pdf.set_xy(20,193);    pdf.multi_cell(130, 5, "Carta de confidencialidad (firmada por cada integrante del sínodo, más la carta de la o del sustentante)", align="J")

    # Notas / Observaciones / Fechas / Firmas (igual que tenías)
    pdf.set_font("Arial", size=7, style="B")
    pdf.set_xy(10,205);   pdf.multi_cell(130, 5, "Notas:", align="J")
    pdf.set_font("Arial", size=7.5, style="B")
    pdf.set_xy(21.5,205); pdf.multi_cell(130, 5, "*En caso de que el programa de Posgrado haya recibido documentos de ingreso.", align="J")
    pdf.set_xy(21.5,209); pdf.multi_cell(176, 3, "La liberación de estudios la integrará la DGAE al expediente, para que con todos estos documentos se emita la Autorización de Examen, sin necesidad de realizar una doble entrega documental.", align="J")
    pdf.set_xy(21.5,214); pdf.multi_cell(176, 5, "Solo se aceptarán expedientes completos, es decir, que contengan TODOS los documentos en el orden en que aparecen en el listado.", align="J")

    pdf.set_xy(11,222);   pdf.set_font("Arial", size=8.5, style="B"); pdf.multi_cell(180, 5, "Observaciones:", align="J")
    pdf.set_xy(11,226);   pdf.multi_cell(180, 5, "", align="J")

    pdf.set_xy(11,237);   pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(180, 5, f"Ciudad Universitaria, Cd. Mx., a {dia} de {mes} de {año}", align="J")

    pdf.set_xy(11,248.5); pdf.set_font("Arial", size=8.5, style="B"); pdf.multi_cell(69, 5, "Entrega", align="C")
    pdf.set_xy(91,248.5); pdf.multi_cell(69, 5, "                  Recibe", align="C")

    pdf.set_xy(11,268);   pdf.set_font("Arial", size=8.5); pdf.multi_cell(69, 5, "M.I. BRISIA JON SERRANO", align="C")
    pdf.set_xy(11,271.8); pdf.multi_cell(69, 5, "Nombre, cargo y firma", align="C")
    pdf.set_xy(120,271.8); pdf.multi_cell(90, 5, "Nombre, cargo y firma", align="J")

    pdf.set_font("Arial", size=6.5)
    pdf.set_xy(180,268);  pdf.multi_cell(18, 5, "Rev.", align="C")
    pdf.set_xy(180,271.5);pdf.multi_cell(18, 5, "Octubre_2024", align="J")

    pdf.output(direccionPDF+"DocumentoDGAE.pdf", "F")

def documentoDosHojas(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, tipo, modalidad, gradoAux):
    dia, mes, año = fecha()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # ========= Encabezado =========
    pdf.image(direccionImagen+"UNAM_SinTexto.jpeg", x=12, y=10, w=14, h=15)
    pdf.image(direccionImagen+"LogoDGAE.PNG", x=182, y=16.5, w=18.5, h=9)
    pdf.image(direccionImagen+"Nacion.PNG", x=175, y=261.5, w=15.9, h=14)
    pdf.set_line_width(0.05)
    pdf.line(10, 27, 200, 27)
    pdf.set_xy(12,10); pdf.set_font("Arial", size=8)
    pdf.multi_cell(185, 4, "Universidad Nacional Autónoma de México", align="C")
    pdf.set_xy(12,14); pdf.multi_cell(185, 4, "Secretaría General", align="C")
    pdf.set_xy(12,18); pdf.multi_cell(185, 4, "Dirección General de Administración Escolar", align="C")
    pdf.set_xy(12,22); pdf.multi_cell(185, 4, "Dirección de Certificación y Control Documental", align="C")
    pdf.set_xy(10,28); pdf.set_font("Arial", "B", 12.2)
    pdf.multi_cell(185, 5, f"Relación de documentos para Autorización de Exámenes de Grado ({grado})", align="C")
    pdf.set_line_width(1); pdf.line(10, 34, 200, 34)

    # ===== Caja de datos (dinámica) =====
    # Columnas
    X_L = 10.0           # borde izq
    X_ETQ = 49.3         # fin de etiquetas
    X_PLAN_FIN = 161     # antes de "Clave:"
    X_CLAVE_ETQ = 161
    X_CLAVE_VAL = 172.5
    X_R = 200.0          # borde der

    y_top = 36.0
    pdf.set_line_width(0.10)
    pdf.line(X_L, y_top, X_R, y_top)  # línea superior

    # Fila 1: Programa (altura fija)
    y_prog_top = y_top
    y_prog_bot = y_prog_top + 4.5
    pdf.set_xy(X_L, y_prog_top);       pdf.set_font("Arial", size=8.5); pdf.multi_cell(45, 5, "Programa:", align="J")
    pdf.set_xy(X_ETQ+1.2, y_prog_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(95, 5, programa, align="J")
    pdf.line(X_L, y_prog_bot, X_R, y_prog_bot)

    # Fila 2: Plan de estudios + Clave (altura variable)
    y_plan_top = y_prog_bot
    pdf.set_xy(X_L, y_plan_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(45, 5, "Plan de estudios:", align="J")

    pdf.set_xy(X_ETQ+1.2, y_plan_top); pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(X_PLAN_FIN - (X_ETQ+1.2) - 1, 5, gradoAux + Plan_estudios, align="J")
    y_plan_text_bot = pdf.get_y()

    pdf.set_xy(X_CLAVE_ETQ-0.5, y_plan_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(15, 5, "Clave:", align="J")
    pdf.set_xy(X_CLAVE_VAL,     y_plan_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(25, 5, clave_str, align="J")

    y_plan_bot = max(y_plan_text_bot, y_plan_top + 4.5)
    pdf.line(X_L, y_plan_bot, X_R, y_plan_bot)

    # Fila 3: Nombre + Cuenta (debajo del plan)
    y_nom_top = y_plan_bot
    pdf.set_xy(X_L, y_nom_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(45, 5, "Nombre de la o del alumno:", align="J")

    pdf.set_xy(X_ETQ+1.2, y_nom_top); pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(X_PLAN_FIN - (X_ETQ+1.2) - 1, 5.3, Nomb_alu, align="J")
    y_nom_text_bot = pdf.get_y()

    pdf.set_xy(X_CLAVE_ETQ-0.5, y_nom_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(15, 5, "Cuenta:", align="J")
    pdf.set_xy(X_CLAVE_VAL,     y_nom_top); pdf.set_font("Arial", size=8.5); pdf.multi_cell(25, 5, No_cuenta_str, align="J")

    y_nom_bot = max(y_nom_text_bot, y_nom_top + 5.0)

    # Verticales de la caja
    pdf.line(X_L,          y_top,      X_L,          y_nom_bot)
    pdf.line(X_R,          y_top,      X_R,          y_nom_bot)
    pdf.line(X_ETQ,        y_top,      X_ETQ,        y_nom_bot)
    pdf.line(X_CLAVE_ETQ,  y_plan_top, X_CLAVE_ETQ,  y_nom_bot)
    pdf.line(X_CLAVE_VAL,  y_plan_top, X_CLAVE_VAL,  y_nom_bot)
    # Base de la caja
    pdf.line(X_L, y_nom_bot, X_R, y_nom_bot)

    # Título siguiente (ajustado a la altura real)
    pdf.set_xy(12, y_nom_bot - 0.5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(185, 5, "Alumnado sin antecedente UNAM en el ciclo anterior inmediato", align="C")

    # ======= De aquí en adelante tu maquetado original =======
    # Caja de datos ,lineas verticales
    pdf.set_line_width(0.1)
    pdf.line(10, 242, 10, 59.5)
    pdf.line(200, 242, 200, 59.5)
    pdf.line(18.5, 217, 18.5, 59.5)
    pdf.line(157, 217, 157, 59.5)
    pdf.line(163, 217, 163, 65)
    pdf.line(187, 217, 187, 59.5)
    pdf.line(18.5, 242, 18.5, 222)
    pdf.line(157, 242, 157, 222)
    pdf.line(163, 242, 163, 222)
    pdf.line(187, 242, 187, 222)
    # líneas horizontales de documentos
    pdf.line(10, 59.5, 200, 59.5)
    pdf.line(157, 65, 200, 65)
    pdf.line(10, 73, 200, 73)
    pdf.line(10, 82, 200, 82)
    pdf.line(10, 87, 200, 87)
    pdf.line(10, 97, 200, 97)
    pdf.line(10, 115.5, 200, 115.5)
    pdf.line(10, 127, 200, 127)
    pdf.line(10, 132, 200, 132)
    pdf.line(10, 137, 200, 137)
    pdf.line(10, 142, 200, 142)
    pdf.line(10, 152, 200, 152)
    pdf.line(10, 157, 200, 157)
    pdf.line(10, 167, 200, 167)
    pdf.line(10, 172, 200, 172)
    pdf.line(10, 177, 200, 177)
    pdf.line(10, 192, 200, 192)
    pdf.line(10, 202, 200, 202)
    pdf.line(10, 212, 200, 212)
    pdf.line(10, 217, 200, 217)
    pdf.line(10, 222, 200, 222)
    pdf.line(10, 227, 200, 227)
    pdf.line(10, 232, 200, 232)
    pdf.line(10, 242, 200, 242)

    # Encabezados de la tabla
    pdf.set_xy(10,64);   pdf.set_font("Arial", size=6.5, style="B"); pdf.multi_cell(10, 5, "Núm.", align="J")
    pdf.set_xy(25,64);   pdf.set_font("Arial", size=10, style="B");  pdf.multi_cell(130, 5, "Listado de documentos", align="C")
    pdf.set_xy(156,60.5);pdf.set_font("Arial", size=10, style="B");  pdf.multi_cell(35, 5, "Programa", align="C")
    pdf.set_xy(188,60.5);pdf.set_font("Arial", size=10, style="B");  pdf.multi_cell(15, 5, "DGAE", align="J")
    pdf.set_xy(155.5,66);pdf.set_font("Arial", size=7.5, style="B"); pdf.multi_cell(8, 5, "SI", align="C")
    pdf.set_xy(162,64.5);pdf.set_font("Arial", size=6.9, style="B"); pdf.multi_cell(25, 5, "No aplica", align="C")
    pdf.set_xy(162,66.9);                                  pdf.multi_cell(25, 5, "conforme al Plan", align="C")
    pdf.set_xy(188,66);  pdf.set_font("Arial", size=7.5, style="B"); pdf.multi_cell(12, 5, "Recibe", align="J")

    # ===== Listado (sin antecedentes / con antecedentes) =====
    if tipo == "1":
        pdf.set_font("Arial", size=9.5)
        pdf.set_xy(10,75.8); pdf.multi_cell(8, 5, "1", align="C")
        pdf.set_xy(20,73.8); pdf.multi_cell(130, 5, "Acta de nacimiento original", align="J")
        pdf.set_xy(20,78);   pdf.multi_cell(130, 4, "(para extranjeros apostillada o legalizada y, en su caso, traducida)*", align="J")
        pdf.set_xy(156,74);  pdf.multi_cell(8, 5, "", align="C")

        pdf.set_xy(10,82);   pdf.multi_cell(8, 5, "2", align="C")
        pdf.set_xy(156,82);  pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,82);   pdf.multi_cell(130, 5, "CURP*", align="J")

        pdf.set_xy(10,89.5); pdf.multi_cell(8, 5, "3", align="C")
        pdf.set_xy(156,89.5);pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,87);   pdf.multi_cell(130, 5, "Título de licenciatura (copia con el sello de cotejado por el Programa) ", align="J")
        pdf.set_xy(20,92);   pdf.multi_cell(130, 5, "(Para extranjeros, apostillado o legalizado y, en su caso, traducido)*", align="J")

        pdf.set_xy(10,104.5);pdf.multi_cell(8, 5, "4", align="C")
        pdf.set_xy(156,104.5);pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,97);   pdf.multi_cell(135, 4.5, "Certificado de estudios de licenciatura (Si el certificado no tiene promedio, se deberá anexar la constancia de promedio correspondiente, (para estudios en el extranjero apostillado o legalizado y, en su caso, traducido y equivalencia de promedio emitido por la DGIRE, todo en original)*", align="J")
    elif tipo == "2":
        pdf.set_font("Arial", size=9.5)
        pdf.set_xy(10,75.8); pdf.multi_cell(8, 5, "1", align="C")
        pdf.set_xy(20,73.8); pdf.multi_cell(130, 5, "Acta de nacimiento original", align="J")
        pdf.set_xy(20,78);   pdf.multi_cell(130, 4, "(para extranjeros apostillada o legalizada y, en su caso, traducida)*", align="J")
        pdf.set_xy(156,74);  pdf.multi_cell(8, 5, "X", align="C")

        pdf.set_xy(10,82);   pdf.multi_cell(8, 5, "2", align="C")
        pdf.set_xy(156,82);  pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,82);   pdf.multi_cell(130, 5, "CURP*", align="J")

        pdf.set_xy(10,89.5); pdf.multi_cell(8, 5, "3", align="C")
        pdf.set_xy(156,89.5);pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,87);   pdf.multi_cell(130, 5, "Título de licenciatura (copia con el sello de cotejado por el Programa) ", align="J")
        pdf.set_xy(20,92);   pdf.multi_cell(130, 5, "(Para extranjeros, apostillado o legalizado y, en su caso, traducido)*", align="J")

        pdf.set_xy(10,104.5);pdf.multi_cell(8, 5, "4", align="C")
        pdf.set_xy(156,104.5);pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,97);   pdf.multi_cell(135, 4.5, "Certificado de estudios de licenciatura (Si el certificado no tiene promedio, se deberá anexar la constancia de promedio correspondiente, (para estudios en el extranjero apostillado o legalizado y, en su caso, traducido y equivalencia de promedio emitido por la DGIRE, todo en original)*", align="J")

    # Resto del listado (común)
    pdf.set_xy(10,119.5); pdf.multi_cell(8, 5, "5", align="C")
    pdf.set_xy(156,119.5);pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,117);   pdf.multi_cell(135, 5, "Constancia de idioma(s) (si es emitida por la UNAM, solo copia, en caso de ser de otra institución deberá ser original)*", align="J")

    pdf.set_xy(10,127);   pdf.multi_cell(8, 5, "6", align="C")
    pdf.set_xy(156,127);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,127);   pdf.multi_cell(135, 5, "Carta de aceptación o suficiencia académica", align="J")

    pdf.set_xy(10,132);   pdf.multi_cell(8, 5, "7", align="C")
    pdf.set_xy(156,132);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,132);   pdf.multi_cell(135, 5, "Oficio de prórroga", align="J")

    pdf.set_xy(10,137);   pdf.multi_cell(8, 5, "8", align="C")
    pdf.set_xy(156,137);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,137);   pdf.multi_cell(135, 5, "Oficio de designación de jurado (tesis)", align="J")

    if modalidad == "Tesina" or modalidad == "Tesis" or modalidad == "Informe de Trabajo de Investigación":
        pdf.set_xy(10,144.5); pdf.multi_cell(8, 5, "9", align="C")
        pdf.set_xy(156,142);  pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,144.5); pdf.multi_cell(135, 3.5, "Cinco votos (podrán ser digitales, siempre y cuando tengan el Vo. Bo. de la o del Coordinador)", align="J")
    else:
        pdf.set_xy(10,144.5); pdf.multi_cell(8, 5, "9", align="C")
        pdf.set_xy(156,142);  pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,144.5); pdf.multi_cell(135, 3.5, "Cinco votos (podrán ser digitales, siempre y cuando tengan el Vo. Bo. de la o del Coordinador)", align="J")

    pdf.set_xy(10,152);   pdf.multi_cell(8, 5, "10", align="C")
    pdf.set_xy(156,152);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,152);   pdf.multi_cell(135, 5, "Hoja de actualización de datos", align="J")

    pdf.set_xy(10,159);   pdf.multi_cell(8, 5, "11", align="C")
    pdf.set_xy(156,159);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,157);   pdf.multi_cell(135, 4, "Formato de Autorización de Transferencia de Información a la Dirección General de Profesiones de la Secretaría de Educación Pública (ATI)", align="J")

    pdf.set_xy(10,167);   pdf.multi_cell(8, 5, "12", align="C")
    pdf.set_xy(156,167);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,167);   pdf.multi_cell(135, 5, "Formato de no adeudo de bibliotecas", align="J")

    pdf.set_xy(10,172);   pdf.multi_cell(8, 5, "13", align="C")
    pdf.set_xy(156,172);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,172);   pdf.multi_cell(135, 5, "Formato de solicitud y elección de grado", align="J")

    pdf.set_xy(10,182);   pdf.multi_cell(8, 5, "14", align="C")
    pdf.set_xy(156,182);  pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,177);   pdf.multi_cell(135, 5, "Comprobante de pago por el tipo de grado y la situación documental (Se debe incluir la ficha referenciada que genera el sistema de pagos y el comprobante expedido por BANXICO, si fue pago digital, excepto para pagos en BBVA Bancomer)", align="J")

    pdf.set_xy(10,194.5); pdf.multi_cell(8, 5, "15", align="C")
    pdf.set_xy(156,194.5);pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,192);   pdf.multi_cell(135, 5, "Cuatro (4) fotografías (de acuerdo con los requisitos específicos para el tipo de grado que la o el egresado solicitó)", align="J")

    pdf.set_xy(10,204.5); pdf.multi_cell(8, 5, "16", align="C")
    pdf.set_xy(156,204.5);pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,202);   pdf.multi_cell(135, 5, "Protesta Universitaria de Integridad y Honestidad Académica y Profesional (con la firma original de la o del alumno)", align="J")
    
    if modalidad == "Tesina" or modalidad == "Tesis" or modalidad == "Informe de Trabajo de Investigación":
        pdf.set_xy(10,212);   pdf.multi_cell(8, 5, "17", align="C")
        pdf.set_xy(156,212);  pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,212);   pdf.multi_cell(135, 5, "Carta aval firmada por la tutora o el tutor (en caso de trabajo escrito)", align="J")
    else:
        pdf.set_xy(10,212);   pdf.multi_cell(8, 5, "17", align="C")
        pdf.set_xy(156,212);  pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,212);   pdf.multi_cell(135, 5, "Carta aval firmada por la tutora o el tutor (en caso de trabajo escrito)", align="J")

    pdf.set_xy(20,217);   pdf.set_font("Arial", size=8, style="B")
    pdf.multi_cell(130, 5, "Para exámenes de grado realizados a distancia:", align="J")
    pdf.set_font("Arial", size=9.5)

    pdf.set_xy(10,222);   pdf.multi_cell(8, 5, "18", align="C")
    pdf.set_xy(20,222);   pdf.multi_cell(135, 5, "Solicitud de la o del alumno para presentar exámenes de grado vía remota", align="J")

    pdf.set_xy(10,227);   pdf.multi_cell(8, 5, "19", align="C")
    pdf.set_xy(20,227);   pdf.multi_cell(135, 5, "Oficio de autorización para presentar examen de grado vía remota.", align="J")

    pdf.set_xy(10,234.5); pdf.multi_cell(8, 5, "20", align="C")
    pdf.set_xy(20,232);   pdf.multi_cell(135, 5, "Carta de confidencialidad (firmada por cada integrante del sínodo, más la carta de la o del sustentante)", align="J")

    pdf.set_font("Arial", size=6.5)
    pdf.set_xy(148,271.5); pdf.multi_cell(32, 5, "Rev. Octubre_2024", align="J")

    # ================== Segunda página ==================
    pdf.add_page()
    pdf.image(direccionImagen+"UNAM_SinTexto.jpeg", x=12, y=10, w=14, h=15)
    pdf.image(direccionImagen+"LogoDGAE.PNG", x=182, y=16.5, w=18.5, h=9)
    pdf.image(direccionImagen+"Nacion.PNG", x=175, y=261.5, w=15.9, h=14)
    pdf.set_line_width(0.05)
    pdf.line(10, 27, 200, 27)
    pdf.set_xy(12,10); pdf.set_font("Arial", size=8)
    pdf.multi_cell(185, 4, "Universidad Nacional Autónoma de México", align="C")
    pdf.set_xy(12,14); pdf.multi_cell(185, 4, "Secretaría General", align="C")
    pdf.set_xy(12,18); pdf.multi_cell(185, 4, "Dirección General de Administración Escolar", align="C")
    pdf.set_xy(12,22); pdf.multi_cell(185, 4, "Dirección de Certificación y Control Documental", align="C")
    pdf.set_xy(10,28); pdf.set_font("Arial", "B", 12.2)
    pdf.multi_cell(185, 5, f"Relación de documentos para Autorización de Exámenes de Grado ({grado})", align="C")
    pdf.set_line_width(1); pdf.line(10, 34, 200, 34)

    pdf.set_xy(10,37); pdf.set_font("Arial", size=8, style="B");   pdf.multi_cell(130, 5, "Notas:", align="J")
    pdf.set_xy(10,44); pdf.set_font("Arial", size=8.5, style="B"); pdf.multi_cell(200, 4, "*En caso de que el programa de Posgrado haya recibido documentos de ingreso.", align="J")
    pdf.set_xy(10,49);                                       pdf.multi_cell(190, 4, "La liberación de estudios la integrará la DGAE al expediente, para que con todos estos documentos se emita la Autorización de Examen, sin necesidad de realizar una doble entrega documental.", align="J")
    pdf.set_xy(10,59);                                       pdf.multi_cell(190, 4, "Solo se aceptarán expedientes completos, es decir, que contengan TODOS los documentos en el orden en que aparecen en el listado.", align="J")

    # Observaciones
    pdf.set_xy(10,72); pdf.set_font("Arial", size=8.5, style="B"); pdf.multi_cell(180, 5, "Observaciones:", align="J")
    pdf.set_xy(11,76); pdf.multi_cell(180, 5, "", align="J")
    pdf.set_line_width(0.1)
    pdf.line(10, 71.5, 200, 71.5)
    pdf.line(10, 92.5, 200, 92.5)
    pdf.line(10, 92.5, 10, 71.5)
    pdf.line(200, 92.5, 200, 71.5)

    pdf.set_xy(11,102.5); pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(180, 5, f"Ciudad Universitaria, Cd. Mx., a {dia} de {mes} de {año}", align="J")

    # Firmas
    pdf.set_xy(10,112.5); pdf.set_font("Arial", size=8.5, style="B"); pdf.multi_cell(95, 5, "Entrega", align="C")
    pdf.set_xy(10,132.5); pdf.set_font("Arial", size=8.5);          pdf.multi_cell(95, 5, "M.I. BRISIA JON SERRANO", align="C")
    pdf.set_xy(10,136.5);                                           pdf.multi_cell(95, 5, "Nombre, cargo y firma", align="C")
    pdf.set_xy(95,112.5); pdf.set_font("Arial", size=8.5, style="B"); pdf.multi_cell(95, 5, " Recibe", align="C")
    pdf.set_xy(95,136.5); pdf.set_font("Arial", size=8.5);            pdf.multi_cell(95, 5, "Nombre, cargo y firma", align="C")

    pdf.line(10, 112, 200, 112)
    pdf.line(10, 117.2, 200, 117.2)
    pdf.line(10, 137, 200, 137)
    pdf.line(10, 141, 200, 141)
    pdf.line(105, 141, 105, 112)
    pdf.line(10, 141, 10, 112)
    pdf.line(200, 141, 200, 112)

    pdf.set_font("Arial", size=6.5)
    pdf.set_xy(148,271.5); pdf.multi_cell(32, 5, "Rev. Octubre_2024", align="J")

    # Guardar
    pdf.output(direccionPDF+"DocumentoDGAE.pdf", "F")

########## DOCUMENTOS DOCTORADO ##########
def documentoDOC_UnaHoja(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, gradoAux):
    dia,mes,año= fecha()
    pdf = FPDF()
    # Agregar una página
    pdf.add_page()

    # Establecer la fuente y el tamaño de la fuente
    pdf.set_font("Arial", size=10)

    # Caja de Datos de alumno
    pdf.set_line_width(0.1)  # set the line thickness 
    pdf.line(10, 36, 200, 36) # lineas horizontales
    pdf.line(10, 40.5, 200, 40.5) # lineas horizontales
    pdf.line(10, 44.5, 200, 44.5) # lineas horizontales
    pdf.line(10, 49, 200, 49) # lineas horizontales
    pdf.line(10, 54.5, 200, 54.5) # lineas horizontales

    pdf.line(10, 36, 10, 54.5)  # linea izquierda
    pdf.line(49.3, 36, 49.3, 49)  # l
    pdf.line(161, 36, 161, 49)  # l
    pdf.line(172.5, 36, 172.5, 49) # l
    pdf.line(200, 36, 200, 54.5)  # linea derecha 

    #Caja de datos 
    pdf.line(10, 207, 10, 59.5)  # linea izquierda
    pdf.line(200, 207, 200, 59.5)  # linea derecha 
    pdf.line(18.5, 182.3, 18.5, 59.5) #linea central 
    pdf.line(157, 182.3, 157, 59.5)
    pdf.line(163, 182.3, 163, 65)
    pdf.line(187, 182.3, 187, 59.5)

    #Caja examenes a distancia 
    pdf.line(18.5, 207, 18.5, 187)
    pdf.line(157, 207, 157, 187)
    pdf.line(163, 207, 163, 187)
    pdf.line(187, 207, 187, 187)

    # Encabezado 
    pdf.line(10, 59.5, 200, 59.5) # lineas horizontales
    pdf.line(157, 65, 200, 65) # lineas horizontales
    pdf.line(10, 73, 200, 73) # lineas horizontales
    pdf.line(10, 73, 200, 73) # lineas horizontales

    ##########
    pdf.line(10, 79, 200, 79) # lineas horizontales
    pdf.line(10, 89, 200, 89) # lineas horizontales
    pdf.line(10, 84, 200, 84) # lineas horizontales
    pdf.line(10, 99, 200, 99) # lineas horizontales
    pdf.line(10, 104, 200, 104) # lineas horizontales
    pdf.line(10, 109, 200, 109) # lineas horizontales
    pdf.line(10, 119, 200, 119) # lineas horizontales
    pdf.line(10, 124, 200, 124) # lineas horizontales
    pdf.line(10, 134, 200, 134) # lineas horizontales
    pdf.line(10, 139, 200, 139) # lineas horizontales
    pdf.line(10, 144, 200, 144) # lineas horizontales
    pdf.line(10, 159, 200, 159) # lineas horizontales
    pdf.line(10, 169, 200, 169) # lineas horizontales
    pdf.line(10, 178, 200, 178) # lineas horizontales
    pdf.line(10, 182.3, 200, 182.3) # lineas horizontales
    pdf.line(10, 187, 200, 187) # lineas horizontales
    pdf.line(10, 192, 200, 192) # lineas horizontales
    pdf.line(10, 197, 200, 197) # lineas horizontales
    pdf.line(10, 207, 200, 207) # lineas horizontales
    #Caja de observaciones
    pdf.line(10, 222, 200, 222) # lineas horizontales
    pdf.line(10, 235, 200, 235) # lineas horizontales
    pdf.line(10, 235, 10, 222)  # linea izquierda
    pdf.line(200, 235, 200, 222)  # linea derecha 
    #Caja de firmas 
    pdf.line(10, 249, 180, 249) # lineas horizontales
    pdf.line(10, 253, 180, 253) # lineas horizontales
    pdf.line(10, 272.5, 180, 272.5) # lineas horizontales
    pdf.line(10, 276.5, 180, 276.5) # lineas horizontales
    pdf.line(10, 276.5, 10, 249)  # linea izquierda
    pdf.line(90, 276.5, 90, 249) #linea central
    pdf.line(180, 276.5, 180, 249)  # linea derecha 

    pdf.image(direccionImagen+"UNAM_SinTexto.jpeg", x=12, y=10, w=14, h=15)  # Agregar imagen
    pdf.image(direccionImagen+"LogoDGAE.PNG", x=182, y=16.5, w=18.5, h=9)  # Agregar imagen
    pdf.image(direccionImagen+"Nacion.PNG", x=182, y=255, w=14.5, h=13)  # Agregar imagen
    pdf.set_line_width(0.05)  # set the line thickness 
    pdf.line(10, 27, 200, 27)  # draw a line 
    pdf.set_xy(12,10)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(185, 4, "Universidad Nacional Autónoma de México", align="C")
    pdf.set_xy(12,14)
    pdf.multi_cell(185, 4, "Secretaría General", align="C")
    pdf.set_xy(12,18)
    pdf.multi_cell(185, 4, "Dirección General de Administración Escolar", align="C")
    pdf.set_xy(12,22)
    pdf.multi_cell(185, 4, "Dirección de Certificación y Control Documental", align="C")
    pdf.set_xy(5,28)
    pdf.set_font("Arial", "B", 13) 
    pdf.multi_cell(200, 5, "Relación de documentos para Autorización de Exámen de Grado (Doctorado)", align="C")
    pdf.set_line_width(1)  # set the line thickness 
    pdf.line(10, 34, 200, 34)  # draw a line 
    pdf.set_xy(10,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(45, 5, "Programa:", align="J")
    pdf.set_xy(10,40)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(45, 5, "Plan de estudios:", align="J")
    pdf.set_xy(10,44)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(45, 5, "Nombre de la o del alumno:", align="J")
    pdf.set_xy(50.5,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(95, 5, programa, align="J")
    pdf.set_xy(50.5,40)
    if len(Plan_estudios) > 90:
        pdf.set_font("Arial", size=4)

    else:
        pdf.set_font("Arial", size=8.5)
    
    pdf.multi_cell(95, 5, gradoAux + Plan_estudios, align="J")
    pdf.set_xy(50.5,44)
    if len(Nomb_alu) > 90:
        pdf.set_font("Arial", size=4)

    else:
        pdf.set_font("Arial", size=8.5)
        
    pdf.multi_cell(105, 5.3, Nomb_alu, align="J")
    pdf.set_xy(160.5,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(15, 5, "Clave:", align="J")
    pdf.set_xy(160.5,40)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(15, 5, "Clave:", align="J")
    pdf.set_xy(160.5,44)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(15, 5, "Cuenta:", align="J")
    pdf.set_xy(172.5,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(25, 5, "125", align="J")
    pdf.set_xy(172.5,40)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(25, 5, clave_str, align="J")
    pdf.set_xy(172.5,44)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(25, 5, No_cuenta_str, align="J")
    pdf.set_xy(12,49)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(185, 5, "Alumnado con antecedente UNAM en el ciclo inmediato anterior", align="C")

    pdf.set_xy(10,64)
    pdf.set_font("Arial", size=6.5, style="B")
    pdf.multi_cell(10, 5, "Núm.", align="J")

    pdf.set_xy(25,64)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(130, 5, "Listado de documentos", align="C")

    pdf.set_xy(156,60.5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(35, 5, "Programa", align="C")
    pdf.set_xy(188,60.5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(15, 5, "DGAE", align="J")

    pdf.set_xy(155.5,66)
    pdf.set_font("Arial", size=7.5, style="B")
    pdf.multi_cell(8, 5, "SI", align="C")

    pdf.set_xy(162,64.5)
    pdf.set_font("Arial", size=6.9, style="B")
    pdf.multi_cell(25, 5, "No aplica", align="C")
    pdf.set_xy(162,66.9)
    pdf.multi_cell(25, 5, "conforme al Plan", align="C")

    pdf.set_xy(188,66)
    pdf.set_font("Arial", size=7.5, style="B")
    pdf.multi_cell(12, 5, "Recibe", align="J")

    pdf.set_font("Arial", size=9.5)
    pdf.set_xy(10,74)
    pdf.multi_cell(8, 5, "1", align="C")
    pdf.set_xy(20,74)
    pdf.multi_cell(130, 5, "Carta de aceptación o suficiencia académica", align="J")
    pdf.set_xy(156,74)
    pdf.multi_cell(8, 5, "X", align="C")


    pdf.set_xy(10,79)
    pdf.multi_cell(8, 5, "2", align="C") 
    pdf.set_xy(156,79)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,79)
    pdf.multi_cell(130, 5, "Acta de candidatura al grado de Doctor", align="J")

    pdf.set_xy(10,84)
    pdf.multi_cell(8, 5, "3", align="C")
    pdf.set_xy(156,84)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,84)
    pdf.multi_cell(130, 5, "Dictamen del cumplimiento de actividades emitido por el Comité Académico", align="J")


    pdf.set_xy(10,91.5)
    pdf.multi_cell(8, 5, "4", align="C")
    pdf.set_xy(156,91.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,89)
    pdf.multi_cell(130, 5, "Constancia de idioma(s) (si es emitida por la UNAM solo copia, en caso de ser de otra institución deberá ser original)", align="J")

    pdf.set_xy(10,99)
    pdf.multi_cell(8, 5, "5", align="C")
    pdf.set_xy(156,99)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,99)
    pdf.multi_cell(130, 5, "Oficio de prórroga", align="J")

    pdf.set_xy(10,104)
    pdf.multi_cell(8, 5, "6", align="C")
    pdf.set_xy(156,104)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,104)
    pdf.multi_cell(130, 5, "Oficio de designación de jurado (tesis)", align="J")

    pdf.set_xy(10,111.5)
    pdf.multi_cell(8, 5, "7", align="C")
    pdf.set_xy(156,111.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,109)
    pdf.multi_cell(130, 5, "Cinco votos (podrán ser digitales, siempre y cuando tengan el Vo. Bo. de la o del Coordinador)", align="J")

    pdf.set_xy(10,119)
    pdf.multi_cell(8, 5, "8", align="C")
    pdf.set_xy(156,119)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,119)
    pdf.multi_cell(130, 5, "Hoja de actualización de datos", align="J")

    pdf.set_xy(10,126.5)
    pdf.multi_cell(8, 5, "9", align="C")
    pdf.set_xy(156,126.)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,124)
    pdf.multi_cell(130, 5, "Formato de Autorización de Transferencia de Información a la Dirección General de Profesiones de la Secretaría de Educación Pública (ATI)", align="J")


    pdf.set_xy(10,134)
    pdf.multi_cell(8, 5, "10", align="C")
    pdf.set_xy(156,134)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,134)
    pdf.multi_cell(130, 5, "Formato de no adeudo de biblioteca", align="J")

    pdf.set_xy(10,139)
    pdf.multi_cell(8, 5, "11", align="C")
    pdf.set_xy(156,139)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,139)
    pdf.multi_cell(130, 5, "Formato de solicitud y elección de grado", align="J")

    pdf.set_xy(10,149)
    pdf.multi_cell(8, 5, "12", align="C")
    pdf.set_xy(156,149)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,144)
    pdf.multi_cell(130, 5, "Comprobante de pago por el tipo de grado y la situación documental (Se debe incluir la ficha referenciada que genera el sistema de pagos y el comprobante expedido por BANXICO, si fue pago digital, excepto para pagos en BBVA Bancomer)", align="J")

    pdf.set_xy(10,161.5)
    pdf.multi_cell(8, 5, "13", align="C")
    pdf.set_xy(156,161.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,159)
    pdf.multi_cell(130, 5, "Cuatro (4) fotografías (de acuerdo con los requisitos específicos para el tipo de grado que la o el egresado solicitó)", align="J")

    pdf.set_xy(10,171.5)
    pdf.multi_cell(8, 5, "14", align="C")
    pdf.set_xy(156,171.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,169)
    pdf.multi_cell(130, 5, "Protesta Universitaria de Integridad y Honestidad Académica y Profesional (con la firma original de la o del alumno)", align="J")


    pdf.set_xy(10,178)
    pdf.multi_cell(8, 5, "15", align="C")
    pdf.set_xy(156,178)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,178)
    pdf.multi_cell(130, 5, "Carta aval firmada por la tutora o el tutor (en caso de trabajo escrito)", align="J")

    pdf.set_xy(20,182.2)
    pdf.set_font("Arial", size=7.2, style="B")
    pdf.multi_cell(130, 5, "Para exámenes de grado realizados a distancia:", align="J")

    pdf.set_font("Arial", size=9.5)
    pdf.set_xy(10,187)
    pdf.multi_cell(8, 5, "16", align="C")
    pdf.set_xy(156,187)
    pdf.multi_cell(8, 5, "", align="C")
    pdf.set_xy(20,187)
    pdf.multi_cell(130, 5, "Solicitud de la o del alumno para presentar exámenes de grado vía remota", align="J")

    pdf.set_xy(10,192)
    pdf.multi_cell(8, 5, "17", align="C")
    pdf.set_xy(156,192)
    pdf.multi_cell(8, 5, "", align="C")
    pdf.set_xy(20,192)
    pdf.multi_cell(130, 5, "Oficio de autorización para presentar examen de grado vía remota.", align="J")

    pdf.set_xy(10,199.5)
    pdf.multi_cell(8, 5, "18", align="C")
    pdf.set_xy(156,199.5)
    pdf.multi_cell(8, 5, "", align="C")
    pdf.set_xy(20,197)
    pdf.multi_cell(130, 5, "Carta de confidencialidad (firmada por cada integrante del sínodo, más la carta de la o del sustentante)", align="J")

    pdf.set_font("Arial", size=7, style="B")
    pdf.set_xy(10,207.3)
    pdf.multi_cell(130, 3.5, "Notas:", align="J")
    pdf.set_xy(20,207.5)
    pdf.multi_cell(176, 3, "La liberación de estudios la integrará la DGAE al expediente, para que con todos estos documentos se emita la Autorización de Examen, sin necesidad de realizar una doble entrega documental.", align="J")
    pdf.set_xy(20,212.5)
    pdf.multi_cell(176, 5, "Solo se aceptarán expedientes completos, es decir, que contengan TODOS los documentos en el orden en que aparecen en el listado.", align="J")

    pdf.set_xy(11,222)
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(180, 5, "Observaciones:", align="J")
    pdf.set_xy(11,226)
    pdf.multi_cell(180, 5, "Se anexa oficio de artículo de investigación, requisito de plan de estudios.", align="J")

    pdf.set_xy(11,237)
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(180, 5, "Ciudad Universitaria, Cd. Mx., a "+dia+" de "+mes+" de " +año, align="J")

    pdf.set_xy(11,248.5)
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(69, 5, "Entrega", align="C")
    pdf.set_xy(91,248.5)
    pdf.multi_cell(69, 5, "                  Recibe", align="C")

    pdf.set_xy(11,268)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(69, 5, "M.I. BRISIA JON SERRANO", align="C")
    pdf.set_xy(11,271.8)
    pdf.multi_cell(69, 5, "Nombre, cargo y firma", align="C")
    pdf.set_xy(120,271.8)
    pdf.multi_cell(90, 5,            "Nombre, cargo y firma", align="J")

    pdf.set_font("Arial", size=6.5)
    pdf.set_xy(180,268)
    pdf.multi_cell(18, 5, "Rev.", align="C")
    pdf.set_xy(180,271.5)
    pdf.multi_cell(18, 5, "Octubre_2024", align="J")

    # Guardar el PDF
    pdf.output(direccionPDF+"DocumentoDGAE.pdf", "F")

def documentoDOC_DosHojas(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, grado, gradoAux,tipo):
    dia,mes,año= fecha()
    # Crear un objeto FPDF
    pdf = FPDF()

    # Agregar una página
    pdf.add_page()

    # Establecer la fuente y el tamaño de la fuente
    pdf.set_font("Arial", size=10)

    # Caja de Datos de alumno
    pdf.set_line_width(0.1)  # set the line thickness 
    pdf.line(10, 36, 200, 36) # lineas horizontales
    pdf.line(10, 40.5, 200, 40.5) # lineas horizontales
    pdf.line(10, 44.5, 200, 44.5) # lineas horizontales
    pdf.line(10, 49, 200, 49) # lineas horizontales
    pdf.line(10, 54.5, 200, 54.5) # lineas horizontales

    pdf.line(10, 36, 10, 54.5)  # linea izquierda
    pdf.line(49.3, 36, 49.3, 49)  # l
    pdf.line(161, 36, 161, 49)  # l
    pdf.line(172.5, 36, 172.5, 49) # l
    pdf.line(200, 36, 200, 54.5)  # linea derecha 

    #Caja de datos ,lineas verticales
    pdf.line(10, 262.5, 10, 59.5)  # linea izquierda
    pdf.line(200, 262.5, 200, 59.5)  # linea derecha 
    pdf.line(18.5, 237.5, 18.5,59.5) #linea central 
    pdf.line(157, 237.5, 157, 59.5)
    pdf.line(163, 237.5, 163, 65)
    pdf.line(187, 237.5, 187, 59.5)

    pdf.line(18.5, 262.5, 18.5, 241.4) #linea central continuacion
    pdf.line(157, 262.5, 157, 241.4)
    pdf.line(163, 262.5, 163, 241.4)
    pdf.line(187, 262.5, 187, 241.4)

    #lineas horizontales de la caja de entrega de documentos 
    pdf.line(10, 59.5, 200, 59.5) # lineas horizontales
    pdf.line(157, 65, 200, 65) # lineas horizontales
    pdf.line(10, 73.5, 200, 73.5) # lineas horizontales
    pdf.line(10, 82, 200, 82) # lineas horizontales
    pdf.line(10, 86.5, 200, 86.5) # lineas horizontales
    pdf.line(10, 96.5, 200, 96.5) # lineas horizontales 
    pdf.line(10, 115, 200, 115) # lineas horizontales
    pdf.line(10, 124, 200, 124) # lineas horizontales
    pdf.line(10, 140, 200, 140) # lineas horizontales
    pdf.line(10, 145, 200, 145) # lineas horizontales
    pdf.line(10, 150, 200, 150) # lineas horizontales
    pdf.line(10, 155, 200, 155) # lineas horizontales
    pdf.line(10, 163, 200, 163) # lineas horizontales
    pdf.line(10, 167, 200, 167) # lineas horizontales
    pdf.line(10, 172, 200, 172) # lineas horizontales
    pdf.line(10, 180, 200, 180) # lineas horizontales
    pdf.line(10, 185, 200, 185) # lineas horizontales
    pdf.line(10, 193, 200, 193) # lineas horizontales
    pdf.line(10, 198, 200, 198) # lineas horizontales
    pdf.line(10, 203, 200, 203) # lineas horizontales
    pdf.line(10, 215, 200, 215) # lineas horizontales
    pdf.line(10, 224, 200, 224) # lineas horizontales
    pdf.line(10, 233, 200, 233) # lineas horizontales
    pdf.line(10, 237.5, 200, 237.5) # lineas horizontales
    pdf.line(10, 241.4, 200, 241.4) # lineas horizontales
    pdf.line(10, 246.5, 200, 246.5) # lineas horizontales
    pdf.line(10, 251.5, 200, 251.5) # lineas horizontales
    pdf.line(10, 262.5, 200, 262.5) # lineas horizontales

    pdf.image(direccionImagen+"UNAM_SinTexto.jpeg", x=12, y=10, w=14, h=15)  # Agregar imagen
    pdf.image(direccionImagen+"LogoDGAE.PNG", x=182, y=16.5, w=18.5, h=9)  # Agregar imagen
    pdf.image(direccionImagen+"Nacion.PNG", x=178, y=263.9, w=13.7, h=11.8)  # Agregar imagen
    pdf.set_line_width(0.05)  # set the line thickness 
    pdf.line(10, 27, 200, 27)  # draw a line 
    pdf.set_xy(12,10)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(185, 4, "Universidad Nacional Autónoma de México", align="C")
    pdf.set_xy(12,14)
    pdf.multi_cell(185, 4, "Secretaría General", align="C")
    pdf.set_xy(12,18)
    pdf.multi_cell(185, 4, "Dirección General de Administración Escolar", align="C")
    pdf.set_xy(12,22)
    pdf.multi_cell(185, 4, "Dirección de Certificación y Control Documental", align="C")
    pdf.set_xy(10,28)
    pdf.set_font("Arial", "B", 13.2)
    pdf.multi_cell(185, 5, "Relación de documentos para Autorización de Exámenes de Grado (Doctorado)", align="C")
    pdf.set_line_width(1)  # set the line thickness 
    pdf.line(10, 34, 200, 34)  # draw a line 
    pdf.set_xy(10,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(45, 5, "Programa:", align="J")
    pdf.set_xy(10,40)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(45, 5, "Plan de estudios:", align="J")
    pdf.set_xy(10,44)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(45, 5, "Nombre de la o del alumno:", align="J")
    pdf.set_xy(50.5,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(95, 5, programa, align="J")
    pdf.set_xy(50.5,40)
    if len(Plan_estudios) > 90:
        pdf.set_font("Arial", size=4)

    else:
        pdf.set_font("Arial", size=8.5)
    
    pdf.multi_cell(95, 5, gradoAux + Plan_estudios, align="J")
    pdf.set_xy(50.5,44)
    if len(Nomb_alu) > 90:
        pdf.set_font("Arial", size=4)

    else:
        pdf.set_font("Arial", size=8.5)
        
    pdf.multi_cell(105, 5.3, Nomb_alu, align="J")
    pdf.set_xy(160.5,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(15, 5, "Clave:", align="J")
    pdf.set_xy(160.5,40)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(15, 5, "Clave:", align="J")
    pdf.set_xy(160.5,44)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(15, 5, "Cuenta:", align="J")
    pdf.set_xy(172.5,36)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(25, 5, "125", align="J")
    pdf.set_xy(172.5,40)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(25, 5, clave_str, align="J")
    pdf.set_xy(172.5,44)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(25, 5, No_cuenta_str, align="J")
    pdf.set_xy(12,49)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(185, 5, "Alumnado sin antecedente UNAM en el ciclo anterior inmediato", align="C")

    pdf.set_xy(10,64)
    pdf.set_font("Arial", size=6.5, style="B")
    pdf.multi_cell(10, 5, "Núm.", align="J")

    pdf.set_xy(25,64)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(130, 5, "Listado de documentos", align="C")

    pdf.set_xy(156,60.5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(35, 5, "Programa", align="C")
    pdf.set_xy(188,60.5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.multi_cell(15, 5, "DGAE", align="J")

    pdf.set_xy(155.5,66)
    pdf.set_font("Arial", size=7.5, style="B")
    pdf.multi_cell(8, 5, "SI", align="C")

    pdf.set_xy(162,64.5)
    pdf.set_font("Arial", size=6.9, style="B")
    pdf.multi_cell(25, 5, "No aplica", align="C")
    pdf.set_xy(162,66.9)
    pdf.multi_cell(25, 5, "conforme al Plan", align="C")

    pdf.set_xy(188,66)
    pdf.set_font("Arial", size=7.5, style="B")
    pdf.multi_cell(12, 5, "Recibe", align="J")
    #Sin antecedentes
    if tipo == "1":
        pdf.set_font("Arial", size=9.5)
        pdf.set_xy(10,75.8)
        pdf.multi_cell(8, 5, "1", align="C")
        pdf.set_xy(20,73.8)
        pdf.multi_cell(130, 5, "Acta de nacimiento original", align="J")
        pdf.set_xy(20,78)
        pdf.multi_cell(130, 4, "(para extranjeros apostillada o legalizada y, en su caso, traducida)*", align="J")
        pdf.set_xy(156,74)
        #Posible x a quitar
        pdf.multi_cell(8, 5, "", align="C")

        pdf.set_xy(10,82)
        pdf.multi_cell(8, 5, "2", align="C")
        pdf.set_xy(156,82)
        #Posible x a quitar
        pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,82)
        pdf.multi_cell(130, 5, "CURP*", align="J")

        pdf.set_xy(10,89.5)
        pdf.multi_cell(8, 5, "3", align="C")
        pdf.set_xy(156,89.5)
        #Posible x a quitar
        pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,87)
        pdf.multi_cell(130, 4, "Título de licenciatura (copia con el sello de cotejado por el Programa) ", align="J")
        pdf.set_xy(20,91)
        pdf.multi_cell(130, 4, "(Para extranjeros, apostillado o legalizado y, en su caso, traducido)*", align="J")

        pdf.set_xy(10,104.5)
        pdf.multi_cell(8, 5, "4", align="C")
        pdf.set_xy(156,104.5)
        pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,96.5)
        pdf.multi_cell(135, 4.5, "Certificado de estudios de licenciatura ", align="J")
        pdf.set_xy(20,100.5)
        pdf.multi_cell(135, 4.5, "Si el certificado no tiene promedio, se deberá anexar la constancia de promedio correspondiente, (para estudios en el extranjero apostillado o legalizado y, en su caso, traducido y equivalencia de promedio emitido por la DGIRE, todo en original)*", align="J")

        pdf.set_xy(10,117.8)
        pdf.multi_cell(8, 5, "5", align="C")
        pdf.set_xy(156,119.5)
        pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,115)
        pdf.multi_cell(135, 4, "Grado de maestría (copia con el sello de cotejado por el Programa)", align="J")
        pdf.set_xy(20,119)
        pdf.multi_cell(135, 4, "(para extranjeros, apostillado o legalizado y, en su caso, traducido)*", align="J")

        pdf.set_xy(10,130.2)
        pdf.multi_cell(8, 5, "6", align="C")
        pdf.set_xy(156,131.5)
        pdf.multi_cell(8, 5, "", align="C")
        pdf.set_xy(20,124)
        pdf.multi_cell(135, 4, "Certificado de estudios de maestría", align="J")
        pdf.set_xy(20,128)
        pdf.multi_cell(135, 4, "(Si el certificado no tiene promedio, se deberá anexar la constancia de promedio correspondiente, (para estudios en el extranjero apostillado o legalizado y, en su caso, traducido y equivalencia de promedio emitida por la DGIRE todo en original)*", align="J")

    #Con antecedentes
    elif tipo=="2":
        pdf.set_font("Arial", size=9.5)
        pdf.set_xy(10,75.8)
        pdf.multi_cell(8, 5, "1", align="C")
        pdf.set_xy(20,73.8)
        pdf.multi_cell(130, 5, "Acta de nacimiento original", align="J")
        pdf.set_xy(20,78)
        pdf.multi_cell(130, 4, "(para extranjeros apostillada o legalizada y, en su caso, traducida)*", align="J")
        pdf.set_xy(156,74)
        #Posible x a quitar
        pdf.multi_cell(8, 5, "X", align="C")

        pdf.set_xy(10,82)
        pdf.multi_cell(8, 5, "2", align="C")
        pdf.set_xy(156,82)
        #Posible x a quitar
        pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,82)
        pdf.multi_cell(130, 5, "CURP*", align="J")

        pdf.set_xy(10,89.5)
        pdf.multi_cell(8, 5, "3", align="C")
        pdf.set_xy(156,89.5)
        #Posible x a quitar
        pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,87)
        pdf.multi_cell(130, 4, "Título de licenciatura (copia con el sello de cotejado por el Programa) ", align="J")
        pdf.set_xy(20,91)
        pdf.multi_cell(130, 4, "(Para extranjeros, apostillado o legalizado y, en su caso, traducido)*", align="J")


        pdf.set_xy(10,104.5)
        pdf.multi_cell(8, 5, "4", align="C")
        pdf.set_xy(156,104.5)
        pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,96.5)
        pdf.multi_cell(135, 4.5, "Certificado de estudios de licenciatura ", align="J")
        pdf.set_xy(20,100.5)
        pdf.multi_cell(135, 4.5, "Si el certificado no tiene promedio, se deberá anexar la constancia de promedio correspondiente, (para estudios en el extranjero apostillado o legalizado y, en su caso, traducido y equivalencia de promedio emitido por la DGIRE, todo en original)*", align="J")

        pdf.set_xy(10,117.8)
        pdf.multi_cell(8, 5, "5", align="C")
        pdf.set_xy(156,119.5)
        pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,115)
        pdf.multi_cell(135, 4, "Grado de maestría (copia con el sello de cotejado por el Programa)", align="J")
        pdf.set_xy(20,119)
        pdf.multi_cell(135, 4, "(para extranjeros, apostillado o legalizado y, en su caso, traducido)*", align="J")

        pdf.set_xy(10,130.2)
        pdf.multi_cell(8, 5, "6", align="C")
        pdf.set_xy(156,131.5)
        pdf.multi_cell(8, 5, "X", align="C")
        pdf.set_xy(20,124)
        pdf.multi_cell(135, 4, "Certificado de estudios de maestría", align="J")
        pdf.set_xy(20,128)
        pdf.multi_cell(135, 4, "(Si el certificado no tiene promedio, se deberá anexar la constancia de promedio correspondiente, (para estudios en el extranjero apostillado o legalizado y, en su caso, traducido y equivalencia de promedio emitida por la DGIRE todo en original)*", align="J")


    pdf.set_xy(10,140)
    pdf.multi_cell(8, 5, "7", align="C")
    pdf.set_xy(156,140)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,140)
    pdf.multi_cell(135, 5, "Carta de aceptación o suficiencia académica", align="J")

    pdf.set_xy(10,145)
    pdf.multi_cell(8, 5, "8", align="C")
    pdf.set_xy(156,145)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,145)
    pdf.multi_cell(135, 5, "Acta de candidatura al grado de Doctor", align="J")

    pdf.set_xy(10,150)
    pdf.multi_cell(8, 5, "9", align="C")
    pdf.set_xy(156,150)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,150)
    pdf.multi_cell(135, 5, "Dictamen de cumplimiento de actividades emitido por el Comité Académico", align="J")

    pdf.set_xy(10,157)
    pdf.multi_cell(8, 5, "10", align="C")
    pdf.set_xy(156,157)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,155)
    pdf.multi_cell(135, 4, "Constancia de idioma(s) (si es emitida por la UNAM, solo copia, en caso de ser de otra institución deberá ser original)*", align="J")

    pdf.set_xy(10,162.5)
    pdf.multi_cell(8, 5, "11", align="C")
    pdf.set_xy(156,162.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,162.5)
    pdf.multi_cell(135, 5, "Oficio de prórroga", align="J")

    pdf.set_xy(10,167)
    pdf.multi_cell(8, 5, "12", align="C")
    pdf.set_xy(156,167)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,167)
    pdf.multi_cell(135, 5, "Oficio de designación de jurado (tesis)", align="J")

    pdf.set_xy(10,173.5)
    pdf.multi_cell(8, 5, "13", align="C")
    pdf.set_xy(156,173.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,172)
    pdf.multi_cell(135, 4, "Cinco votos (podrán ser digitales, siempre y cuando tengan el Vo. Bo. de la o del Coordinador)", align="J")

    pdf.set_xy(10,180)
    pdf.multi_cell(8, 5, "14", align="C")
    pdf.set_xy(156,180)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,180)
    pdf.multi_cell(135, 5, "Hoja de actualización de datos", align="J")

    pdf.set_xy(10,185)
    pdf.multi_cell(8, 5, "15", align="C")
    pdf.set_xy(156,185)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,185)
    pdf.multi_cell(135,4, "Formato de Autorización de Transferencia de Información a la Dirección General de Profesiones de la Secretaría de Educación Pública (ATI)", align="J")

    pdf.set_xy(10,193)
    pdf.multi_cell(8, 5, "16", align="C")
    pdf.set_xy(156,193)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,193)
    pdf.multi_cell(135, 5, "Formato de no adeudo de bibliotecas", align="J")

    pdf.set_xy(10,198)
    pdf.multi_cell(8, 5, "17", align="C")
    pdf.set_xy(156,198)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,198)
    pdf.multi_cell(135, 5, "Formato de solicitud y elección de grado", align="J")

    pdf.set_xy(10,206)
    pdf.multi_cell(8, 5, "18", align="C")
    pdf.set_xy(156,206)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,203)
    pdf.multi_cell(135,4, "Comprobante de pago por el tipo de grado y la situación documental (Se debe incluir la ficha referenciada que genera el sistema de pagos y el comprobante expedido por BANXICO, si fue pago digital, excepto para pagos en BBVA Bancomer)", align="J")

    pdf.set_xy(10,217.5)
    pdf.multi_cell(8, 5, "19", align="C")
    pdf.set_xy(156,217.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,216)
    pdf.multi_cell(135, 4, "Cuatro (4) fotografías (de acuerdo con los requisitos específicos para el tipo de grado que la o el egresado solicitó)", align="J")

    pdf.set_xy(10,224.5)
    pdf.multi_cell(8, 5, "20", align="C")
    pdf.set_xy(156,224.5)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,224.5)
    pdf.multi_cell(135, 4, "Protesta Universitaria de Integridad y Honestidad Académica y Profesional (con la firma original de la o del alumno)", align="J")

    pdf.set_xy(10,233)
    pdf.multi_cell(8, 5, "21", align="C")
    pdf.set_xy(156,233)
    pdf.multi_cell(8, 5, "X", align="C")
    pdf.set_xy(20,233)
    pdf.multi_cell(135, 5, "Carta aval firmada por la tutora o el tutor (en caso de trabajo escrito)", align="J")

    pdf.set_xy(20,237)
    pdf.set_font("Arial", size=7.5, style="B")
    pdf.multi_cell(130, 5, "Para exámenes de grado realizados a distancia:", align="J")

    pdf.set_font("Arial", size=9.5)
    pdf.set_xy(10,242)
    pdf.multi_cell(8, 5, "22", align="C")
    pdf.set_xy(20,242)
    pdf.multi_cell(135, 5, "Solicitud de la o del alumno para presentar exámenes de grado vía remota", align="J")

    pdf.set_xy(10,247)
    pdf.multi_cell(8, 5, "23", align="C")
    pdf.set_xy(20,247)
    pdf.multi_cell(135, 5, "Oficio de autorización para presentar examen de grado vía remota.", align="J")

    pdf.set_xy(10,252)
    pdf.multi_cell(8, 5, "24", align="C")
    pdf.set_xy(20,252)
    pdf.multi_cell(135, 5, "Carta de confidencialidad (firmada por cada integrante del sínodo, más la carta de la o del sustentante)", align="J")

    pdf.set_font("Arial", size=6.5)
    pdf.set_xy(153,271.5)
    pdf.multi_cell(32, 5, "Rev. Octubre_2024", align="J")

    #inicia segunda paguina 
    pdf.add_page()
    pdf.image(direccionImagen+"UNAM_SinTexto.jpeg", x=12, y=10, w=14, h=15)  # Agregar imagen
    pdf.image(direccionImagen+"LogoDGAE.PNG", x=182, y=16.5, w=18.5, h=9)  # Agregar imagen
    pdf.image(direccionImagen+"Nacion.PNG", x=175, y=261.5, w=15.9, h=14)  # Agregar imagen
    pdf.set_line_width(0.05)  # set the line thickness 
    pdf.line(10, 27, 200, 27)  # draw a line 
    pdf.set_xy(12,10)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(185, 4, "Universidad Nacional Autónoma de México", align="C")
    pdf.set_xy(12,14)
    pdf.multi_cell(185, 4, "Secretaría General", align="C")
    pdf.set_xy(12,18)
    pdf.multi_cell(185, 4, "Dirección General de Administración Escolar", align="C")
    pdf.set_xy(12,22)
    pdf.multi_cell(185, 4, "Dirección de Certificación y Control Documental", align="C")
    pdf.set_xy(10,28)
    pdf.set_font("Arial", "B", 13.2) 
    pdf.multi_cell(185, 5, "Relación de documentos para Autorización de Exámenes de Grado (Doctorado)", align="C")
    pdf.set_line_width(1)  # set the line thickness 
    pdf.line(10, 34, 200, 34)  # draw a line 
    pdf.set_xy(10,37)
    pdf.set_font("Arial", size=8, style="B")
    pdf.multi_cell(130, 5, "Notas:", align="J")
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.set_xy(10,44)
    pdf.multi_cell(200, 4, "*En caso de que el programa de Posgrado haya recibido documentos de ingreso.", align="J")
    pdf.set_xy(10,49)
    pdf.multi_cell(190, 4, "La liberación de estudios la integrará la DGAE al expediente, para que con todos estos documentos se emita la Autorización de Examen, sin necesidad de realizar una doble entrega documental.", align="J")
    pdf.set_xy(10,59)
    pdf.multi_cell(190, 4, "Solo se aceptarán expedientes completos, es decir, que contengan TODOS los documentos en el orden en que aparecen en el listado.", align="J")
    #TextoCajaDeObservaciones
    pdf.set_xy(10,72)
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(180, 5, "Observaciones:", align="J")
    pdf.set_xy(11,76)

    #Sin antecedentes
    if tipo == "1":
        pdf.multi_cell(180, 5, "Se anexa oficio de artículo de investigación, requisito de plan de estudios más expediente electronica.", align="J")
    #Con antecedentes
    elif tipo=="2":
        pdf.multi_cell(180, 5, "Se anexa oficio de artículo de investigación, requisito de plan de estudios.", align="J")

    #Caja de observaciones
    pdf.set_line_width(0.1)  # set the line thickness 
    pdf.line(10, 71.5, 200, 71.5) # lineas horizontales
    pdf.line(10, 92.5, 200, 92.5) # lineas horizontales
    pdf.line(10, 92.5, 10, 71.5)  # linea izquierda
    pdf.line(200, 92.5, 200, 71.5)  # linea derecha 
    pdf.set_xy(11,102.5)
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(180, 5, "Ciudad Universitaria, Cd. Mx., a "+dia+" de "+mes+" de " +año, align="J")
    #Texto Caja de firmas 
    pdf.set_xy(10,112.5)
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(95, 5, "Entrega", align="C")
    pdf.set_xy(10,132.5)
    pdf.set_font("Arial", size=8.5)
    pdf.multi_cell(95, 5, "M.I. BRISIA JON SERRANO", align="C")
    pdf.set_xy(10,136.5)
    pdf.multi_cell(95, 5, "Nombre, cargo y firma", align="C")
    pdf.set_xy(95,112.5)
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.multi_cell(95, 5, " Recibe", align="C")
    pdf.set_font("Arial", size=8.5)
    pdf.set_xy(95,136.5)
    pdf.multi_cell(95, 5, "Nombre, cargo y firma", align="C") 
    #Caja de firmas 
    pdf.line(10, 112, 200, 112) # lineas horizontales
    pdf.line(10, 117.2, 200, 117.2) # lineas horizontales
    pdf.line(10, 137, 200, 137) # lineas horizontales
    pdf.line(10, 141, 200, 141) # lineas horizontale
    pdf.line(105, 141, 105, 112) #linea central
    pdf.line(10, 141, 10, 112)  # linea izquierda
    pdf.line(200, 141, 200, 112)  # linea derecha
    pdf.set_font("Arial", size=6.5)
    pdf.set_xy(148,271.5)
    pdf.multi_cell(32, 5, "Rev. Octubre_2024", align="J")

    # Guardar el PDF
    pdf.output(direccionPDF+"DocumentoDGAE.pdf", "F")


########## FUNCIONES AUXILIARES ##########
def fecha():
    ahora = datetime.now()

    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    dia = str(ahora.day)
    mes = meses[ahora.month]
    año = str(ahora.year)

    return dia, mes, año

# === Helpers para leer POSGRADO y decidir programa/flujo ===
def _determinar_programa_y_grado(plan_int: int):
    if 3000 <= plan_int <= 3999:
        return ("PROGRAMA UNICO DE ESPECIALIZACIONES DE INGENIERIA", "Especialidad")
    if 4000 <= plan_int <= 4999:
        return ("PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA", "Maestría")
    if 5000 <= plan_int <= 5999:
        return ("PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA", "Doctorado")
    return (None, None)

def _buscar_alumno(numero_cuenta: str):
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

def _infer_programa(plan):
    plan = int(plan)
    if 3000 <= plan <= 3999:
        return "especialidad"
    if 4000 <= plan <= 4999:
        return "maestria"
    if 5000 <= plan <= 5999:
        return "doctorado"
    return "desconocido"

def _listar_registros_dgae(numero_cuenta):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                   tituloTesina, modalidad
            FROM posgrado
            WHERE numeroCuenta = ?
            ORDER BY planEstudios
        """, (numero_cuenta,))
        return cur.fetchall()

def _obtener_registro_dgae_por_id(reg_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                   tituloTesina, modalidad
            FROM posgrado
            WHERE id = ?
            LIMIT 1
        """, (reg_id,))
        return cur.fetchone()

#################################################################################################################################
@dgae_bp.route("/", methods=["GET", "POST"])
@permission_required("dgae")
def dgae():
    if request.method == "GET":
        return render_template("dgae.html")

    numero = (request.form.get("numeroDeCuenta") or "").strip()
    tipo_doc = (request.form.get("tipoDocumento") or "").strip()
    seleccion_id = request.form.get("seleccion_id")

    # Validaciones básicas
    if not numero or not numero.isdigit() or len(numero) != 9:
        return jsonify(success=False, error="Número de cuenta inválido (9 dígitos)."), 400

    # Si el usuario ya eligió un plan específico
    if seleccion_id:
        fila = _obtener_registro_dgae_por_id(int(seleccion_id))

        if not fila:
            return jsonify(success=False, error="Selección inválida.")

        _id, No_cuenta_str, Nomb_alu, clave_int, Plan_estudios, _titulo, modalidad = fila

        try:
            clave_int = int(clave_int)
        except Exception:
            return jsonify(success=False, error="El plan de estudios no es numérico.")

        Plan_estudios = Plan_estudios or ""
        modalidad = modalidad or ""

    else:
        # Buscar todos los registros de esa cuenta
        filas = _listar_registros_dgae(numero)

        if not filas:
            return jsonify(success=False, error="No se encontró la cuenta en POSGRADO.")

        # Si hay más de un registro y todavía no selecciona plan, mandar opciones al JS
        if len(filas) > 1:
            opciones = []

            for rid, cuenta, nombre, plan, espec, titulo, modalidad in filas:
                opciones.append({
                    "id": rid,
                    "numeroCuenta": cuenta,
                    "nombre": nombre,
                    "planEstudios": int(plan),
                    "programa": _infer_programa(plan).capitalize(),
                    "especializacion": espec or ""
                })

            return jsonify({
                "success": True,
                "multiples": opciones,
                "resumen": "Este alumno tiene más de un plan. Selecciona cuál usar para DGAE."
            })

        # Si solo hay un registro, usar ese directamente
        _id, No_cuenta_str, Nomb_alu, clave_int, Plan_estudios, _titulo, modalidad = filas[0]

        try:
            clave_int = int(clave_int)
        except Exception:
            return jsonify(success=False, error="El plan de estudios no es numérico.")

        Plan_estudios = Plan_estudios or ""
        modalidad = modalidad or ""

    programa, grado = _determinar_programa_y_grado(clave_int)

    if not programa:
        return jsonify(success=False, error="El plan está fuera de rango (3000–5999).")

    # Si todavía no se pide documento, solo validar y mostrar botones
    if not tipo_doc:
        return jsonify(success=True, msg="Cuenta válida en POSGRADO.")

    tipos_documento = {
        "documento1": ("1", "2"),
        "documento2_sinX": ("2", "1"),
        "documento2_conX": ("2", "2"),
    }

    config = tipos_documento.get(tipo_doc)

    if not config:
        return jsonify(success=False, error="Tipo de documento no reconocido."), 400

    opcion, tipo = config
    clave_str = str(clave_int)

    try:
        if grado == "Especialidad":
            especialidad(
                No_cuenta_str,
                Plan_estudios,
                clave_str,
                Nomb_alu,
                programa,
                opcion,
                tipo,
                modalidad
            )
        elif grado == "Maestría":
            maestria(
                No_cuenta_str,
                Plan_estudios,
                clave_str,
                Nomb_alu,
                programa,
                opcion,
                tipo,
                modalidad
            )
        elif grado == "Doctorado":
            doctorado(
                No_cuenta_str,
                Plan_estudios,
                clave_str,
                Nomb_alu,
                programa,
                opcion,
                tipo,
                modalidad
            )
        else:
            return jsonify(success=False, error="Grado no identificado.")
    except Exception as e:
        return jsonify(success=False, error=f"Error al generar PDF: {e}")

    return jsonify(success=True, documentos=["DocumentoDGAE.pdf"])
        
@dgae_bp.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
