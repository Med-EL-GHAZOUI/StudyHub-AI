"""Tests de l'interface Streamlit (T1.1, T1.4, T2.1 à T2.3)."""

from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from studyhub.llm import ErreurClaude
from studyhub.resume import Resume, Segment

APP_PATH = Path(__file__).parent.parent / "app.py"
TEXTE_SUFFISANT = "Une page de cours avec assez de texte."


def lancer_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH)).run()


def importer(app: AppTest, nom_fichier: str, contenu: bytes) -> AppTest:
    app.file_uploader[0].set_value((nom_fichier, contenu, "application/octet-stream"))
    return app.run()


def textes(elements) -> list[str]:
    return [element.value for element in elements]


def test_la_page_affiche_le_titre_studyhub_ai():
    app = lancer_app()

    assert not app.exception
    assert app.title[0].value == "StudyHub AI"


def test_la_zone_d_import_n_accepte_que_les_formats_retenus():
    # Streamlit refuse lui-même les autres extensions avant d'appeler notre code :
    # le statut « refusé » de controle.py reste une seconde barrière (tests/test_controle.py).
    app = lancer_app()

    assert sorted(app.file_uploader[0].allowed_type) == [".md", ".pdf", ".txt"]


def test_un_pdf_valide_affiche_nom_pages_statut_et_apercu(creer_pdf):
    app = importer(lancer_app(), "cours.pdf", creer_pdf(["Chapitre 1 : les vecteurs du plan", TEXTE_SUFFISANT]))

    assert not app.exception
    assert app.subheader[0].value == "cours.pdf"
    assert any("Pages : 2" in texte for texte in textes(app.markdown))
    assert "texte a été extrait de toutes les pages" in app.success[0].value
    assert [expander.label for expander in app.expander] == ["Page 1", "Page 2"]
    assert "Chapitre 1 : les vecteurs du plan" in app.expander[0].text[0].value


def test_un_cours_lisible_affiche_le_formulaire_de_contexte(creer_pdf):
    # 01 §3 : matière, niveau et chapitre étudiés.
    app = importer(lancer_app(), "cours.pdf", creer_pdf([TEXTE_SUFFISANT]))

    assert [champ.label for champ in app.text_input] == [
        "Matière",
        "Niveau d'étude",
        "Chapitre étudié (facultatif)",
    ]


def test_le_formulaire_garde_les_valeurs_saisies(creer_pdf):
    app = importer(lancer_app(), "cours.pdf", creer_pdf([TEXTE_SUFFISANT]))

    app.text_input(key="matiere").input("Algèbre linéaire").run()

    assert app.text_input(key="matiere").value == "Algèbre linéaire"


@pytest.fixture
def cle_configuree(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-cle-de-test-secrete")
    monkeypatch.setattr("studyhub.llm.CHEMIN_ENV", tmp_path / ".env")


def bouton_resume(app: AppTest):
    return next(bouton for bouton in app.button if bouton.label == "Générer le résumé")


def test_sans_cle_le_bouton_de_resume_est_desactive(monkeypatch, tmp_path, creer_pdf):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("studyhub.llm.CHEMIN_ENV", tmp_path / ".env")

    app = importer(lancer_app(), "cours.pdf", creer_pdf([TEXTE_SUFFISANT]))

    assert bouton_resume(app).disabled


def test_le_resume_genere_s_affiche_avec_ses_pages_et_avertissements(cle_configuree, creer_pdf):
    resume = Resume(
        segments=[Segment("Un vecteur a une norme.", (1,))],
        avertissements=["Le résumé cite la page 2, dont le texte n'a pas été extrait."],
    )
    app = importer(lancer_app(), "cours.pdf", creer_pdf([TEXTE_SUFFISANT]))

    with patch("studyhub.resume.generer_resume", return_value=resume) as generer:
        bouton_resume(app).click().run()

    assert not app.exception
    generer.assert_called_once()
    assert any("Un vecteur a une norme. *(p. 1)*" in texte for texte in textes(app.markdown))
    assert any("page 2" in texte for texte in textes(app.warning))


def test_le_resume_reste_affiche_apres_une_autre_action(cle_configuree, creer_pdf):
    resume = Resume(segments=[Segment("Un vecteur a une norme.", (1,))], avertissements=[])
    app = importer(lancer_app(), "cours.pdf", creer_pdf([TEXTE_SUFFISANT]))
    with patch("studyhub.resume.generer_resume", return_value=resume):
        bouton_resume(app).click().run()

    app.text_input(key="matiere").input("Algèbre").run()

    assert any("Un vecteur a une norme." in texte for texte in textes(app.markdown))


def test_une_erreur_de_generation_s_affiche_en_francais(cle_configuree, creer_pdf):
    app = importer(lancer_app(), "cours.pdf", creer_pdf([TEXTE_SUFFISANT]))

    erreur = ErreurClaude("Trop de demandes en peu de temps.")
    with patch("studyhub.resume.generer_resume", side_effect=erreur):
        bouton_resume(app).click().run()

    assert not app.exception
    assert "Trop de demandes" in app.error[0].value


def test_un_cours_illisible_n_affiche_pas_le_formulaire(creer_pdf):
    app = importer(lancer_app(), "scan.pdf", creer_pdf(["", ""]))

    assert len(app.text_input) == 0


def test_l_apercu_affiche_le_texte_brut_sans_mise_en_forme():
    # D01 : un texte qui ressemble à du Markdown doit rester identique.
    contenu = "# Titre\n**gras** et _italique_, assez long."

    app = importer(lancer_app(), "notes.md", contenu.encode("utf-8"))

    assert app.expander[0].text[0].value == contenu


def test_un_pdf_incomplet_affiche_un_avertissement_et_marque_la_page(creer_pdf):
    app = importer(lancer_app(), "cours.pdf", creer_pdf([TEXTE_SUFFISANT, "", TEXTE_SUFFISANT]))

    assert "page 2" in app.warning[0].value
    assert [expander.label for expander in app.expander] == [
        "Page 1",
        "Page 2 — aucun texte extrait",
        "Page 3",
    ]


def test_un_fichier_illisible_affiche_une_erreur_sans_apercu(creer_pdf):
    app = importer(lancer_app(), "scan.pdf", creer_pdf(["", ""]))

    assert "scanné" in app.error[0].value
    assert len(app.expander) == 0


def test_un_fichier_vide_affiche_une_erreur():
    app = importer(lancer_app(), "cours.pdf", b"")

    assert "vide" in app.error[0].value
    assert not app.exception


def test_sans_cle_d_api_la_barre_laterale_l_indique(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("studyhub.llm.CHEMIN_ENV", tmp_path / ".env")

    app = lancer_app()

    assert not app.exception
    assert "clé d'API Anthropic est absente" in app.sidebar.warning[0].value


def test_avec_cle_d_api_la_barre_laterale_le_confirme(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-cle-de-test-secrete")
    monkeypatch.setattr("studyhub.llm.CHEMIN_ENV", tmp_path / ".env")

    app = lancer_app()

    assert "configurée" in app.sidebar.success[0].value
    assert "sk-ant-cle-de-test-secrete" not in app.sidebar.success[0].value


def test_une_erreur_inattendue_affiche_un_message_generique():
    # D24 : filet de sécurité.
    with patch("studyhub.controle.extraire_texte", side_effect=RuntimeError("panne imprévue")):
        app = importer(lancer_app(), "cours.pdf", b"contenu quelconque")

    assert not app.exception
    assert "erreur inattendue" in app.error[0].value
    assert "panne imprévue" not in app.error[0].value
