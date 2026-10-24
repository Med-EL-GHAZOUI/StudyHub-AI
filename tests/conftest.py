"""Outils partagés par les tests (D20 : les PDF de test sont générés, aucun cours réel)."""

import pytest
from fpdf import FPDF


@pytest.fixture
def creer_pdf():
    """Renvoie une fonction qui crée un PDF avec une page par texte donné.

    Un texte vide produit une page sans texte, comme une page scannée.
    """

    def _creer(textes_des_pages: list[str]) -> bytes:
        pdf = FPDF()
        pdf.set_font("Helvetica", size=12)
        for texte in textes_des_pages:
            pdf.add_page()
            if texte:
                pdf.multi_cell(0, 10, texte)
        return bytes(pdf.output())

    return _creer
