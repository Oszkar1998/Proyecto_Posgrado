"""
pdf_texto.py — Texto compatible con las fuentes de los PDF
==========================================================
Los PDF usan las fuentes base (Arial/Helvetica, Times), que en fpdf2 se
codifican por defecto como latin-1. Con eso, un título copiado de Word con
comillas curvas (“ ”), apóstrofos (’), guiones largos (– —) o símbolos como
Δ hacía fallar el PDF con FPDFUnicodeEncodingException.

Este módulo cambia, para TODOS los PDF del sistema, la forma en que fpdf2
prepara el texto de las fuentes base:
  1. Usa la codificación Windows-1252, que es la que realmente dibujan esas
     fuentes; así las comillas curvas, guiones largos, … y € salen tal cual.
  2. Lo que aún no exista en esas fuentes se reemplaza por algo equivalente
     (Δ → Delta, ≥ → >=, etc.) o, como último recurso, por "?".

Se activa solo con importarlo una vez (Login.py lo hace al arrancar).
El texto con fuentes TTF/Unicode no se toca.
"""

import unicodedata

from fpdf import FPDF

# Símbolos que no existen en Windows-1252 y su equivalente legible
_EQUIVALENTES = {
    "Δ": "Delta", "δ": "delta", "α": "alfa", "β": "beta", "γ": "gamma",
    "λ": "lambda", "μ": "mu", "π": "pi", "σ": "sigma", "Σ": "Sigma",
    "Ω": "Omega", "ω": "omega", "θ": "theta", "φ": "phi", "ε": "epsilon",
    "≥": ">=", "≤": "<=", "≠": "!=", "≈": "~", "→": "->", "←": "<-",
    "√": "raiz de ", "∞": "infinito", "−": "-", "‐": "-", "‑": "-",
    "′": "'", "″": '"', "‹": "<", "›": ">",
    " ": " ", " ": " ", "​": "", "﻿": "",
}


def texto_compatible(texto):
    """Devuelve el texto con solo caracteres que las fuentes base pueden dibujar."""
    if not texto:
        return texto
    resultado = []
    for ch in texto:
        try:
            ch.encode("windows-1252")
            resultado.append(ch)
            continue
        except UnicodeEncodeError:
            pass
        if ch in _EQUIVALENTES:
            resultado.append(_EQUIVALENTES[ch])
            continue
        # Letras con acentos raros (ā, ő, ç̌...) -> letra base
        base = "".join(c for c in unicodedata.normalize("NFKD", ch)
                       if not unicodedata.combining(c))
        try:
            base.encode("windows-1252")
            resultado.append(base or "?")
        except UnicodeEncodeError:
            resultado.append("?")
    return "".join(resultado)


def _normalize_text(self, text):
    if not self.is_ttf_font and self.core_fonts_encoding:
        # fpdf2 espera la cadena "decodificada como latin-1" de los bytes finales
        return texto_compatible(text).encode("windows-1252").decode("latin-1")
    return text


if not getattr(FPDF, "_posgrado_texto_compatible", False):
    FPDF.normalize_text = _normalize_text
    FPDF._posgrado_texto_compatible = True
