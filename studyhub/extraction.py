"""Extraction du texte d'un cours en conservant les numéros de page (02 étape 2, T1.2)."""

import io
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

FORMATS_ACCEPTES = (".md", ".pdf", ".txt")  # D18


class FormatNonPrisEnCharge(ValueError):
    """Le fichier importé n'est pas dans un format accepté."""


@dataclass(frozen=True)
class Passage:
    """Texte d'une page de PDF, ou du fichier entier pour un fichier texte."""

    numero: int
    texte: str


def extraire_texte(nom_fichier: str, contenu: bytes) -> list[Passage]:
    """Renvoie le texte du fichier, découpé en passages numérotés à partir de 1.

    Le texte est renvoyé tel qu'extrait, sans correction (D01).
    """
    extension = Path(nom_fichier).suffix.lower()
    if extension not in FORMATS_ACCEPTES:
        raise FormatNonPrisEnCharge(
            f"Le format du fichier « {nom_fichier} » n'est pas pris en charge. "
            f"Formats acceptés : {', '.join(FORMATS_ACCEPTES)}."
        )
    if extension == ".pdf":
        return _extraire_pdf(contenu)
    return [Passage(numero=1, texte=_decoder_texte(contenu))]


def _extraire_pdf(contenu: bytes) -> list[Passage]:
    lecteur = PdfReader(io.BytesIO(contenu))
    return [
        Passage(numero=numero, texte=page.extract_text() or "")
        for numero, page in enumerate(lecteur.pages, start=1)
    ]


def _decoder_texte(contenu: bytes) -> str:
    try:
        return contenu.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Anciens fichiers créés sous Windows.
        return contenu.decode("cp1252")
