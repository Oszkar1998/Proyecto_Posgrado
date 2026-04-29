# Libreria Necesaria para conectar PYTHON con HTMLX, y con la Base de Datos
from flask import Blueprint , render_template, request, jsonify, session, redirect, url_for, send_from_directory
import sqlite3
from datetime import datetime
from fpdf import FPDF
from auth import permission_required

pagoExamen_bp = Blueprint('pagoExamen', __name__, template_folder='../templates')

# Variables Globales 
direccionBase = 'static/BaseDeDatos/basePosgrado.db'
direccionImagen = "static/Imagenes/"
direccionPDF = "static/Documentos/"

@pagoExamen_bp.route("/", methods=["GET"])
@permission_required("pago_examen")
def index():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("pagoExamen.html")