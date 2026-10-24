"""Vérifie que l'interface se lance sans erreur (T1.1)."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).parent.parent / "app.py"


def test_la_page_affiche_le_titre_studyhub_ai():
    app = AppTest.from_file(str(APP_PATH)).run()

    assert not app.exception
    assert app.title[0].value == "StudyHub AI"
