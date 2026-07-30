# Librerías necesarias
from flask import Blueprint, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from datetime import datetime
from fpdf import FPDF, HTMLMixin
from auth import permission_required
from db import get_connection

class MyPDF(FPDF, HTMLMixin):
    pass

examen_bp = Blueprint('examen', __name__, template_folder='../templates')

direccionBase = 'static/BaseDeDatos/basePosgrado.db'
direccionImagen = "static/Imagenes/"
direccionPDF = "static/Documentos/"

############################## FUNCIONES NORMALES SIN HTML ##############################
def opciones_de_Doc(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, opcion, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero):
    pdf = FPDF()
    
    
    if opcion == "2":
        documento_medalla(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad)
    elif opcion == "3":
        documentos_Menciones(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)
    elif opcion == "4": 
        documento_medalla(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad)
        generar_citatorio(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)
        generar_protesta(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad)
        documentos_Menciones(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)
        generar_acta(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)
    elif opcion == "5":  # CITATORIO solo
        generar_citatorio(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)

    elif opcion == "6":  # PROTESTA solo
        generar_protesta(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad)
    
    elif opcion == "7":
        generar_acta(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)

    else:
        print("No existe esa opción")
        return

    # **Guardar el PDF en la carpeta correcta**
    nombre_pdf=pdf.output(direccionPDF + "DocumentoFinal.pdf", "F")
    
    return nombre_pdf  # Devolver el nombre del documento
  
def especialidad(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, opcion, tituloTesina, modalidad):
    encabezado = "PROGRAMA UNICO DE ESPECIALIZACIONES DE INGENIERIA"
    grado = "ESPECIALIDAD"
    coordinadorNombre = "Dra. AIDA HUERTA BARRIENTOS"
    coordinadorGenero = "LA COORDINADORA DEL PROGRAMA"

    opciones_de_Doc(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, opcion, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)

def maestria(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, opcion, tituloTesina, modalidad):
    encabezado = "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
    grado = "MAESTRIA"
    coordinadorNombre = "Dr. GABRIEL EDUARDO SANDOVAL ROMERO"
    coordinadorGenero = "COORDINADOR DEL PROGRAMA"

    opciones_de_Doc(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, opcion, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)

def doctorado(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, opcion, tituloTesina, modalidad):
    encabezado = "PROGRAMA DE MAESTRÍA Y DOCTORADO EN INGENIERÍA"
    grado = "DOCTORADO"
    coordinadorNombre = "Dr. GABRIEL EDUARDO SANDOVAL ROMERO"
    coordinadorGenero = "COORDINADOR DEL PROGRAMA"
    
    opciones_de_Doc(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, opcion, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero)


