"""
pdf_temp.py — PDFs temporales con nombre único
==============================================
Evita que dos usuarios que generan documentos al mismo tiempo se
sobrescriban el archivo (antes todos usaban nombres fijos como
"DocumentoFinal.pdf").

Uso en un módulo:

    from pdf_temp import guardar_pdf_temporal, enviar_pdf_temporal

    nombre = guardar_pdf_temporal(pdf, "Revision")      # -> "tmp_Revision_<uuid>.pdf"
    return jsonify(success=True, pdf_url=f"/revision/ver_pdf/{nombre}")

    @bp.route("/ver_pdf/<filename>")
    @permission_required("revision")
    def ver_pdf(filename):
        return enviar_pdf_temporal(filename)
"""

import glob
import os
import re
import time
import uuid

from flask import abort, send_from_directory

from config import direccionPDF

# Tiempo que se conserva un PDF temporal en disco (segundos).
# Da margen para recargar la pestaña o descargar el archivo.
EDAD_MAXIMA = 30 * 60

# tmp_<Prefijo>_<32 hex>.pdf  — el uuid4 completo hace imposible adivinar el nombre.
_PATRON_NOMBRE = re.compile(r"^tmp_[A-Za-z0-9]+_[0-9a-f]{32}\.pdf$")


def limpiar_pdfs_temporales(edad_maxima=EDAD_MAXIMA):
    """Borra los PDFs temporales más viejos que edad_maxima."""
    limite = time.time() - edad_maxima
    for ruta in glob.glob(os.path.join(direccionPDF, "tmp_*.pdf")):
        try:
            if os.path.getmtime(ruta) < limite:
                os.remove(ruta)
        except OSError:
            # Otro proceso pudo borrarlo primero; no es un error.
            pass


def guardar_pdf_temporal(pdf, prefijo):
    """Guarda el objeto FPDF con un nombre único y devuelve solo el nombre."""
    prefijo = re.sub(r"[^A-Za-z0-9]", "", prefijo) or "Documento"
    nombre = f"tmp_{prefijo}_{uuid.uuid4().hex}.pdf"
    pdf.output(os.path.join(direccionPDF, nombre), "F")
    limpiar_pdfs_temporales()
    return nombre


def enviar_pdf_temporal(filename):
    """Entrega un PDF temporal; solo acepta nombres creados por guardar_pdf_temporal."""
    if not _PATRON_NOMBRE.match(filename or ""):
        abort(404)
    return send_from_directory(direccionPDF, filename,
                               mimetype="application/pdf", as_attachment=False)
