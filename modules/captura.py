
# Libreria Necesaria para conectar PYTHON con HTMLX, y con la Base de Datos
from flask import Blueprint , render_template, request, jsonify, session, redirect, url_for, send_from_directory
import sqlite3
from datetime import datetime
from fpdf import FPDF
import os
from auth import permission_required
from config import direccionBase, direccionImagen,direccionPDF

captura_bp = Blueprint('captura', __name__, template_folder='../templates')

#################################################################################################################################
@captura_bp.route("/", methods=["GET"])
@permission_required("captura")
def index():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("captura.html")

@captura_bp.route("/votos", methods=["GET"])
def captura_votos():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("captura_votos.html")

@captura_bp.route("/actasGrado", methods=["GET"])
def actas_grado():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("actasGrado.html")

