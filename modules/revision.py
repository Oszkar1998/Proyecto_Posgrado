# Librerías necesarias
from datetime import datetime
from flask import Blueprint, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from fpdf import FPDF
from auth import permission_required
from config import direccionBase, direccionImagen,direccionPDF
from db import get_connection

revision_bp = Blueprint('revision', __name__, template_folder='../templates')

############################## FUNCIONES NORMALES SIN HTML ##############################
def especialidad(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, trabajo, presidente, secretario, vocal1, vocal2, vocal3, modalidad):
    programa = "PROGRAMA UNICO DE ESPECIALIZACIONES DE INGENIERIA"
    grado = "la ESPECIALIZACIÓN"
    gradoEstudios = "ESPECIALISTA EN "
   
    # Obtener Número de Oficio 
    contador = obtener_contador()
    contador = verificarContador(contador)

    # Obtener Nombre del coordinador 
    nombreCoor, sexoCoor = obtener_coordinador()
    nombreCoor = nombreCoor.upper()
    sexoCoor = verificarCoordinador(sexoCoor)
    pdf=FPDF()

    ingles(pdf,Plan_estudios, Nomb_alu, programa, genero, contador, nombreCoor, sexoCoor, grado, gradoEstudios)
    prorroga(pdf,Plan_estudios, Nomb_alu, No_cuenta_str, clave_str, genero, programa, grado, contador, nombreCoor, sexoCoor, gradoEstudios) 
    dictamen(pdf,Plan_estudios, Nomb_alu, No_cuenta_str, genero, grado, nombreCoor, sexoCoor, gradoEstudios)  
    oficioJurado(pdf, Nomb_alu, Plan_estudios, clave_str, trabajo, presidente, secretario, vocal1, vocal2, vocal3, genero, modalidad, nombreCoor, sexoCoor, programa, gradoEstudios)
    pdf.output(direccionPDF + "DocumentoEspecialidad.pdf", "F")

def maestria(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, trabajo, presidente, secretario, vocal1, vocal2, vocal3, modalidad):
    programa = "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
    grado = "la MAESTRIA"
    gradoEstudios = "MAESTRIA EN "
    
    # Obtener Número de Oficio 
    contador = obtener_contador()
    contador = verificarContador(contador)

    # Obtener Nombre del coordinador 
    #nombreCoor, sexoCoor = obtener_coordinador()
    #nombreCoor = nombreCoor.upper()
    #sexoCoor = verificarCoordinador(sexoCoor)

    nombreCoor = "DR. GABRIEL EDUARDO SANDOVAL ROMERO" 
    sexoCoor = "EL COORDINADOR"

    pdf=FPDF()

    ingles(pdf,Plan_estudios, Nomb_alu, programa, genero, contador, nombreCoor, sexoCoor, grado, gradoEstudios)
    prorroga(pdf,Plan_estudios, Nomb_alu, No_cuenta_str, clave_str, genero, programa, grado, contador, nombreCoor, sexoCoor, gradoEstudios) 
    dictamen(pdf,Plan_estudios, Nomb_alu, No_cuenta_str, genero, grado, nombreCoor, sexoCoor, gradoEstudios)  
    oficioJurado(pdf, Nomb_alu, Plan_estudios, clave_str, trabajo, presidente, secretario, vocal1, vocal2, vocal3, genero, modalidad, nombreCoor, sexoCoor, programa, gradoEstudios)
    pdf.output(direccionPDF + "DocumentoMaestria.pdf", "F")

def doctorado(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, articulo, revista, trabajo, presidente, secretario, vocal1, vocal2, vocal3, modalidad    ):
    programa = "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
    grado = "el DOCTORADO"
    gradoEstudios = "DOCTORADO EN "

    # Obtener Número de Oficio 
    contador = obtener_contador()
    contador = verificarContador(contador)

    # Obtener Nombre del coordinador 
    #nombreCoor, sexoCoor = obtener_coordinador()
    #nombreCoor = nombreCoor.upper()
    #sexoCoor = verificarCoordinador(sexoCoor)

    nombreCoor = "DR. GABRIEL EDUARDO SANDOVAL ROMERO" 
    sexoCoor = "EL COORDINADOR"

    pdf=FPDF()

    ingles(pdf,Plan_estudios, Nomb_alu, programa, genero, contador, nombreCoor, sexoCoor, grado, gradoEstudios)
    prorroga(pdf,Plan_estudios, Nomb_alu, No_cuenta_str, clave_str, genero, programa, grado, contador, nombreCoor, sexoCoor, gradoEstudios) 
    dictamen(pdf,Plan_estudios, Nomb_alu, No_cuenta_str, genero, grado, nombreCoor, sexoCoor, gradoEstudios)  
    oficioJurado(pdf, Nomb_alu, Plan_estudios, clave_str, trabajo, presidente, secretario, vocal1, vocal2, vocal3, genero, modalidad, nombreCoor, sexoCoor, programa, gradoEstudios)
    articuloRevista(pdf,No_cuenta_str, Plan_estudios, Nomb_alu, genero, articulo, revista, contador, nombreCoor, sexoCoor, gradoEstudios)
    examenDoctorado(pdf,No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, genero, contador, nombreCoor, sexoCoor, gradoEstudios)
    pdf.output(direccionPDF + "DocumentoDoctorado.pdf", "F")


