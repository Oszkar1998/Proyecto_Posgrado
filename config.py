
# ============================================================
# config.py — Configuración central del proyecto
# Importar en cada módulo con: from config import direccionBase, direccionImagen, direccionPDF
# ============================================================
import os

# Carpeta donde está este archivo (la raíz del proyecto).
# Así las rutas funcionan aunque el servidor se arranque desde otra carpeta.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base de datos: FUERA de static/ para que Flask no la pueda servir por internet.
direccionBase = os.path.join(BASE_DIR, "instance", "basePosgrado.db")

# Recursos estáticos
direccionImagen = "static/Imagenes/"

# Carpetas de documentos generados
direccionPDF           = "static/Documentos/"
DIRECCION_PDF_GRADO    = "static/DocumentosGenerados/"   # Exclusivo de dgaeGrado
