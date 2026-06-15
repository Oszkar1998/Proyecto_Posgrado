# Libreria Necesaria para conectar PYTHON con HTMLX, y con la Base de Datos
from flask import Blueprint , render_template, request, jsonify, session, redirect, url_for, send_from_directory
import sqlite3
from datetime import datetime
from fpdf import FPDF
from auth import permission_required
from config import direccionBase, direccionImagen,direccionPDF

pagoExamen_bp = Blueprint('pagoExamen', __name__, template_folder='../templates')

#################################################################################################################################
@pagoExamen_bp.route("/", methods=["GET"])
@permission_required("pago_examen")
def index():
    return render_template("pagoExamen.html")