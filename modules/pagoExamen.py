# Libreria Necesaria para conectar PYTHON con HTMLX, y con la Base de Datos
from flask import Blueprint , render_template, request, jsonify, session, redirect, url_for, send_from_directory
from datetime import datetime
from fpdf import FPDF
from auth import permission_required
from config import direccionBase, direccionImagen,direccionPDF
from db import get_connection

pagoExamen_bp = Blueprint('pagoExamen', __name__, template_folder='../templates')

#################################################################################################################################
@pagoExamen_bp.route("/", methods=["GET"])
@permission_required("pago_examen")
def index():
    return render_template("pagoExamen.html")