########## DOCUMENTOS ##########
##########  INGLES  ############
def ingles(pdf, Plan_estudios, Nomb_alu, programa, genero, contador, nombreCoor, sexoCoor, grado, gradoEstudios):
    dia, mes, año = fecha()

    if genero == "el alumno":
        inscrito = "inscrito"
    elif genero == "la alumna":
        inscrito = "inscrita"

    # Agregar una página
    pdf.add_page()

    # Establecer la fuente y el tamaño de la fuente
    pdf.set_font("Arial", size=10)

    # Agregar un encabezado con una imagen y texto
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.image(direccionImagen + "Logo_Unam.jpeg", x=15, y=10, w=46, h=49)  # Agregar imagen
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.set_font("Arial", size=15, style="B")  # Establecer fuente en negrita
    pdf.set_y(15)
    pdf.set_x(68)
    pdf.cell(0, 10, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", 0, 0)  # Texto 1
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.set_font("Arial", size=12, style="B")  # Negrita
    pdf.set_x(72)
    pdf.cell(0, 10, programa, 0, 0)  # Texto 2
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.set_x(107)
    pdf.cell(0, 10, "OF." + contador + "/" + año + "/SEDEPFI-60.2", 0, 1)  # Texto 3

    # Destinatario
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.set_y(80)
    pdf.set_x(10)
    pdf.cell(0, 10, "LIC. DIANA GONZÁLEZ NIETO", 0, 0)
    pdf.cell(0, 5, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECTORA DE CERTIFICACIÓN Y CONTROL DOCUMENTAL", 0, 0)
    pdf.cell(0, 5, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECCIÓN GENERAL DE ADMINISTRACIÓN ESCOLAR", 0, 0)
    pdf.cell(0, 5, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 10, "UNAM.", 0, 0)
    pdf.cell(0, 5, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 10, "Presente", 0, 0)
    pdf.cell(0, 10, "", 0, 1)  # Salto

    # Texto Justificado 
    pdf.set_y(120)
    pdf.set_x(10)
    pdf.multi_cell(
        0, 5,
        "Por este medio comunico a usted que " + genero + " " + Nomb_alu +
        ", " + inscrito + " en " + grado + " EN " + Plan_estudios +
        ", aprobó el siguiente requisito:",
        align="J"
    )
    pdf.cell(0, 13, "", 0, 1)  # Salto
    pdf.cell(0, 10, "0998 Inglés Técnico", 0, 0, 'C')
    pdf.cell(0, 15, "", 0, 1)  # Salto
    pdf.cell(0, 10, "Según consta en los archivos de este Programa.", 0, 0)
    pdf.cell(0, 15, "", 0, 1)  # Salto
    pdf.cell(0, 10, "Sin otro particular, reciba un cordial saludo.", 0, 0)
    pdf.cell(0, 15, "", 0, 1)  # Salto
    pdf.cell(0, 10, "Atentamente", 0, 0)
    pdf.cell(0, 5, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 10, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", 0, 0)
    pdf.cell(0, 5, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 10, "Cd. Universitaria Cd. Mx. a " + dia + " de " + mes + " del " + año + ".", 0, 0)
    pdf.cell(0, 5, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 10, sexoCoor + " DEL PROGRAMA.", 0, 0)
    pdf.cell(0, 25, "", 0, 1)  # Salto
    pdf.set_x(10)
    pdf.cell(0, 30, nombreCoor, 0, 0)

########## PRORROGA ##########
def prorroga(pdf, Plan_estudios, Nomb_alu, No_cuenta_str, clave_str, genero, programa, grado, contador, nombreCoor, sexoCoor, gradoEstudios):
    dia, mes, año = fecha()

    if genero == "el alumno":
        inscrito = "inscrito"
    elif genero == "la alumna":
        inscrito = "inscrita"
    
    # Agregar una página
    pdf.add_page()

    # Establecer la fuente y el tamaño de la fuente
    pdf.set_font("Arial", size=10)

    # Agregar un encabezado con una imagen y texto
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.image(direccionImagen + "Logo_Unam.jpeg", x=15, y=10, w=46, h=49)  # Agregar imagen
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.set_font("Arial", size=15, style="B")
    pdf.set_y(15)
    pdf.set_x(68)
    pdf.cell(0, 10, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", 0, 0)
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_x(72)
    pdf.cell(0, 10, programa, 0, 0)
    pdf.cell(0, 10, "", 0, 1)  # Salto de línea
    pdf.set_x(107)
    pdf.cell(0, 10, "OF." + contador + "/" + año + "/SEDEPFI-60.2", 0, 1)

    # Cuerpo
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "", 0, 1)
    pdf.set_y(80)
    pdf.set_x(10)
    pdf.cell(0, 10, "LIC. DIANA GONZÁLEZ NIETO", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECTORA DE CERTIFICACIÓN Y CONTROL DOCUMENTAL", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECCIÓN GENERAL DE ADMINISTRACIÓN ESCOLAR", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "UNAM.", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "Presente", 0, 0)
    pdf.cell(0, 10, "", 0, 1)

    pdf.set_y(120)
    pdf.set_x(10)
    pdf.multi_cell(0, 5,
        "Con fundamento en lo establecido en el Artículo 22 del Reglamento General de Estudios de Posgrado vigente en el momento de su ingreso, "
        "el Comité Académico le autoriza una prórroga por 6 meses a partir de esta fecha con el fin de que pueda presentar el examen de grado "
        "correspondiente, a " + genero + " " + Nomb_alu + " con número de cuenta " + No_cuenta_str + ", " + inscrito + " en " + grado + " EN " + Plan_estudios +
        " clave " + clave_str + ".", align="J"
    )

    pdf.cell(0, 15, "", 0, 1)
    pdf.cell(0, 10, "Sin más por el momento aprovecho la ocasión para enviarle un cordial saludo", 0, 0)
    pdf.cell(0, 15, "", 0, 1)
    pdf.cell(0, 10, "Atentamente", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "Cd. Universidad Cd. Mx. a " + dia + " de " + mes + " del " + año + ".", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, sexoCoor + " DEL PROGRAMA.", 0, 0)
    pdf.cell(0, 25, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 30, nombreCoor, 0, 0)

########## DICTAMEN ##########
def dictamen(pdf, Plan_estudios, Nomb_alu, No_cuenta_str, genero, grado, nombreCoor, sexoCoor, gradoEstudios):
    dia, mes, año = fecha()

    # Agregar una página
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Encabezado con imagen y textos
    pdf.cell(0, 10, "", 0, 1)
    pdf.image(direccionImagen + "Logo_Unam.jpeg", x=15, y=10, w=43, h=46)
    pdf.set_font("Arial", size=16, style="B")
    pdf.set_x(-30)
    pdf.cell(0, 10, "", 0, 1)
    pdf.cell(0, 5, "Universidad Nacional Autónoma de México", 0, 1, 'R')

    pdf.set_font("Arial", size=13, style="B")
    pdf.set_x(-30)
    pdf.cell(0, 10, "", 0, 1)
    pdf.cell(0, 10, "", 0, 1)
    pdf.cell(0, 5, "Asunto: Dictamen de Suficiencia Académica", 0, 1, 'R')

    # Destinatario
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "", 0, 1)
    pdf.cell(0, 10, "MTRA. IVONNE RAMÍREZ WENCE", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECTORA GENERAL DE ADMINISTRACIÓN ESCOLAR ", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "P R E S E N T E", 0, 0)

    pdf.cell(0, 10, "", 0, 2)
    pdf.cell(0, 5, "No. de cuenta: " + No_cuenta_str, 0, 1, 'R')
    pdf.cell(0, 5, "", 0, 2)

    # Cuerpo del dictamen
    pdf.multi_cell(0, 5,
        "Con objeto de dar cumplimiento a lo estipulado en el artículo 7 inciso b) del Reglamento General de Estudios de Posgrado, me permito informarle que, previa revisión de los documentos comprobatorios de antecedentes académicos y requisitos de ingreso del PROGRAMA DE POSGRADO EN INGENIERÍA, el Comité Académico resolvió emitir opinión favorable de SUFICIENCIA ACADÉMICA, a "
        + genero + " " + Nomb_alu + " para su ingreso al plan de estudios de " + grado + " EN " + Plan_estudios + ".", align="J"
    )

    pdf.cell(0, 15, "", 0, 1)
    pdf.cell(0, 10, "Atentamente", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "\"POR MI RAZA HABLARÁ EL ESPÍRITU\"", 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "Cd. Universidad Cd. Mx. a " + dia + " de " + mes + " del " + año + ".", 0, 0)
    pdf.cell(0, 25, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 30, nombreCoor, 0, 0)
    pdf.cell(0, 5, "", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, sexoCoor + " DEL PROGRAMA.", 0, 0)

    # Pie de página
    pdf.set_y(266)
    pdf.set_x(10)
    pdf.set_font("Arial", size=10, style="B")
    pdf.cell(0, 10, "Anexo: Documentos comprobatorios", 0, 0)

########## ARTICULO DE REVISTA ##########
def articuloRevista(pdf, No_cuenta_str, Plan_estudios, Nomb_alu, genero, articulo, revista, contador, nombreCoor, sexoCoor, gradoEstudios):
    dia, mes, año = fecha()

    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Encabezado
    pdf.cell(0, 10, "", 0, 1)  # salto normal
    pdf.image(direccionImagen + "Logo_Unam.jpeg", x=15, y=10, w=46, h=49)
    pdf.cell(0, 10, "", 0, 1)  # otro salto normal (antes usabas 0.5)
    pdf.set_font("Arial", size=15, style="B")
    pdf.set_y(15)
    pdf.set_x(68)
    pdf.cell(0, 10, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", 0, 0)
    pdf.ln(8)  # espacio fino
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_x(72)
    pdf.cell(0, 10, "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA", 0, 0)
    pdf.ln(8)
    pdf.set_x(107)
    pdf.cell(0, 10, "OF." + contador + "/" + año + "/SEDEPFI-60.2", 0, 1)

    # Destinatario
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "", 0, 1)          # salto normal
    pdf.set_y(80); pdf.set_x(10)
    pdf.cell(0, 10, "LIC. DIANA GONZÁLEZ NIETO", 0, 0)
    pdf.ln(5)
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECTORA DE CERTIFICACIÓN Y CONTROL DOCUMENTAL", 0, 0)
    pdf.ln(5)
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECCIÓN GENERAL DE ADMINISTRACIÓN ESCOLAR", 0, 0)
    pdf.ln(5)
    pdf.set_x(10)
    pdf.cell(0, 10, "UNAM.", 0, 0)
    pdf.ln(10)
    pdf.set_x(10)
    pdf.cell(0, 10, "PRESENTE", 0, 0)
    pdf.ln(0.5)

    # Cuerpo
    pdf.set_y(120); pdf.set_x(10)
    pdf.multi_cell(
        0, 5,
        "Por este medio comunico a usted que " + genero + " " + Nomb_alu +
        ", con número de cuenta " + No_cuenta_str +
        ", inscrito en el DOCTORADO EN INGENIERÍA en el campo del conocimiento " + Plan_estudios +
        ", envió el artículo a la revista internacional arbitrada para su publicación, con lo cual cumple el requisito para obtener el grado correspondiente.",
        align="J"
    )

    pdf.set_xy(10,150);
    pdf.cell(0, 10, "Sin otro particular, reciba un cordial saludo.", 0, 1)
    pdf.set_xy(10,190);
    pdf.cell(0, 10, "Atentamente", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 5, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 10, "Cd. Universidad Cd. Mx. a " + dia + " de " + mes + " del " + año + ".", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 5, sexoCoor + " DEL PROGRAMA.", 0, 1)

    # Firma
    pdf.set_x(10)
    pdf.cell(0, 60, nombreCoor, 0, 0)

########## Examen Docotarado ##########
def examenDoctorado(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, genero, contador, nombreCoor, sexoCoor, gradoEstudios):
    dia, mes, año = fecha()

    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Encabezado
    pdf.cell(0, 10, "", 0, 1)  # salto normal
    pdf.image(direccionImagen + "Logo_Unam.jpeg", x=15, y=10, w=46, h=49)
    pdf.cell(0, 10, "", 0, 0)  # sin salto
    pdf.ln(0.5)                # espacio fino
    pdf.set_font("Arial", size=15, style="B")
    pdf.set_y(15); pdf.set_x(68)
    pdf.cell(0, 10, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", 0, 0)
    pdf.ln(10)
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_x(72)
    pdf.cell(0, 10, "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA", 0, 0)
    pdf.ln(10)
    pdf.set_x(107)
    pdf.cell(0, 10, "OF." + contador + "/" + año + "/SEDEPFI-60.2", 0, 1)

    # Destinatario
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "", 0, 1)  # salto normal
    pdf.set_y(80); pdf.set_x(10)
    pdf.cell(0, 10, "LIC. DIANA GONZÁLEZ NIETO", 0, 0)
    pdf.ln(5)
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECTORA DE CERTIFICACIÓN Y CONTROL DOCUMENTAL", 0, 0)
    pdf.ln(5)
    pdf.set_x(10)
    pdf.cell(0, 10, "DIRECCIÓN GENERAL DE ADMINISTRACIÓN ESCOLAR", 0, 0)
    pdf.ln(5)
    pdf.set_x(10)
    pdf.cell(0, 10, "UNAM.", 0, 0)
    pdf.ln(15)
    pdf.set_x(10)
    pdf.cell(0, 10, "PRESENTE", 0, 0)
    pdf.ln(0.5)

    
    if genero == "el alumno":
        gradoAux = "DOCTOR EN INGENIERÍA"
    elif genero == "la alumna":
        gradoAux = "DOCTORA EN INGENIERÍA"

    # Cuerpo
    pdf.set_y(120); pdf.set_x(10)
    pdf.multi_cell(
        0, 5,
        "Informo a usted, a solicitud de la Dirección General de Administración Escolar, que es opinión del Comité Académico que "
        + genero + " " + Nomb_alu + ", con el número de cuenta " + No_cuenta_str +
        ", puede presentar examen de grado de " + gradoAux +
        " en el campo del conocimiento " + Plan_estudios +
        " plan " + clave_str + ", por haber cumplido con todas las actividades señaladas en el plan de estudios.",
        align="J"
    )

    # Cierres
    pdf.set_xy(10,150);
    pdf.cell(0, 10, "Sin más por el momento, hago propicia la ocasión para enviarle un cordial saludo.", 0, 1)
    pdf.set_xy(10,190);
    pdf.cell(0, 10, "Atentamente", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 5, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 5, "Cd. Universitaria Cd. Mx. a " + dia + " de " + mes + " del " + año + ".", 0, 1)
    pdf.set_x(10)
    pdf.cell(0, 5, sexoCoor + " DEL PROGRAMA.", 0, 1)

    # Firma
    pdf.set_x(10)
    pdf.cell(0, 60, nombreCoor, 0, 0)

########## Oficio Jurado ##########
# helpers 
def _val(x): 
    return "" if x is None else str(x).strip()

def _fila_jurado(pdf, etiqueta, valor, label_w=48, line_h=6):
    pdf.set_x(pdf.l_margin)                  # vuelve al margen izquierdo
    pdf.set_font("Times", size=12)
    pdf.cell(label_w, line_h, etiqueta, ln=0)   # columna fija para la etiqueta
    pdf.multi_cell(0, line_h, _val(valor), align="L")  # el resto para el nombre

def _pie_line(pdf, txt, line_h=6):
    pdf.set_x(pdf.l_margin)           # garantiza ancho > 0
    pdf.multi_cell(0, line_h, txt, align="L")

def oficioJurado(pdf, nombreCompleto, planEstudios, especializacion, trabajo, presidente, secretario, vocal1, vocal2, vocal3, genero, modalidad, nombreCoor, sexoCoor, programa, gradoEstudios):

    if gradoEstudios == "ESPECIALISTA EN ":
        grado = "ESPECIALISTA EN"
        if genero == "el alumno":
            mencionado = "El mencionado alumno"
            interesado = "el interesado"
        elif genero == "la alumna":
            mencionado = "La mencionada alumna"
            interesado = "la interesada"
    elif gradoEstudios == "MAESTRIA EN ":
        if genero == "el alumno":
            grado = "MAESTRO EN"
            mencionado = "El mencionado alumno"
            interesado = "el interesado"
        elif genero == "la alumna":
            grado = "MAESTRA EN"
            mencionado = "La mencionada alumna"
            interesado = "la interesada"
    elif gradoEstudios == "DOCTORADO EN ":
        if genero == "el alumno":
            grado = "DOCTOR EN"
            mencionado = "El mencionado alumno"
            interesado = "el interesado"
        elif genero == "la alumna":
            grado = "DOCTORA EN"
            mencionado = "La mencionada alumna"
            interesado = "la interesada"

    hoy = datetime.today()
    dia = str(hoy.day)
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    mes = meses[hoy.month - 1]
    año = str(hoy.year)

    pdf.set_left_margin(25)    # Márgenes personalizados
    pdf.set_right_margin(25)
    pdf.set_top_margin(20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    pdf.set_font("Times", size=12)

    # 📄 Cuerpo del documento
    pdf.image(direccionImagen + "Logo_Unam.jpeg", x=15, y=15, w=35)

    pdf.set_xy(70, 25)
    pdf.set_font("Times", "B", 12)
    pdf.cell(110, 6, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", ln=True, align="C")

    pdf.set_xy(70, 35)
    pdf.cell(110, 6, programa, ln=True, align="C")

    pdf.set_xy(70, 45)  # <-- agregamos nueva línea 10mm abajo
    pdf.cell(110, 6, "OFICIO DE JURADO", ln=True, align="C")

    pdf.ln(10)  # Dejar espacio después del encabezado

    pdf.set_font("Times", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 6,
        "LIC. DIANA GONZÁLEZ NIETO\n"
        "Directora de Certificación y Control Documental\n"
        "Dirección General de Administración Escolar\n"
        "UNAM\n"
        "Presente", align="J")

    if str(modalidad) == "Tesina" or str(modalidad) == "Tesis" or str(modalidad) == "Reporte de Estancia Industrial o Empresarial" or str(modalidad) == "Informe de Trabajo de Investigación":
        
        if int(especializacion) <= 3999:
            pdf.ln(10)
            pdf.multi_cell(0, 6,
                f"Este Programa informa a usted que {genero} {nombreCompleto}, ha solicitado autorización "
                f"para presentar examen con {modalidad.lower()}, con el fin de obtener el grado de {grado} {planEstudios}, "
                f"plan 11-{especializacion}.", align="J")
        else:
            pdf.ln(10)
            pdf.multi_cell(0, 6,
                f"Este Programa informa a usted que {genero} {nombreCompleto}, ha solicitado autorización "
                f"para presentar examen con {modalidad.lower()}, con el fin de obtener el grado de {grado} {planEstudios}, "
                f"plan {especializacion}.", align="J")

        pdf.ln(5)
        pdf.multi_cell(0, 6,
            f"{mencionado} ha elaborado el trabajo titulado: "
            f"\"{trabajo}\", el cual no tiene valor en créditos académicos.", align="J")
    
    elif str(modalidad) == "Examen General de Conocimiento":
        if int(especializacion) <= 3999:
            pdf.ln(10)
            pdf.multi_cell(0, 6,
                f"Este Programa informa a usted que {genero} {nombreCompleto}, ha solicitado autorización "
                f"para presentar examen general de conocimientos, con el fin de obtener el grado de {grado} {planEstudios}, "
                f"plan 11-{especializacion}.", align="J")
        else:
            pdf.ln(10)
            pdf.multi_cell(0, 6,
                f"Este Programa informa a usted que {genero} {nombreCompleto}, ha solicitado autorización "
                f"para presentar examen general de conocimientos, con el fin de obtener el grado de {grado} {planEstudios}, "
                f"plan {especializacion}.", align="J")
    #AQUI HABRA MAS CODIGO PARA LAS DEMAS MODALIDADES 
     
    pdf.ln(5)
    pdf.multi_cell(0, 6,
        "Tomando en cuenta que " + interesado + " ha cumplido con todos los requisitos que se exigen para sustentar dicho examen, "
        "no hay ningún inconveniente en que se lleve a cabo dicho acto ante el jurado integrado por los profesores:", align="J")
 
    # 👨‍🏫 Lista de jurado
    pdf.ln(5)
    _fila_jurado(pdf, "Presidente:",     presidente)
    _fila_jurado(pdf, "Primer Vocal:",   vocal1)
    _fila_jurado(pdf, "Segundo Vocal:",  vocal2)
    _fila_jurado(pdf, "Tercer Vocal:",   vocal3)
    _fila_jurado(pdf, "Secretario:",     secretario)
    
    # ✍ Pie del documento
    # ✍ Pie del documento (robusto)
    pdf.ln(7)

    # Si estás cerca del final de la página y usas auto_page_break(False), abre nueva página:
    try:
        if pdf.get_y() > pdf.page_break_trigger - 40:  # ~40 mm libres para el pie
            pdf.add_page()
    except Exception:
        pass  # por si la versión no tiene page_break_trigger

    _pie_line(pdf, "A t e n t a m e n t e,")
    _pie_line(pdf, '"POR MI RAZA HABLARÁ EL ESPÍRITU"')  # comillas ASCII (compatibles con Times)
    _pie_line(pdf, f"Cd. Universitaria, {dia} de {mes} de {año}")
    _pie_line(pdf, sexoCoor + " DEL PROGRAMA.")
    pdf.ln(20)
    _pie_line(pdf, nombreCoor)

    if str(modalidad) == "Tesina":
        _pie_line(pdf, "Anexos: votos originales")

########## FUNCIONES AUXILIARES ##########
def _infer_programa(plan_int: int) -> str:
    if 3000 <= plan_int <= 3999: return "Especialidad"
    if 4000 <= plan_int <= 4999: return "Maestria"
    if 5000 <= plan_int <= 5999: return "Doctorado"
    return "Desconocido"

def _listar_registros_por_cuenta(num_cuenta: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                   tituloTesina, tutor, presidente, secretario, vocal1, vocal2, vocal3,
                   sexo, modalidad
            FROM posgrado
            WHERE numeroCuenta = ?
            ORDER BY planEstudios
        """, (num_cuenta,))
        return cur.fetchall()

########## FECHA ##########
def fecha():
    ahora = datetime.now()

    meses = {
        1: "enero",
        2: "febrero",
        3: "marzo",
        4: "abril",
        5: "mayo",
        6: "junio",
        7: "julio",
        8: "agosto",
        9: "septiembre",
        10: "octubre",
        11: "noviembre",
        12: "diciembre",
    }

    dia = str(ahora.day)
    mes = meses[ahora.month]
    año = str(ahora.year)

    return dia, mes, año

########## CONTADOR ##########
CONTADOR_REVISION_ID = 1

def _ensure_contador_revision(conn):
    cur = conn.cursor()
    cur.execute("SELECT valor FROM contador WHERE id = ?", (CONTADOR_REVISION_ID,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO contador (id, valor) VALUES (?, ?)", (CONTADOR_REVISION_ID, 1))
        conn.commit()

def obtener_contador():
    with get_connection() as conn:
        _ensure_contador_revision(conn)
        cur = conn.cursor()
        cur.execute("SELECT valor FROM contador WHERE id = ?", (CONTADOR_REVISION_ID,))
        val = cur.fetchone()[0]
    return int(val)

def incrementar_contador():
    with get_connection() as conn:
        _ensure_contador_revision(conn)
        cur = conn.cursor()
        cur.execute("BEGIN IMMEDIATE")
        cur.execute("SELECT valor FROM contador WHERE id = ?", (CONTADOR_REVISION_ID,))
        actual = int(cur.fetchone()[0])
        nuevo = actual + 1
        cur.execute("UPDATE contador SET valor = ? WHERE id = ?", (nuevo, CONTADOR_REVISION_ID))
        conn.commit()
    return nuevo

def verificarContador(contador):
    
    contador = str(contador)
    
    if len(contador) == 1:
        contador = "00" + contador
    elif len(contador) == 2:
        contador = "0" + contador

    return contador

########## COORDINADOR ########
def obtener_coordinador():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, genero FROM coordinador ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
    if resultado:
        return resultado
    return ("", "")

# 🔵 Actualizar coordinador
def actualizar_coordinador(nombre, genero):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE coordinador SET nombre = ?, genero = ?
            WHERE id = (SELECT id FROM coordinador ORDER BY id DESC LIMIT 1)
        """, (nombre, genero))
        conn.commit()

def verificarCoordinador(sexo):
    if sexo == "M":
        sexo = "EL COORDINADOR" 
    elif sexo == "F":
        sexo = "LA COORDINADORA"
    else:
        sexo = " "

    return sexo


#################################################################################################################################
@revision_bp.route("/", methods=["GET", "POST"])
@permission_required("revision")
def index():
    # --- GET: página ---
    if request.method == "GET":
        return render_template("revision.html")

        # --- POST: SIEMPRE JSON ---
    numDeCuenta = (request.form.get("numDeCuenta") or "").strip()
    sel_id = request.form.get("seleccion_id")  # opcional: llega cuando el usuario eligió un plan

    if not numDeCuenta:
        return jsonify({"success": False, "error": "Falta el número de cuenta."}), 400

    # Si el front ya envió una selección de plan, cargamos ese registro directo
    if sel_id:
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                sel_id_int = int(sel_id)
            except (TypeError, ValueError):
                return jsonify({"success": False, "error": "Selección inválida."}), 400

            cur.execute("""
                SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                    tituloTesina, tutor, presidente, secretario, vocal1, vocal2, vocal3,
                    sexo, modalidad
                FROM posgrado
                WHERE id = ? AND numeroCuenta = ?
                LIMIT 1
            """, (sel_id_int, numDeCuenta))
            datos_alumno = cur.fetchone()

        if not datos_alumno:
            return jsonify({"success": False, "error": "Selección inválida."}), 400

        plan_int = int(datos_alumno[3])
        programa = _infer_programa(plan_int)

    else:
        # Primera consulta: ver cuántos planes tiene
        filas = _listar_registros_por_cuenta(numDeCuenta)
        if not filas:
            return jsonify({"success": False, "no_encontrado": True})

        if len(filas) > 1:
            opciones = []
            programas_set = set()
            for (id_, _, _, planEstudios, especializacion, *_resto) in filas:
                prog = _infer_programa(int(planEstudios))
                programas_set.add(prog)
                opciones.append({
                    "id": id_,
                    "planEstudios": int(planEstudios),
                    "programa": prog,
                    "especializacion": especializacion or ""
                })
            resumen = "Este alumno tiene: " + ", ".join(sorted(programas_set))
            return jsonify({"success": True, "multiples": opciones, "resumen": resumen})

        # Solo 1 → usarlo directo
        datos_alumno = filas[0]
        programa = _infer_programa(int(datos_alumno[3]))


    # --------- A partir de aquí, 'datos_alumno' y 'programa' están definidos ---------
    (id_, numeroCuenta, nombreCompleto, planEstudios, especializacion,
     tituloTesina, tutor, presidente, secretario, vocal1, vocal2, vocal3,
     sexo, modalidad) = datos_alumno

    genero_txt = "el alumno"
    if sexo == 'F':
        genero_txt = "la alumna"
    elif sexo == 'X':
        genero_txt = "elle alumne"

    if programa.lower() == "especialidad":
        especialidad(
            str(numeroCuenta), especializacion, str(planEstudios),
            nombreCompleto, "Especialidad", genero_txt, tituloTesina,
            presidente, secretario, vocal1, vocal2, vocal3, modalidad
        )
        return jsonify({"success": True, "pdf_url": "/revision/ver_pdf/DocumentoEspecialidad.pdf"})

    if programa.lower() == "maestria":
        maestria(
            str(numeroCuenta), especializacion, str(planEstudios),
            nombreCompleto, "Maestria", genero_txt, tituloTesina,
            presidente, secretario, vocal1, vocal2, vocal3, modalidad
        )
        return jsonify({"success": True, "pdf_url": "/revision/ver_pdf/DocumentoMaestria.pdf"})

    if programa.lower() == "doctorado":
        # Por ahora estos campos no se están usando
        articulo = ""
        revista = ""

        doctorado(
            str(numeroCuenta), especializacion, str(planEstudios),
            nombreCompleto, "Doctorado", genero_txt, articulo, revista,
            tituloTesina, presidente, secretario, vocal1, vocal2, vocal3, modalidad
        )
        return jsonify({"success": True, "pdf_url": "/revision/ver_pdf/DocumentoDoctorado.pdf"})

    return jsonify({"success": False, "error": "Programa no reconocido."}), 400

########## ABRIR PDFS ##########
@revision_bp.route("/ver_pdf/<filename>")
@permission_required("revision")
def ver_pdf(filename):
    return send_from_directory("static/Documentos", filename, mimetype="application/pdf", as_attachment=False)

########## CONTADOR ##########
@revision_bp.route("/obtener_contador", methods=["GET"])
@permission_required("revision")
def obtener_contador_api():
    try:
        contador_actual = obtener_contador()
        return jsonify({"contador": contador_actual})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@revision_bp.route("/actualizar_contador", methods=["POST"])
@permission_required("revision")
def actualizar_contador_api():
    try:
        nuevo_valor = request.json.get("nuevoContador")
        if not isinstance(nuevo_valor, int) or nuevo_valor < 1:
            return jsonify({"success": False, "error": "Valor inválido"}), 400

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contador SET valor = ? WHERE id = ?",
                          (nuevo_valor, CONTADOR_REVISION_ID))
            conn.commit()

        return jsonify({"success": True, "contador": nuevo_valor})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@revision_bp.route("/incrementar_contador", methods=["POST"])
@permission_required("revision")
def incrementar_contador_api():
    try:
        nuevo_valor = incrementar_contador()
        return jsonify({"success": True, "contador": nuevo_valor})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

########## Coordinador ##########
@revision_bp.route("/obtener_coordinador", methods=["GET"])
@permission_required("revision")
def obtener_coordinador_api():
    try:
        nombre, genero = obtener_coordinador()
        return jsonify({"nombre": nombre, "genero": genero})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@revision_bp.route("/actualizar_coordinador", methods=["POST"])
@permission_required("revision")
def actualizar_coordinador_api():
    try:
        datos = request.json
        nombre = datos.get("nombre", "").strip()
        genero = datos.get("genero", "").strip()

        if not nombre or not genero:
            return jsonify({"success": False, "error": "Nombre o género inválido"}), 400

        actualizar_coordinador(nombre, genero)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

########## Nuevo Usuario ##########
@revision_bp.route("/registrar_usuario", methods=["POST"])
@permission_required("revision")
def registrar_usuario():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        cuenta = data.get("cuenta", "").strip()
        plan = data.get("plan", "").strip()
        clave = data.get("clave", "").strip()
        programa = data.get("programa", "").strip()
        genero = data.get("genero", "").strip()

        if not (nombre and cuenta and plan and clave and programa and genero):
            return jsonify({"success": False, "error": "Todos los campos son obligatorios."}), 400

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (No_cuenta, Plan_estudios, Clave, Nomb_alu, programa, genero)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cuenta, plan, clave, nombre, programa, genero))
            conn.commit()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@revision_bp.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