########## DOCUMENTOS ##########
def generar_citatorio(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero):
    fecha_examen, hora_examen, presidente, vocal1, vocal2, vocal3, secretario, ingreso, termino, promedio, folio, modalidadSede = obtener_examen_por_cuenta(No_cuenta_str, clave_str)
    idPos, numeroCuentaPos, nombreCompletoPos, planEstudiosPos, especializacionPos, tituloTesinaPos, tutorPos, presidentePos, secretarioPos, vocal1Pos, vocal2Pos, vocal3Pos, sexoPos, modalidadPos, sexoTutor = obtnerDatosPosgrado(No_cuenta_str, clave_str)
    
    # 👉 Usar siempre los sinodales de POSGRADO (evitamos depender de examenDatos)
    presidente = presidentePos
    secretario = secretarioPos
    vocal1 = vocal1Pos
    vocal2 = vocal2Pos
    vocal3 = vocal3Pos

    diaEXA, mesEXA, añoEXA = fecha(fecha_examen)
    dia, mes, año = fechaActual()

    Plan_estudios = Plan_estudios.lower().title()
    Plan_estudios = formatear_titulo(Plan_estudios)

    if grado == "ESPECIALIDAD":
        grado = "Especialista en"
    elif grado == "MAESTRIA":
        if genero == "del alumno":
            grado = "Maestro en"
        elif genero == "de la alumna":
            grado = "Maestra en"
    elif grado == "DOCTORADO":
        if genero == "del alumno":
            grado = "Doctor en"
        elif genero == "de la alumna":
            grado = "Doctora en"
 
    # Agregar una página
    pdf.add_page()

    #################CITATORIO#####################
    pdf.image(direccionImagen + "loooogo.jpeg", x=15, y=14, w=31, h=42)  # Agregar imagen

    # Encabezado del documento
    pdf.set_font("Arial", size=14)
    pdf.set_xy(60, 20)
    pdf.multi_cell(130, 5, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="C")

    pdf.set_font("Arial", size=12)
    pdf.set_xy(60, 28)
    pdf.multi_cell(130, 5, encabezado, align="C")

    pdf.set_font("Arial", size=14)
    pdf.set_xy(60, 36)
    pdf.multi_cell(130, 5, "CITATORIO PARA EXAMEN DE GRADO", align="C")

    # Para ESPECIALIDAD
    if grado == "Especialista en":
        
        # 🔼 Subimos este bloque de y=84 a y=69 (3 renglones arriba)
        pdf.set_font("Arial", size=12)
        pdf.set_xy(12, 69)
        pdf.multi_cell(186, 5, "Por la presente se les cita el día " + diaEXA + " de " + mesEXA + " del año " + añoEXA + ", a las " + hora_examen + " hrs., " + modalidadSede + ", para el examen de grado de " + grado + " " + Plan_estudios + " " + genero + ":", align="J")

        pdf.cell(0, 10, "", 0, 1)  # Salto de línea
        pdf.set_font("Arial", size=12, style="B")
        pdf.multi_cell(0, 5, Nomb_alu, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "", 0, 1)  # Salto de línea
        pdf.multi_cell(185, 4.5, "  con el siguiente jurado:", align="J")

        pdf.set_font("Arial", size=12, style="BU")

        # Etiquetas del jurado
        pdf.set_font("Arial", size=12)
        pdf.set_xy(20, 123)
        pdf.multi_cell(0, 5, "PRESIDENTE:", align="L")
        pdf.set_xy(20, 133)
        pdf.multi_cell(0, 5, "SECRETARIO:", align="L")
        pdf.set_xy(20, 143)
        pdf.multi_cell(0, 5, "PRIMER VOCAL:", align="L")
        pdf.set_xy(20, 153)
        pdf.multi_cell(0, 5, "SEGUNDO VOCAL:", align="L")
        pdf.set_xy(20, 163)
        pdf.multi_cell(0, 5, "TERCER VOCAL:", align="L")

        # Nombres del jurado
        pdf.set_xy(62, 123)
        pdf.multi_cell(0, 5, presidente, align="L")
        pdf.set_xy(62, 133)
        pdf.multi_cell(0, 5, secretario, align="L")
        pdf.set_xy(62, 143)
        pdf.multi_cell(0, 5, vocal1, align="L")
        pdf.set_xy(62, 153)
        pdf.multi_cell(0, 5, vocal2, align="L")
        pdf.set_xy(62, 163)
        pdf.multi_cell(0, 5, vocal3, align="L")

        # Firma
        pdf.set_xy(156.5, 113)
        pdf.multi_cell(40, 5, "Firma", align="C")

        # Líneas para firma
        pdf.set_font("Arial", size=12, style="BU")
        pdf.set_xy(102, 123)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 133)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 143)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 153)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 163)
        pdf.multi_cell(0, 5, "                                    ", align="R")

        # Pie de página
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(10, 203)
        pdf.multi_cell(185, 5, "A t e n t a m e n t e", align="C")
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(10, 210)
        pdf.multi_cell(185, 5, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", align="C")
        pdf.set_font("Arial", size=12)
        pdf.set_xy(10, 217)
        pdf.multi_cell(185, 5, "Ciudad Universitaria, a " + dia + " de " + mes + " de " + año, align="C")

        # Firma de la Coordinadora
        pdf.set_font("Arial", size=12, style="BU")
        pdf.set_xy(10, 240)
        pdf.multi_cell(185, 5, "                                                                  ", align="C")
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(10, 247)
        pdf.multi_cell(185, 5, coordinadorNombre, align="C")
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(10, 254)
        pdf.multi_cell(185, 5, coordinadorGenero, align="C")
    
    # PARA MAESTRIA Y DOCTORADO
    elif grado == "Maestro en" or grado == "Maestra en" or grado == "Doctor en" or grado == "Doctora en":
        pdf.ln(10)
        # Estilo normal <b>{mesEXA}</b>
        parrafo_html = (
            f"<p> Por medio de la presente se les cita al examen de grado de <b>{grado.upper()} INGENIERÍA</b> {genero}"
            f" <b>{Nomb_alu},</b> C. de Conocimiento: <b>{Plan_estudios}</b>. </p>"
        )
        pdf.set_font("Arial", size=12)
        pdf.set_xy(12, 69)
        pdf.write_html(parrafo_html)


        if modalidadSede == "en la Facultad de Ingeniería":
            modalidadSede = "Facultad de Ingeniería"
        elif modalidadSede == "en la Aula Virtual Universitaria":
            modalidadSede = "Aula Virtual Universitaria"
        elif modalidadSede == "en el Instituto de Ingeniería":
            modalidadSede = "Instituto de Ingeniería"
        elif modalidadSede == "en el Instituto de Ciencias Aplicadas y Tecnología":
            modalidadSede = "Instituto de Ciencias Aplicadas y Tecnología"
        elif modalidadSede == "en el Instituto de Energías Renovables":
            modalidadSede = "Instituto de Energías Renovables"
        elif modalidadSede == "en el Instituto Mexicano de Tecnología del Agua":
            modalidadSede = "Instituto Mexicano de Tecnología del Agua"


        parrafo_html = (
            f"<p> Lugar: <b>{modalidadSede}</b></p>"
        )
        pdf.set_font("Arial", size=12)
        pdf.set_xy(12, 89)
        pdf.write_html(parrafo_html)

        diaAux, mesAux, anioAux = fecha(fecha_examen)
        
        parrafo_html = (
            f"<p> Fecha y Hora: <b>{diaAux} de {mesAux} de {anioAux} a las {hora_examen} hrs.</b></p>"
        )
        pdf.set_font("Arial", size=12)
        pdf.set_xy(12, 94)
        pdf.write_html(parrafo_html)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "", 0, 1)  # Salto de línea
        pdf.multi_cell(185, 4.5, "   El examen se realizará con el siguiente jurado:", align="J")

        pdf.set_font("Arial", size=12, style="BU")

        # Etiquetas del jurado
        pdf.set_font("Arial", size=12)
        pdf.set_xy(20, 133)
        pdf.multi_cell(0, 5, "PRESIDENTE:", align="L")
        pdf.set_xy(20, 143)
        pdf.multi_cell(0, 5, "SECRETARIO:", align="L")
        pdf.set_xy(20, 153)
        pdf.multi_cell(0, 5, "PRIMER VOCAL:", align="L")
        pdf.set_xy(20, 163)
        pdf.multi_cell(0, 5, "SEGUNDO VOCAL:", align="L")
        pdf.set_xy(20, 173)
        pdf.multi_cell(0, 5, "TERCER VOCAL:", align="L")

        
        # Nombres del jurado
        pdf.set_xy(62, 133)
        pdf.multi_cell(0, 5, modificMombreSinodal(presidentePos), align="L")
        pdf.set_xy(62, 143)
        pdf.multi_cell(0, 5, modificMombreSinodal(secretarioPos), align="L")
        pdf.set_xy(62, 153)
        pdf.multi_cell(0, 5, modificMombreSinodal(vocal1Pos), align="L")
        pdf.set_xy(62, 163)
        pdf.multi_cell(0, 5, modificMombreSinodal(vocal2Pos), align="L")
        pdf.set_xy(62, 173)
        pdf.multi_cell(0, 5, modificMombreSinodal(vocal3Pos), align="L")

        # Firma
        pdf.set_xy(156.5, 123)
        pdf.multi_cell(40, 5, "Firma", align="C")

        # Líneas para firma
        pdf.set_font("Arial", size=12, style="BU")
        pdf.set_xy(102, 133)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 143)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 153)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 163)
        pdf.multi_cell(0, 5, "                                    ", align="R")
        pdf.set_xy(102, 173)
        pdf.multi_cell(0, 5, "                                    ", align="R")

        # Pie de página
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(12, 203)
        pdf.multi_cell(40, 5, "A t e n t a m e n t e", align="C")
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(4, 210)
        pdf.multi_cell(100, 5, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", align="C")
        pdf.set_font("Arial", size=12)
        pdf.set_xy(4, 217)
        pdf.multi_cell(100, 5, "Ciudad Universitaria, a " + dia + " de " + mes + " de " + año, align="C")

        # Firma de la Coordinadora
        pdf.set_font("Arial", size=12, style="BU")
        pdf.set_xy(8, 240)
        pdf.multi_cell(110, 5, "                                                                                     ", align="C")
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(10, 247)
        pdf.multi_cell(100, 5, coordinadorNombre.upper(), align="C")
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(7.5, 254)
        pdf.multi_cell(78, 5, coordinadorGenero, align="C")

def documento_medalla(pdf,No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad):
    
    if grado == "ESPECIALIDAD":
        grado = "ESPECIALISTA EN"
    elif grado == "MAESTRIA":
        grado = "MAESTRÍA EN"
    elif grado == "DOCTORADO":
        grado = "DOCTORADO EN"

    # Agregar una página
    pdf.add_page()

    #enEncabezado del documento
    pdf.set_font("Arial", size=15,style="B" )
    pdf.multi_cell(0, 5,"UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="C")
    pdf.set_font("Arial", size=14, style="B")
    pdf.set_xy(10,15)
    pdf.multi_cell(0, 5, encabezado, align="C")
    
    if grado == "MAESTRÍA EN" or grado == "DOCTORADO EN":
        pdf.cell(0, 7, "", 0, 1) # Salto de línea
        pdf.set_font("Arial", "BU", 12) 
        pdf.multi_cell(185, 5, grado + " INGENIERÍA", align="C")
    elif grado == "ESPECIALISTA EN":
        pdf.cell(0, 7, "", 0, 1) # Salto de línea
        pdf.set_font("Arial", "BU", 12) 
        pdf.multi_cell(185, 5, grado + " " + Plan_estudios + "", align="C")
    
    pdf.cell(0, 7, "", 0, 1) # Salto de línea
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 5, "SINODALES MIEMBROS DEL JURADO DEL EXAMEN", 0, 1,)
    pdf.cell(0, 5, "DE GRADO DE: " + Nomb_alu, 0, 1,)
    
    # Estilo normal
    parrafo_html = (
        f"<p align='justify'>Nuestra Universidad ha otorgado la Medalla <b>Gabino Barreda</b> "
        f"como reconocimiento a los graduados académicamente más distinguidos en cada programa "
        f"de Bachillerato, Licenciatura y Posgrado. A partir de la generación de graduación de "
        f"1996, a los estudiantes graduados académicamente más distinguidos en cada  generación "
        f"se les otorga  la  Medalla <b>Alfonso Caso</b>, quedando la Medalla Gabino Barreda "
        f"para los estudiantes de Bachillerato y Licenciatura."
    )
    pdf.set_font("Arial", size=12)
    pdf.set_xy(10, 50)
    pdf.write_html(parrafo_html)
    
    pdf.cell(0, 8, "", 0, 1)
    pdf.set_font("Arial", size=10, style="B")
    pdf.cell(0, 7, "EL ARTÍCULO 10 DEL REGLAMENTO AL MÉRITO UNIVERSITARIO INDICA LO SIGUIENTE:", 0, 1,)
    pdf.set_xy(15,94)
    pdf.set_font("Arial", size=9.5, style="BI")
    pdf.multi_cell(0, 5, "a)", align="J")
    pdf.set_xy(20,94)
    pdf.multi_cell(0, 5, "Los alumnos de especialización requerirán un promedio de nueve como mínimo, no tener en su historial académico calificaciones de NA (no acreditado), así como haber cubierto todos los créditos y requisitos del plan de estudios en el tiempo estipulado en el mismo, de conformidad con lo señalado en el Reglamento General de Estudios de Posgrado.", align="J")
    pdf.set_xy(15,114)
    pdf.multi_cell(0, 5, "b)", align="J")
    pdf.set_xy(20,114)
    pdf.multi_cell(0, 5, "Los alumnos de maestria requerirán un promedio de nueve como mínimo, no tener en su historial académico calificaciones de NA (no acreditado), así como haber cubierto todos los créditos y requisitos del plan de estudios en el tiempo estipulado en el mismo.Cuando se incluya la realizacion de una tesis, se evaluara su calidad, de confirmidad con lo se;alado en el Reglamento General de Estudios de Posgrado.", align="J")
    pdf.set_xy(15,134)
    pdf.multi_cell(0, 5, "c)", align="J")
    pdf.set_xy(20,134)
    pdf.multi_cell(0, 5, "Los alumnos de doctorado requerirán no tener evaluaciones desfavorables y haber realizado las actividades academicas asignadas en los plazos establecidos; se considerara,ademas, la calidad del trabajo y la tesis doctoral, de confomidad con lo senalado en el Reglamento General de Esttudios de Posgrado.", align="J")
    pdf.set_xy(15,149)
    pdf.multi_cell(0, 5, "d)", align="J")
    pdf.set_xy(20,149)
    pdf.multi_cell(0, 5, "El jurado de examen de grado, debera recomendar su otorgamiento. Cuando el plan de estudios de una especializacion establezca otra forma para el otorgamiento del grado, la instancia que hara la recomendacion sera determinada por el comite academico correspondiente o, a falta de este, por el respectivo consejo tecnico.", align="J")
    pdf.cell(0, 3.5, "", 0, 1) # Salto de línea
    pdf.set_font("Arial", size=9.5, style="B")
    pdf.multi_cell(0, 5, "De acuerdo al inciso \"d\" del mencionado artículo, nos permitimos pedir a ustedes que, a través de la firma del Secretario del Jurado, expresen la recomendación, en su caso, para el otorgamiento de la \"Medalla de Plata Alfonso Caso\" " + genero + " que se gradúa en este examen, indicando la Fundamentación Académica en que se basa su recomendación.", align="J")
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.image(direccionImagen+"boton.PNG", x=30, y=192, w=4, h=4)  # Agregar imagen
    pdf.set_xy(45,192)
    pdf.multi_cell(0, 5, "RECOMIENDA EL OTORGAMIENTO DE LA MEDALLA ALFONSO CASO", align="J")
    pdf.image(direccionImagen+"boton.PNG", x=30, y=200, w=4, h=4)  # Agregar imagen
    pdf.set_xy(45,200)
    pdf.multi_cell(0, 5, "NO RECOMIENDA EL OTORGAMIENTO DE LA MEDALLA ALFONSO CASO", align="J")
    pdf.image(direccionImagen+"RecuadroTex.PNG", x=10, y=210, w=190, h=30)  # Agregar imagen
    pdf.set_xy(15,213)
    pdf.multi_cell(0, 5, "Fundamentación Académica", align="J")
    pdf.set_xy(10,265.5)
    pdf.set_font("Arial", size=8.5, style="BU")
    pdf.multi_cell(0, 5, "                                                                                        ", align="C")
    pdf.set_font("Arial", size=8.5, style="B")
    pdf.set_xy(10,270.5)
    pdf.multi_cell(0, 5, "NOMBRE Y FIRMA DEL SECRETARIO", align="C")

def generar_protesta(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad):  
    fecha_examen, hora_examen, presidente, vocal1, vocal2, vocal3, secretario, ingreso, termino, promedio, folio, modalidadSede = obtener_examen_por_cuenta(No_cuenta_str, clave_str)
    
    diaEXA, mesEXA, añoEXA = fecha(fecha_examen)
    dia, mes, año = fechaActual()

    Plan_estudios = Plan_estudios.lower().title()
    Plan_estudios = formatear_titulo(Plan_estudios)

    if grado == "ESPECIALIDAD":
        grado = "ESPECIALISTA EN"
        if genero == "del alumno":
            genero = "el"
        elif genero == "de la alumna":
            genero = "ella"
    elif grado == "MAESTRIA":
        if genero == "del alumno":
            grado = "MAESTRO EN"
            genero = "el"
        elif genero == "de la alumna":
            grado = "MAESTRA EN"
            genero = "ella"
    elif grado == "DOCTORADO":
        if genero == "del alumno":
            grado = "DOCTOR EN"
            genero = "el"
        elif genero == "de la alumna":
            grado = "DOCTORA EN"
            genero = "ella"

    # -------- PROTESTA --------
    Plan_estudios = Plan_estudios.upper()

    pdf.add_page()

    # Escudo
    pdf.image(direccionImagen+"UNAM_SinTexto.jpeg", x=14, y=11, w=34.5, h=35.5)

    # Encabezados (¡ahora con set_font antes de cada multi_cell!)
    pdf.set_font("Arial", size=14, style="B")
    pdf.set_xy(60, 12)
    pdf.multi_cell(130, 5, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="C")

    pdf.set_font("Arial", size=12)
    pdf.set_xy(60, 20)
    pdf.multi_cell(130, 5, encabezado, align="C")

    pdf.set_font("Arial", size=13.5, style="B")
    pdf.set_xy(60, 41)
    pdf.multi_cell(130, 8, "PROTESTA UNIVERSITARIA", align="C")

    # Nombre y pregunta
    pdf.set_font("Arial", size=12)
    pdf.set_xy(59, 67)
    pdf.multi_cell(0, 5, Nomb_alu, align="L")

    pdf.set_font("Arial", size=11.8, style="B")
    pdf.set_x(59)
    pdf.multi_cell(185, 4.5, "¿PROTESTA USTED?", align="L")

    # Párrafo justificado con parte en negritas (HTML)
    pdf.set_left_margin(20)
    pdf.set_right_margin(15)
    pdf.set_xy(20, 99)

    if grado == "ESPECIALISTA EN":
        parrafo_html = (
        f"<p align='justify'>Ejercer la profesión con la responsabilidad y decisión que {genero} requiere, "
        f"con el respeto, dignidad y ética profesional que de usted espera la Universidad Nacional Autónoma de México, "
        f"que hoy le otorga el grado de <b>{grado} {Plan_estudios}.</b></p>"
    )
    
    elif grado == "MAESTRO EN" or grado == "MAESTRA EN" or grado == "DOCTOR EN" or grado == "DOCTORA EN":
        parrafo_html = (
            f"<p align='justify'>Ejercer la profesión con la responsabilidad y decisión que {genero} requiere, "
            f"con el respeto, dignidad y ética profesional que de usted espera la Universidad Nacional Autónoma de México, "
            f"que hoy le otorga el grado de <b>{grado} INGENIERÍA.</b></p>"
        )

    pdf.set_font("Arial", size=12)  # fuente base para el HTML
    pdf.write_html(parrafo_html)

    # Resto del documento
    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(20, 124)
    pdf.multi_cell(175, 5, "SÍ, PROTESTO. ", align="C")

    pdf.set_font("Arial", size=12)
    pdf.set_xy(20, 139)
    pdf.multi_cell(175, 5, "De no ser así, la universidad, la sociedad y su propia conciencia serán quienes se lo demanden.", align="J")

    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(20, 159)
    pdf.multi_cell(175, 5, "\"POR MI RAZA HABLARÁ EL ESPÍRITU\"", align="C")

    pdf.set_font("Arial", size=12)
    pdf.set_xy(20, 164)
    pdf.multi_cell(175, 5, "Ciudad Universitaria, a " + diaEXA + " de " + mesEXA + " de " + añoEXA, align="C")

    pdf.set_font("Arial", size=12, style="BU")
    pdf.set_xy(20, 184)
    pdf.multi_cell(175, 5, "                                                                                             ", align="C")

    pdf.set_font("Arial", size=12)
    pdf.set_xy(20, 189)
    pdf.multi_cell(175, 5, "EL SECRETARIO", align="C")

    pdf.set_font("Arial", size=12, style="BI")
    pdf.set_xy(20, 224)
    pdf.multi_cell(175, 5, "TESTIGO", align="L")

    pdf.set_font("Arial", size=12, style="BU")
    pdf.set_xy(20, 244)
    pdf.multi_cell(175, 5, "                                                                                             ", align="L")

    pdf.set_font("Arial", size=12)
    pdf.set_xy(20, 249)
    pdf.multi_cell(175, 5, "EL PRESIDENTE DEL JURADO", align="L")

def documentos_Menciones(pdf,No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero):
    fecha_examen, hora_examen, presidente, vocal1, vocal2, vocal3, secretario, ingreso, termino, promedio, folio, modalidadSede = obtener_examen_por_cuenta(No_cuenta_str, clave_str)
    diaEXA, mesEXA, añoEXA= fecha(fecha_examen)
    
    if grado == "ESPECIALIDAD":
        grado = "ESPECIALISTA EN"
    elif grado == "MAESTRIA":
        if genero == "del alumno":
            grado = "MAESTRO EN"
        elif genero == "de la alumna":
            grado = "MAESTRA EN"
    elif grado == "DOCTORADO":
        if genero == "del alumno":
            grado = "DOCTOR EN"
        elif genero == "de la alumna":
            grado = "DOCTORA EN"

    # Agregar una página
    pdf.add_page()

    ###################MENCION###################
    # Establecer la fuente y el tamaño de la fuente
    pdf.set_font("Arial", size=10)

    # Crear margen interior 
    pdf.set_line_width(0.05)
    pdf.line(9, 9, 201, 9)
    pdf.line(9, 9, 9, 288)
    pdf.line(9, 288, 201, 288)
    pdf.line(201, 9, 201, 288)

    # Crear margen central
    pdf.set_line_width(0.12)
    pdf.line(9.5, 9.5, 200.5, 9.5)
    pdf.line(9.5, 9.5, 9.5, 287.5)
    pdf.line(9.5, 287.5, 200.5, 287.5)
    pdf.line(200.5, 9.5, 200.5, 287.5)

    # Crear margen exterior
    pdf.set_line_width(0.05)
    pdf.line(10, 10, 200, 10)
    pdf.line(10, 10, 10, 287)
    pdf.line(10, 287, 200, 287)
    pdf.line(200, 10, 200, 287)

    pdf.image(direccionImagen+"loooogo.jpeg", x=15, y=14, w=31, h=40)

    # Encabezado del documento
    pdf.set_font("Arial", size=14, style="B")
    pdf.set_xy(55, 20)  # ← mueve más a la derecha y hacia arriba si es necesario
    pdf.multi_cell(130, 6, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="C")

    pdf.set_font("Arial", size=11.6, style="B")
    pdf.set_xy(59, 27)
    pdf.multi_cell(180, 5,encabezado, align="J")

    pdf.set_font("Arial", size=12, style="B")
    pdf.set_xy(12,60)
    pdf.cell(0, 5, coordinadorNombre.upper(), 0, 1)
    pdf.set_xy(12,64)
    pdf.cell(0, 5, coordinadorGenero.upper(), 0, 1)
    pdf.set_font("Arial", size=11.7)
    pdf.set_xy(12,69)
    pdf.cell(0, 5, "P R E S E N T E", 0, 1)


    pdf.set_left_margin(12)
    pdf.set_right_margin(12)
    pdf.set_y(84)

    if grado == "ESPECIALISTA EN":
        parrafo_html = (
            f"<p align='justify'>Por la presente le comunicamos que el día {diaEXA} de {mesEXA} del año {añoEXA}, "
            f"a las {hora_examen} horas; tuvo lugar en la Facultad de Ingeniería de la Universidad Nacional Autónoma de México, "
            f"el Examen de Grado de  <b>{grado} {Plan_estudios}.</b></p>"
        )
    elif grado == "MAESTRO EN" or grado == "MAESTRA EN" or grado == "DOCTOR EN" or grado == "DOCTORA EN":
        parrafo_html = (
            f"<p align='justify'>Por la presente le comunicamos que el día {diaEXA} de {mesEXA} del año {añoEXA}, "
            f"a las {hora_examen} horas; tuvo lugar en la Facultad de Ingeniería de la Universidad Nacional Autónoma de México, "
            f"el Examen de Grado de  <b>{grado} INGENIERÍA.</b></p>"
        )

    pdf.set_font("Arial", size=11.8)
    pdf.set_xy(10, 80)
    pdf.write_html(parrafo_html)

    pdf.set_font("Arial", size=11.8)
    pdf.set_xy(12,103)
    pdf.multi_cell(185, 4.5, genero +  ":", align="J")
    pdf.set_font("Arial",style="B")
    pdf.set_xy(38,103)
    pdf.multi_cell(0, 5, Nomb_alu, align="J")
    pdf.set_font("Arial", size=11.8)
    pdf.set_xy(12,113)
    pdf.multi_cell(185, 4.5,"Quien elaboró el trabajo titulado :", align="J")
    pdf.set_xy(12,123)
    pdf.set_font("Arial", "BU", 11.8) 
    pdf.multi_cell(185, 5, tituloTesina, align="C")
    pdf.set_font("Arial", size=11.8)
    pdf.set_xy(12,138)
    pdf.multi_cell(186, 4.5,"De acuerdo a su historial académico y la originalidad del trabajo desarrollado y después de debatir entre nosotros reservada y libremente, resolvimos aprobarlo y otorgarle la", align="J")
    pdf.set_xy(12,155)
    pdf.set_font("Arial", size=11.8, style="B")
    pdf.multi_cell(185, 5, "\"MENCIÓN HONORÍFICA\"", align="C")
    pdf.set_xy(12,165)
    pdf.set_font("Arial", size=10.8)
    pdf.multi_cell(185, 5, "A t e n t a m e n t e", align="C")
    pdf.set_xy(12,172)
    pdf.set_font("Arial", size=11.8, style="B")
    pdf.multi_cell(185, 5, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", align="C")
    pdf.set_xy(12,179)
    pdf.set_font("Arial", size=11.8)
    pdf.multi_cell(185, 5, "Ciudad Universitaria, a "+ diaEXA +" de "+ mesEXA +" de "+ añoEXA, align="C")
    pdf.set_font("Arial", size=11.8, style="BU")
    pdf.set_xy(12,213)# Izquierda
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(76,213)# Centro 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(139,213)# Derecha 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(12,218)
    pdf.set_font("Arial", size=11.8,style="B")
    pdf.multi_cell(60, 5, "PRESIDENTE", align="C")
    pdf.set_xy(76,218)
    pdf.multi_cell(60, 5, "PRIMER VOCAL", align="C")
    pdf.set_xy(139,218)
    pdf.multi_cell(60, 5, "SEGUNDO VOCAL", align="C")
    pdf.set_font("Arial", size=11.8, style="BU")
    pdf.set_xy(12,253)# Izquierda
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(76,253)# Centro 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(139,253)# Derecha 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(12,258)
    pdf.set_font("Arial", size=11.8,style="B")
    pdf.multi_cell(60, 5, "TERCER VOCAL", align="C")
    pdf.set_xy(76,258)
    pdf.multi_cell(60, 5, "SECRETARIO", align="C")
    pdf.set_xy(139,258)
    pdf.multi_cell(60, 5, "Vo. Bo. Coordinador", align="C")


    # Agregar una página
    pdf.add_page()

    
    ###########JUSTIFICACION MENCION##################
    pdf.image(direccionImagen+"loooogo.jpeg", x=15, y=14, w=31, h=40)  # Agregar imagen
    #enEncabezado del documento
    pdf.set_font("Arial", size=15, style="B")
    pdf.set_xy(-156.5,20)
    pdf.multi_cell(180, 5,"UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="J")
    
    pdf.set_font("Arial", size=12.5, style="B")
    pdf.set_xy(-156.5,27)
    pdf.multi_cell(180, 5,encabezado, align="J")

    
    pdf.set_font("Arial", size=12)
    pdf.set_xy(12,59)
    pdf.multi_cell(180, 5, coordinadorNombre.upper(), align="L")
    pdf.set_xy(12,65)
    pdf.multi_cell(180, 5, coordinadorGenero, align="L")
    pdf.set_xy(12,71)
    pdf.multi_cell(180, 5, "UNAM", align="L")
    pdf.set_xy(18,80)
    pdf.multi_cell(180, 5, "Justificación de Mención Honorífica", align="R")
    

    pdf.set_left_margin(12)
    pdf.set_right_margin(12)
    pdf.set_y(90)
    pdf.set_font("Arial", size=11.8)

    if grado == "ESPECIALISTA EN":
        if genero == "de la alumna":
            parrafo_html = (
                f"<p align='justify'>El jurado, integrado por las personas que firman al calce, se reunió el día "
                f"{diaEXA} de {mesEXA} de {añoEXA} a las {hora_examen} horas, con el fin de evaluar el examen que presenta "
                f"la alumna <b>{Nomb_alu}</b> para obtener el grado de <b>{grado} {Plan_estudios}</b>. "
                f"Después de llevarse a cabo el examen, el jurado tuvo a bien <b>APROBARLO CON MENCIÓN HONORÍFICA</b>, por las siguientes razones:</p>"
            )

        elif genero == "del alumno":
            parrafo_html = (
                f"<p align='justify'>El jurado, integrado por las personas que firman al calce, se reunió el día "
                f"{diaEXA} de {mesEXA} de {añoEXA} a las {hora_examen} horas, con el fin de evaluar el examen que presenta "
                f"el alumno <b>{Nomb_alu}</b> para obtener el grado de <b>{grado} {Plan_estudios}</b>. "
                f"Después de llevarse a cabo el examen, el jurado tuvo a bien <b>APROBARLO CON MENCIÓN HONORÍFICA</b>, por las siguientes razones:</p>"
            )
    elif grado == "MAESTRO EN" or grado == "MAESTRA EN" or grado == "DOCTOR EN" or grado == "DOCTORA EN":
        if genero == "de la alumna":
            parrafo_html = (
                f"<p align='justify'>El jurado, integrado por las personas que firman al calce, se reunió el día "
                f"{diaEXA} de {mesEXA} de {añoEXA} a las {hora_examen} horas, con el fin de evaluar el examen que presenta "
                f"la alumna <b>{Nomb_alu}</b> para obtener el grado de <b>{grado} INGENIERÍA</b>. "
                f"Después de llevarse a cabo el examen, el jurado tuvo a bien <b>APROBARLO CON MENCIÓN HONORÍFICA</b>, por las siguientes razones:</p>"
            )

        elif genero == "del alumno":
            parrafo_html = (
                f"<p align='justify'>El jurado, integrado por las personas que firman al calce, se reunió el día "
                f"{diaEXA} de {mesEXA} de {añoEXA} a las {hora_examen} horas, con el fin de evaluar el examen que presenta "
                f"el alumno <b>{Nomb_alu}</b> para obtener el grado de <b>{grado} INGENIERÍA</b>. "
                f"Después de llevarse a cabo el examen, el jurado tuvo a bien <b>APROBARLO CON MENCIÓN HONORÍFICA</b>, por las siguientes razones:</p>"
            )

    pdf.write_html(parrafo_html)


    
    #///////////////////////////////////////////////////////////////
    pdf.set_font("Arial", size=12)
    pdf.set_xy(11,182)
    pdf.multi_cell(180, 5, "A t e n t a m e n t e", align="L")
    pdf.set_xy(11,187)
    pdf.multi_cell(180, 5, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", align="L")
    pdf.set_font("Arial", size=11.8)
    pdf.set_xy(11,192)
    pdf.multi_cell(180, 5, "Cd. Universitaria, a "+ diaEXA +" de "+ mesEXA +" de "+ añoEXA +".", align="L")
    
    #///////////////////////////////////////////////////////////////
    pdf.set_font("Arial", size=11.8, style="BU")
    pdf.set_xy(12,228)# Izquierda
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(76,228)# Centro 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(139,228)# Derecha 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    
    pdf.set_xy(12,233)
    pdf.set_font("Arial", size=11.8)
    pdf.multi_cell(60, 5, "Presidente", align="C")
    pdf.set_xy(76,233)
    pdf.multi_cell(60, 5, "Secretario", align="C")
    pdf.set_xy(139,233)
    pdf.multi_cell(60, 5, "Primer Vocal", align="C")
    
    pdf.set_font("Arial", size=11.8, style="BU")
    pdf.set_xy(12,267)# Izquierda
    pdf.multi_cell(60, 5, "                                         ", align="C")
    pdf.set_xy(76,267)# Centro 
    pdf.multi_cell(60, 5, "                                         ", align="C")
    
    pdf.set_xy(12,272)
    pdf.set_font("Arial", size=11.8)
    pdf.multi_cell(60, 5, "Segundo Vocal", align="C")
    pdf.set_xy(76,272)
    pdf.multi_cell(60, 5, "Tercer Vocal", align="C")

def generar_acta(pdf, No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, encabezado, grado, tituloTesina, modalidad, coordinadorNombre, coordinadorGenero):
    # Recupera todo lo capturado en el modal (incluye los 4 nuevos campos)
    fecha_examen, hora_examen, presidente, vocal1, vocal2, vocal3, secretario, ingreso, termino, promedio, folio, modalidadSede = obtener_examen_por_cuenta(No_cuenta_str, clave_str)
    idPos, numeroCuentaPos, nombreCompletoPos, planEstudiosPos, especializacionPos, tituloTesinaPos, tutorPos, presidentePos, secretarioPos, vocal1Pos, vocal2Pos, vocal3Pos, sexoPos, modalidadPos, sexoTutor = obtnerDatosPosgrado(No_cuenta_str, clave_str)

    if grado == "ESPECIALIDAD":
        grado = "ESPECIALISTA EN"
        if genero == "del alumno":
            genero = "el alumno"
            inscrito = "inscrito"
        elif genero == "de la alumna":
            genero = "la alumna"
            inscrito = "inscrita"
    elif grado == "MAESTRIA":
        if genero == "del alumno":
            genero = "el alumno"
            grado = "MAESTRO EN"
            inscrito = "inscrito"
        elif genero == "de la alumna":
            genero = "la alumna"
            grado = "MAESTRA EN"
            inscrito = "inscrita"
    elif grado == "DOCTORADO":
        if genero == "del alumno":
            genero = "el alumno"
            grado = "DOCTOR EN"
            inscrito = "inscrito"
        elif genero == "de la alumna":
            genero = "la alumna"
            grado = "DOCTORA EN"
            inscrito = "inscrita"


    if sexoTutor == "M":
        sexoTutorAux = "tutor principal el"
    elif sexoTutor == "F":
        sexoTutorAux = "tutora principal la"
    elif sexoTutor == "M,M":
        sexoTutorAux = "fueron tutores el"
    elif sexoTutor == "F,F":
        sexoTutorAux = "fueron tutores la"
    elif sexoTutor == "M,F":
        sexoTutorAux = "fueron tutores el"
    elif sexoTutor == "F,M":
        sexoTutorAux = "fueron tutores la"


    # Normaliza
    diaEXA, mesEXA, añoEXA = fecha(fecha_examen)
    plan_fmt = formatear_titulo(Plan_estudios.lower().title())

    # Agregar una página
    pdf.add_page()

    pdf.image(direccionImagen + "UNAM_SinTexto.jpeg", x=20, y=14, w=25, h=35)  # Agregar imagen

    # Encabezado del documento
    pdf.set_font("Arial", size=12)
    pdf.set_xy(60, 20)
    pdf.multi_cell(130, 5, "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO", align="C")
    
    pdf.set_font("Arial", size=10)
    pdf.set_xy(59.5, 25)
    pdf.multi_cell(130, 5, encabezado, align="C")
    
    pdf.set_font("Times", style="B", size=20)
    pdf.set_xy(46, 32)
    pdf.cell(0, 10, "Acta de Grado Protocolaria", ln=1, align="C")

    
    pdf.set_font("Times", size=11)
    pdf.set_xy(70, 39)
    pdf.cell(0, 6, f"No. de cuenta", align="R")
    pdf.ln(5)
    pdf.set_font("Times", style="B", size=12)
    pdf.cell(0, 6, No_cuenta_str, align="R")
    pdf.ln(10)

    # Estilo normal
    parrafo_html = (
        f"<p align='justify'>En la Universidad Nacional Autónoma de México, {modalidadSede}"
        f", a las <b>{hora_examen}</b> horas del dia <b>{diaEXA}</b> de "
        f"<b>{mesEXA}</b> del año <b>{añoEXA}</b>, {genero}</p>"
    )
    pdf.set_font("Arial", size=11)
    pdf.set_xy(10, 50)
    pdf.write_html(parrafo_html)

    # ==== Óvalo de fotografía (referencia visual, izquierda) ====
    pdf.image(direccionImagen + "Ovalo.png", x=11, y=80, w=40, h=65)

    pdf.set_font("Times", style="B", size=12.3)
    pdf.set_xy(70, 63)
    pdf.cell(0, 10, Nomb_alu, ln=1, align="C")

    parrafo_html = (
        f"<p align='justify'>cuya fotografía aparece al margen, se presentó con el fin de sustentar el examen para obtener el grado de</p>"
    )
    pdf.set_font("Arial", size=11)
    pdf.set_xy(61, 72)
    pdf.write_html(parrafo_html)

    if grado == "ESPECIALISTA EN":
        parrafo_html = (
        f"<p align='center'><b>{grado} {Plan_estudios}</b></p>"
        )   
    elif grado == "MAESTRO EN" or grado == "MAESTRA EN" or grado == "DOCTOR EN" or grado == "DOCTORA EN":
        parrafo_html = (
            f"<p align='center'><b>{grado} INGENIERÍA</b></p>"
        )
    
    pdf.set_font("Times", style="B", size=12)
    pdf.set_xy(65, 85)
    pdf.write_html(parrafo_html)

    if modalidad == "Examen General de Conocimiento":
        parrafo_html = (
            f"<p align='justify'>en su modalidad de graduación por <b>{modalidad.upper()}S</b></p>"
        )
        pdf.set_font("Times", style="B", size=11)
        pdf.set_xy(61, 95)
        pdf.write_html(parrafo_html)

        pdf.ln(5)
    elif modalidad == "Tesina" or modalidad == "Tesis" or modalidad == "Informe de Trabajo de Investigación"or modalidad == "Reporte de Estancia Industrial o Empresarial":
        
        if len(sexoTutor) == 1:
            parrafo_html = (
                f"<p align='justify'>en su modalidad de graduación por <b>{modalidad.upper()}</b> "
                f", con el trabajo titulado: <b>{tituloTesina}</b>, del cual fue {sexoTutorAux} <b>{tutorPos.upper()}.</b>"
                f"</p>"
            )
        else:
            parrafo_html = (
                f"<p align='justify'>en su modalidad de graduación por <b>{modalidad.upper()}</b> "
                f", con el trabajo titulado: <b>{tituloTesina}</b>, del cual fue {sexoTutorAux} <b>{tutorPos.upper()}.</b>"
                f"</p>"
            )
        
        pdf.set_font("Times", style="B", size=11)
        pdf.set_xy(61, 95)
        pdf.write_html(parrafo_html)


    if planEstudiosPos >= 5000:
        parrafo_html = (
            f"<p align='justify'>{genero.capitalize()} cursó sus estudios en el periodo <b>{ingreso}</b> "
            f"a <b>{termino}</b> y cumplió con los requisitos "
            f"académicos señalados en el plan de estudios <b>{clave_str}</b> aprobado por el H. Consejo Universitario.</p>"
        )
        pdf.set_font("Times", style="B", size=11)
        pdf.ln(-2)
        pdf.set_x(61) 
        pdf.write_html(parrafo_html)
    else:
        parrafo_html = (
            f"<p align='justify'>{genero.capitalize()} cursó sus estudios en el periodo <b>{ingreso}</b> "
            f"a <b>{termino}</b>, obtuvo un promedio de <b>{promedio}</b> y cumplió con los requisitos "
            f"académicos señalados en el plan de estudios <b>{clave_str}</b> aprobado por el H. Consejo Universitario.</p>"
        )
        pdf.set_font("Times", style="B", size=11)
        pdf.ln(-2)
        pdf.set_x(61) 
        pdf.write_html(parrafo_html)

    pdf.set_font("Times", size=11)
    pdf.cell(68, 6, "El jurado presente asentó la calificación de", align="C")
  
    #Linea de aprobado
    pdf.set_font("Arial", size=12, style="BU")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "                                                                                                                    ", align="R")
    pdf.set_font("Times", size=9)
    pdf.cell(-142, 0, "(APROBADO, SUSPENDIDO, APROBADO CON MENCIÓN HONORÍFICA)", align="C")

    pdf.set_font("Times", size=11)
    pdf.ln(5)
    pdf.cell(220, 6, "le hizo saber el resultado de su examen y le tomó la Protesta Universitaria", align="C")
   
    pdf.set_font("Times", size=11)
    pdf.ln(5)
    pdf.cell(153, 6, "El jurado estuvo integrado por:", align="C")

    # ========= CUADRO DE SINODALES =========
    # Usamos el mismo arranque X que tus párrafos (≈61) para que alinee visualmente
    LM, RM, W = pdf.l_margin, pdf.r_margin, pdf.w
    UW = W - LM - RM

    y_tabla = pdf.get_y() + 10

    x_nombre = 60          # inicio de la columna 'Nombre' (igual que párrafos)
    w_nombre = 100         # largo de la línea bajo el nombre (ajusta 108–116 si quieres)
    sep_col  = 5           # separación entre columnas (más chico => firma más a la izquierda)
    x_firma  = x_nombre + w_nombre + sep_col
    w_firma  = (LM + UW) - x_firma  # hasta el margen derecho

    # Encabezados centrados
    pdf.set_font("Times", style="B", size=11)
    pdf.set_xy(x_nombre, y_tabla); pdf.cell(w_nombre, 8, "Nombre", 0, 0, "C")
    pdf.set_xy(x_firma,  y_tabla); pdf.cell(w_firma,  8, "Firma",  0, 1, "C")
    y = pdf.get_y()

    pdf.set_line_width(0.3)
    pdf.set_draw_color(0, 0, 0)


    def fila_sinodal(nombre: str, cargo: str, y0: float) -> float:
        """Nombre y cargo alineados a la IZQUIERDA; líneas paralelas en mismos rangos."""
        # Nombre (izquierda)
        pdf.set_font("Arial", size=10.5)
        pdf.set_xy(x_nombre, y0)
        pdf.multi_cell(w_nombre, 3, nombre, border=0, align="L")
        y_nombre_fin = pdf.get_y()

        # Subrayado bajo la primera línea del nombre (mismo rango que la columna 'Nombre')
        y_sub = y0 + 4
        pdf.line(x_nombre, y_sub, x_nombre + w_nombre, y_sub)

        # Cargo (izquierda)
        pdf.set_font("Arial", size=10)
        pdf.set_xy(x_nombre, y0 + 5)
        pdf.cell(w_nombre, 4, cargo, border=0, align="L")

        # Línea de firma (mismo rango que la columna 'Firma'; ligeramente más a la izquierda por sep_col)
        pdf.line(x_firma, y_sub, x_firma + w_firma, y_sub)

        # Altura mínima por fila para ritmo uniforme
        altura_min = 16
        return max(y_nombre_fin, y0 + altura_min)

    # Filas
    if numeroCuentaPos == "524021767":
        y = fila_sinodal(presidentePos, "Presidente", y)
        y = fila_sinodal(vocal1Pos,     "Vocal 1",   y - 4)
        y = fila_sinodal(vocal2Pos,     "Vocal 2",   y - 4)
        y = fila_sinodal(vocal3Pos,     "Vocal 3",   y - 4)
        y = fila_sinodal(secretarioPos, "Secretario",y - 4)
    else:
        y = fila_sinodal(presidentePos, "Presidente", y)
        y = fila_sinodal(vocal1Pos,     "Vocal 1",   y - 1)
        y = fila_sinodal(vocal2Pos,     "Vocal 2",   y - 1)
        y = fila_sinodal(vocal3Pos,     "Vocal 3",   y - 1)
        y = fila_sinodal(secretarioPos, "Secretario",y - 1)

    # Continua debajo del cuadro
    pdf.set_y(y)
    # ========= FIN CUADRO DE SINODALES =========

    if numeroCuentaPos == "524021767":
        pdf.set_font("Arial", size=11, style="B")  
        pdf.set_xy(74, 247)                 
        pdf.multi_cell(100, 0, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", align="C")

        pdf.set_font("Times", size=10.3)
        pdf.set_x(50)
        pdf.multi_cell(160, 10, "El suscrito Coordinador del Programa constató que las firmas corresponden al jurado designado", align="C")
        
        if coordinadorNombre == "Dra. AIDA HUERTA BARRIENTOS":  
            pdf.set_font("Arial", style="B", size=10)
            pdf.set_xy(97, 256)
            pdf.multi_cell(0, 5, coordinadorNombre.upper(), align="L")
        elif coordinadorNombre == "Dr. GABRIEL EDUARDO SANDOVAL ROMERO":
            pdf.set_font("Arial", style="B", size=10)
            pdf.set_xy(85, 264)
            pdf.multi_cell(0, 5, coordinadorNombre.upper(), align="L")

        # Líneas para firma
        pdf.set_font("Arial", size=12, style="BU")
        pdf.set_xy(69, 268)
        pdf.multi_cell(100, 5, "                                                                         ", align="R")
        pdf.set_font("Arial", size=10)
        pdf.set_xy(88, 272)
        pdf.multi_cell(0, 5, "Nombre y firma del Coordinador del Programa", align="L")

    else:
        pdf.set_font("Arial", size=11, style="B")  
        pdf.set_xy(74, 248)                 
        pdf.multi_cell(100, 0, "\"POR MI RAZA HABLARÁ EL ESPIRITU\"", align="C")

        pdf.set_font("Times", size=10.3)
        pdf.set_x(50)
        pdf.multi_cell(160, 10, "El suscrito Coordinador del Programa constató que las firmas corresponden al jurado designado", align="C")
        
        if coordinadorNombre == "Dra. AIDA HUERTA BARRIENTOS":  
            pdf.set_font("Arial", style="B", size=10)
            pdf.set_xy(97, 257)
            pdf.multi_cell(0, 5, coordinadorNombre.upper(), align="L")
        elif coordinadorNombre == "Dr. GABRIEL EDUARDO SANDOVAL ROMERO":
            pdf.set_font("Arial", style="B", size=10)
            pdf.set_xy(85, 257)
            pdf.multi_cell(0, 5, coordinadorNombre.upper(), align="L")

        # Líneas para firma
        pdf.set_font("Arial", size=12, style="BU")
        pdf.set_xy(69, 265)
        pdf.multi_cell(100, 5, "                                                                         ", align="R")
        pdf.set_font("Arial", size=10)
        pdf.set_xy(88, 270)
        pdf.multi_cell(0, 5, "Nombre y firma del Coordinador del Programa", align="L")

    pdf.set_font("Arial", size=9)
    pdf.set_xy(15, 265)
    pdf.multi_cell(0, 5, "No. Folio del Programa", align="L")
    pdf.set_xy(15, 270)
    pdf.multi_cell(0, 5, folio, align="L")

########## FUNCIONES AUXILIARES ##########
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

def verificarPlanEstudios(numero_cuenta):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
              numeroCuenta,
              nombreCompleto,
              planEstudios,
              especializacion,
              presidente,
              secretario,
              vocal1,
              vocal2,
              vocal3,
              sexo,
              tituloTesina,
              modalidad
            FROM posgrado
            WHERE numeroCuenta = ?
            ORDER BY id DESC
            LIMIT 1
        """, (numero_cuenta,))
        fila = cursor.fetchone()

    if not fila:
        return None, "completo"

    try:
        plan = int(fila[2])
    except (TypeError, ValueError):
        return None, "completo"

    if 3000 <= plan <= 5999:
        return fila, "solo_fecha_hora"

    return None, "completo"

def creacionDocumento(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, tituloTesina, modalidad, tipo_documento):
    documentos = []

    if genero == 'M':
        genero = "del alumno"
    elif genero == 'F':
        genero = "de la alumna"
    elif genero == 'X':
        genero = "elle alumne"

    # 📌 **Determinar el tipo de programa**
    programa_normalizado = (programa or "").lower()
    programa_normalizado = (
        programa_normalizado
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    if programa_normalizado == "especialidad":
        funcion_generadora = especialidad
    elif programa_normalizado == "maestria":
        funcion_generadora = maestria
    elif programa_normalizado == "doctorado":
        funcion_generadora = doctorado
    else:
        return jsonify({"success": False, "error": "Programa académico no reconocido."})

    # 📌 **Determinar qué documento solicitar**
    opciones_validas = {"1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7"}
    opcion = opciones_validas.get(tipo_documento)
    
    if not opcion:
        return jsonify({"success": False, "error": "Tipo de documento no válido."})

    funcion_generadora(No_cuenta_str, Plan_estudios, clave_str, Nomb_alu, programa, genero, opcion, tituloTesina, modalidad) 
    documentos.append("DocumentoFinal.pdf")

    url_documento = url_for('static', filename='Documentos/DocumentoFinal.pdf')
    return jsonify({"success": True, "documentos": documentos, "pdf_url": url_documento})

def modificMombreSinodal(cadena):
    titulos_validos = {
        "DR": "Dr.",
        "DRA": "Dra.",
        "ING": "Ing.",
        "ESP": "Esp.",
        "MI": "M.I.",
        "MC": "M.C.",
        "LIC": "Lic.",
        "QFB": "QFB",
        "MTRO": "Mtro.",
        "PROF": "Prof.",
        "MA": "M.A."
    }

    if not cadena:
        return ""

    partes = cadena.strip().split()
    titulo_formateado = []
    nombre_partes = []

    for palabra in partes:
        palabra_sin_punto = palabra.replace(".", "").upper()

        if palabra_sin_punto in titulos_validos:
            titulo_formateado.append(titulos_validos[palabra_sin_punto])
        else:
            nombre_partes.append(palabra.lower().title())

    return " ".join(titulo_formateado + nombre_partes)

def formatear_titulo(texto):
    palabras_excluidas = {"y", "de", "la", "el", "en", "del", "al", "por", "con"}
    palabras = texto.lower().split()
    resultado = []

    for i, palabra in enumerate(palabras):
        if palabra in palabras_excluidas and i != 0:
            resultado.append(palabra)
        else:
            resultado.append(palabra.capitalize())

    return " ".join(resultado)

def guardar_examen_por_cuenta(numero_cuenta, plan_estudios, fecha, hora, ingreso, termino, promedio, folio, modalidad_sede):
    numero_cuenta = (numero_cuenta or "").strip()
    if not numero_cuenta:
        raise ValueError("numeroCuenta vacío")
    if not plan_estudios:
        raise ValueError("planEstudios vacío")
    plan_estudios = int(plan_estudios)

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
          INSERT INTO examenDatos
            (numeroCuenta, planEstudios, fecha, hora, ingreso, termino, promedio, folio, modalidadSede)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(numeroCuenta, planEstudios) DO UPDATE SET
            fecha=excluded.fecha,
            hora=excluded.hora,
            ingreso=excluded.ingreso,
            termino=excluded.termino,
            promedio=excluded.promedio,
            folio=excluded.folio,
            modalidadSede=excluded.modalidadSede
        """, (numero_cuenta, plan_estudios, fecha, hora, ingreso, termino, promedio, folio, modalidad_sede))
        conn.commit()

def obtener_examen_por_cuenta(numero_cuenta, plan_estudios):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
          SELECT fecha, hora, presidente, vocal1, vocal2, vocal3, secretario,
                 ingreso, termino, promedio, folio, modalidadSede
          FROM examenDatos
          WHERE numeroCuenta = ? AND planEstudios = ?
          LIMIT 1
        """, (numero_cuenta, int(plan_estudios)))
        return cur.fetchone()

def _infer_programa(plan: int) -> str:
    if 3000 <= plan <= 3999:
        return "Especialidad"
    if 4000 <= plan <= 4999:
        return "Maestría"
    if 5000 <= plan <= 5999:
        return "Doctorado"
    return "Desconocido"

def _listar_registros_por_cuenta(numero_cuenta: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                   sexo, tituloTesina, modalidad
            FROM posgrado
            WHERE numeroCuenta = ?
            ORDER BY id DESC
        """, (numero_cuenta,))
        return cur.fetchall()

def _obtener_registro_por_id(reg_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                   sexo, tituloTesina, modalidad
            FROM posgrado
            WHERE id = ? LIMIT 1
        """, (reg_id,))
        return cur.fetchone()

def obtnerDatosPosgrado(numero_cuenta: str, plan_estudios):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, numeroCuenta, nombreCompleto, planEstudios, especializacion,
                   tituloTesina, tutor, presidente, secretario, vocal1, vocal2, vocal3,
                   sexo, modalidad, sexoTutor
            FROM posgrado
            WHERE numeroCuenta = ? AND planEstudios = ?
            LIMIT 1
        """, (numero_cuenta, int(plan_estudios)))
        return cursor.fetchone()

def actualizar_jurado_y_tutor(numero_cuenta, plan_estudios, tutor, presidente, secretario, vocal1, vocal2, vocal3):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE posgrado
            SET tutor=?, presidente=?, secretario=?, vocal1=?, vocal2=?, vocal3=?
            WHERE numeroCuenta=? AND planEstudios=?
        """, (tutor, presidente, secretario, vocal1, vocal2, vocal3,
              numero_cuenta, int(plan_estudios)))
        conn.commit()


#################################################################################################################################
@examen_bp.route("/", methods=["GET", "POST"])
@permission_required("examen")
def index():
    if request.method == "POST":
        num_de_cuenta = request.form.get("numeroDeCuenta")
        tipo_documento = request.form.get("tipoDocumento")
        fecha_examen = request.form.get("fechaExamen", "").strip()
        hora_examen = request.form.get("horaExamen", "").strip()
        presidente = request.form.get("presidente", "")
        vocal1 = request.form.get("vocal1", "")
        vocal2 = request.form.get("vocal2", "")
        vocal3 = request.form.get("vocal3", "")
        secretario = request.form.get("secretario", "")
        ingreso   = request.form.get("ingreso", "").strip()
        termino   = request.form.get("termino", "").strip()
        promedio  = request.form.get("promedio", "").strip()
        folio     = request.form.get("folio", "").strip()
        modalidad_sede = (request.form.get("modalidadSede") or "").strip()

        # ➊ Soporte de selección directa por ID (cuando ya eligieron en el modal)
        seleccion_id = request.form.get("seleccion_id")
        if seleccion_id:
            fila = _obtener_registro_por_id(int(seleccion_id))

            if not fila:
                return jsonify(success=False, error="Selección inválida.")

            _id, cuenta, nombre, plan, espec, sexo, titulo, modalidad = fila

            plan = int(plan)
            prog = _infer_programa(plan).lower()

            if prog == "desconocido":
                return jsonify(success=False, error="Plan de estudios no reconocido.")

            # Si solo está seleccionando el plan, revisar si ya tiene datos de examen
            if not tipo_documento:
                row = obtener_examen_por_cuenta(str(cuenta), plan)

                if row:
                    fch, hr, pres, v1, v2, v3, sec, ing, ter, prom, fol, *rest = row
                    completos = all([fch, hr, ing, ter, prom, fol])

                    if completos:
                        return jsonify(
                            success=True,
                            tipo_modal="omit_modal",
                            nombreCompleto=nombre
                        )

                return jsonify(
                    success=True,
                    tipo_modal="solo_fecha_hora",
                    nombreCompleto=nombre
                )

            # Si viene de Confirmar modal, guardar datos de examen del plan seleccionado
            if tipo_documento == "confirmar_modal":
                guardar_examen_por_cuenta(
                    str(cuenta),
                    plan,
                    fecha_examen,
                    hora_examen,
                    ingreso,
                    termino,
                    promedio,
                    folio,
                    modalidad_sede
                )

                return jsonify(success=True)

            # Generar documentos con la fila elegida
            return creacionDocumento(
                str(cuenta), espec or "", str(plan), nombre, prog, sexo,
                titulo or "", modalidad or "", tipo_documento
            )

        # ➋ Detectar múltiples registros por número de cuenta
        filas = _listar_registros_por_cuenta(num_de_cuenta or "")
        if not filas:
            # Mantén tu validación actual si prefieres: aquí de una vez corto
            return jsonify(success=False, error="El número de cuenta no se encuentra en la base de datos. Ingresa uno correcto.")

        if len(filas) > 1 and not tipo_documento:
            opciones = []
            programas_set = set()
            for (rid, cuenta, nombre, plan, espec, sexo, titulo, modalidad) in filas:
                prog = _infer_programa(int(plan))
                programas_set.add(prog)
                opciones.append({
                    "id": rid,
                    "planEstudios": int(plan),
                    "programa": prog,
                    "especializacion": espec or "",
                    "nombre": nombre
                })
            resumen = "Este alumno tiene: " + ", ".join(sorted(programas_set))
            return jsonify(success=True, multiples=opciones, resumen=resumen)


        # Verifica si el plan implica modal reducido o "completo"
        resultadoPlan, resultadoIf = verificarPlanEstudios(num_de_cuenta)

        # =============== VALIDACIÓN (sin elegir documento) ===============
        if not tipo_documento:
            
            row = obtener_examen_por_cuenta(num_de_cuenta, resultadoPlan[2])

            if row:
                # Soporta 11 o 12 columnas
                fch, hr, pres, v1, v2, v3, sec, ing, ter, prom, fol, *rest = row
                completos = all([fch, hr, ing, ter, prom, fol])
                if completos:
                    # ✅ Todo listo → no abrir modal, mostrar botones
                    filas = _listar_registros_por_cuenta(num_de_cuenta)
                    nombre = filas[0][2]  # nombreCompleto

                    return jsonify({
                        "success": True,
                        "tipo_modal": "omit_modal",
                        "nombreCompleto": nombre,
                        "planEstudios": resultadoPlan[2]
                    })
                else:
                    # Faltan datos guardados → abrir modal (según solo_fecha_hora o normal)
                    filas = _listar_registros_por_cuenta(num_de_cuenta)
                    nombre = filas[0][2]  # nombreCompleto

                    return jsonify({
                        "success": True,
                        "tipo_modal": ("solo_fecha_hora" if resultadoIf == "solo_fecha_hora" else "completo"),
                        "nombreCompleto": nombre,
                        "planEstudios": resultadoPlan[2]
                    })
            else:
                if resultadoIf == "completo":
                    return jsonify(success=False, error="El número de cuenta no se encuentra en la base de datos. Ingresa uno correcto.")

                # ✅ aquí sí existe en posgrado (solo_fecha_hora), pero no hay examenDatos todavía
                filas = _listar_registros_por_cuenta(num_de_cuenta)
                nombre = filas[0][2]  # nombreCompleto

                return jsonify(
                    success=True,
                    tipo_modal="solo_fecha_hora",
                    nombreCompleto=nombre,
                    planEstudios=resultadoPlan[2]
                )

        # ============= FIN VALIDACIÓN (sin elegir documento) =============

        # =============== SOLO_FECHA_HORA (generar o guardar) ===============
        if resultadoIf == "solo_fecha_hora":
            # Determinar programa (igual que antes)
            if 3000 <= int(resultadoPlan[2]) <= 3999:
                programa = "especialidad"
            elif 4000 <= int(resultadoPlan[2]) <= 4999:
                programa = "maestria"
            elif 5000 <= int(resultadoPlan[2]) <= 5999:
                programa = "doctorado"
            else:
                return jsonify({"success": False, "error": "Plan de estudios no reconocido."})

            # Si viene un tipo de documento → solo generar PDF
            if tipo_documento in ["1", "2", "3", "4", "5", "6", "7"]:
                return creacionDocumento(
                    str(resultadoPlan[0]), resultadoPlan[3], resultadoPlan[2],
                    resultadoPlan[1], programa, resultadoPlan[9],
                    resultadoPlan[10], resultadoPlan[11], tipo_documento
                )

            # Si NO viene tipo de documento → estamos guardando desde el modal

            # 1) Actualizar POSGRADO (tutor + sinodales) SOLO si venían en el formulario
            tutor_form     = (request.form.get("tutor") or "").strip()
            pres_form      = (request.form.get("presidente") or "").strip()
            sec_form       = (request.form.get("secretario") or "").strip()
            vocal1_form    = (request.form.get("vocal1") or "").strip()
            vocal2_form    = (request.form.get("vocal2") or "").strip()
            vocal3_form    = (request.form.get("vocal3") or "").strip()

            if any([tutor_form, pres_form, sec_form, vocal1_form, vocal2_form, vocal3_form]):
                
                # Obtenemos valores actuales para no borrar nada
                pos = obtnerDatosPosgrado(
                    num_de_cuenta,
                    resultadoPlan[2]
                )

                if pos:
                    _, _, _, _, _, _, tutor_act, pres_act, sec_act, v1_act, v2_act, v3_act, _, _, _ = pos
                else:
                    tutor_act = pres_act = sec_act = v1_act = v2_act = v3_act = ""
    
                nuevo_tutor  = modificMombreSinodal(tutor_form)  if tutor_form  else tutor_act
                nuevo_pres   = modificMombreSinodal(pres_form)   if pres_form   else pres_act
                nuevo_sec    = modificMombreSinodal(sec_form)    if sec_form    else sec_act
                nuevo_v1     = modificMombreSinodal(vocal1_form) if vocal1_form else v1_act
                nuevo_v2     = modificMombreSinodal(vocal2_form) if vocal2_form else v2_act
                nuevo_v3     = modificMombreSinodal(vocal3_form) if vocal3_form else v3_act

                actualizar_jurado_y_tutor(
                    num_de_cuenta,
                    resultadoPlan[2],
                    nuevo_tutor,
                    nuevo_pres,
                    nuevo_sec,
                    nuevo_v1,
                    nuevo_v2,
                    nuevo_v3
                )

            # 2) Guardar SOLO los datos de examen en examenDatos
            guardar_examen_por_cuenta(
                num_de_cuenta, resultadoPlan[2], fecha_examen, hora_examen,
                ingreso, termino, promedio, folio, modalidad_sede
            )
            return jsonify(success=True)


        # Si llega aquí con otro estado, considerar inválido (ya NO existe "completo")
        return jsonify(success=False, error="No se pudo validar el número de cuenta.")

    return render_template("examen.html")

@examen_bp.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@examen_bp.route("/datos", methods=["GET"])
def datos_guardados_examen():
    if "user_id" not in session:
        return jsonify(success=False, error="Sesión expirada.")

    num = (request.args.get("numeroDeCuenta") or "").strip()
    if not num:
        return jsonify(success=False, error="Falta número de cuenta.")

    plan_estudios = (request.args.get("planEstudios") or "").strip()

    if not plan_estudios:
        return jsonify(success=False, error="Falta plan de estudios.")

    row = obtener_examen_por_cuenta(num, plan_estudios)

    if not row:
        return jsonify(success=False, error="No hay datos guardados para este número. Captúralos primero.")

    # examenDatos (nos interesan solo estos campos)
    fch, hr, _, _, _, _, _, ing, ter, prom, fol, *rest = row
    mod_sede = rest[0] if rest else ""

    # posgrado (tutor + sinodales)
    pos = obtnerDatosPosgrado(num, plan_estudios)
    tutor = presidente = secretario = vocal1 = vocal2 = vocal3 = ""
    if pos:
        _, _, _, _, _, _, tutor, presidente, secretario, vocal1, vocal2, vocal3, _, _, _ = pos

    return jsonify(success=True, campos={
        "fechaExamen": fch or "",
        "horaExamen": hr or "",
        "ingreso": ing or "",
        "termino": ter or "",
        "promedio": prom or "",
        "folio": fol or "",
        "modalidadSede": mod_sede,
        "tutor": tutor or "",
        "presidente": presidente or "",
        "vocal1": vocal1 or "",
        "vocal2": vocal2 or "",
        "vocal3": vocal3 or "",
        "secretario": secretario or ""
    })
