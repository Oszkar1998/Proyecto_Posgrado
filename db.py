"""
db.py — Gestión centralizada de conexiones SQLite
==================================================
Uso en cualquier módulo:

    from db import get_connection

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posgrado WHERE numeroCuenta = ?", (cuenta,))
        fila = cursor.fetchone()
    # La conexión se cierra automáticamente aquí,
    # incluso si ocurre un error dentro del bloque.
"""

import sqlite3
from contextlib import contextmanager
from config import direccionBase

"""
    Abre una conexión SQLite y la cierra siempre al salir del bloque,
    incluso si ocurre una excepción durante la consulta.
"""

@contextmanager
def get_connection():
    conn = sqlite3.connect(direccionBase, timeout=10)
    try:
        yield conn
    finally:
        conn.close()