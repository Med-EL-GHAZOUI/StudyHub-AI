"""Tests de l'extraction du texte avec numéros de page (T1.2)."""

import pytest

from studyhub.extraction import FormatNonPrisEnCharge, extraire_texte


def test_un_pdf_de_trois_pages_donne_trois_passages_numerotes(creer_pdf):
    contenu = creer_pdf(
        [
            "Chapitre 1 : les vecteurs",
            "Chapitre 2 : les matrices",
            "Chapitre 3 : les déterminants",
        ]
    )

    passages = extraire_texte("cours.pdf", contenu)

    assert [passage.numero for passage in passages] == [1, 2, 3]
    assert "Chapitre 1 : les vecteurs" in passages[0].texte
    assert "Chapitre 2 : les matrices" in passages[1].texte
    assert "Chapitre 3 : les déterminants" in passages[2].texte


def test_une_page_sans_texte_garde_son_numero(creer_pdf):
    contenu = creer_pdf(["Introduction", "", "Conclusion"])

    passages = extraire_texte("cours.pdf", contenu)

    assert [passage.numero for passage in passages] == [1, 2, 3]
    assert passages[1].texte.strip() == ""


def test_l_extension_est_reconnue_sans_tenir_compte_des_majuscules(creer_pdf):
    passages = extraire_texte("COURS.PDF", creer_pdf(["Page unique"]))

    assert len(passages) == 1


@pytest.mark.parametrize("nom_fichier", ["notes.txt", "notes.md"])
def test_un_fichier_texte_donne_un_passage_unique_numerote_1(nom_fichier):
    contenu = "# Notes\nUne définition importante.".encode("utf-8")

    passages = extraire_texte(nom_fichier, contenu)

    assert len(passages) == 1
    assert passages[0].numero == 1
    assert passages[0].texte == "# Notes\nUne définition importante."


def test_un_fichier_texte_windows_ancien_est_lu_correctement():
    contenu = "Matière : mécanique".encode("cp1252")

    passages = extraire_texte("notes.txt", contenu)

    assert passages[0].texte == "Matière : mécanique"


@pytest.mark.parametrize("nom_fichier", ["cours.docx", "cours.pptx", "image.png", "sans_extension"])
def test_un_format_non_pris_en_charge_produit_une_erreur_explicite(nom_fichier):
    with pytest.raises(FormatNonPrisEnCharge, match="Formats acceptés : .md, .pdf, .txt"):
        extraire_texte(nom_fichier, b"contenu quelconque")
