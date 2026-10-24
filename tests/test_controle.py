"""Tests du contrôle de l'extraction (T1.3, règles de 02 §4)."""

import pytest

from studyhub.controle import TAILLE_MAX_OCTETS, Statut, controler_fichier

TEXTE_SUFFISANT = "Une page de cours avec assez de texte."


def test_un_pdf_lisible_est_valide(creer_pdf):
    resultat = controler_fichier("cours.pdf", creer_pdf([TEXTE_SUFFISANT, TEXTE_SUFFISANT]))

    assert resultat.statut is Statut.VALIDE
    assert resultat.message == ""
    assert len(resultat.passages) == 2
    assert resultat.pages_sans_texte == []


def test_un_fichier_vide_est_illisible():
    resultat = controler_fichier("cours.pdf", b"")

    assert resultat.statut is Statut.ILLISIBLE
    assert "vide" in resultat.message
    assert "autre fichier" in resultat.message


def test_un_pdf_sans_aucun_texte_est_illisible(creer_pdf):
    resultat = controler_fichier("scan.pdf", creer_pdf(["", ""]))

    assert resultat.statut is Statut.ILLISIBLE
    assert "scanné" in resultat.message
    assert resultat.pages_sans_texte == [1, 2]


def test_un_pdf_avec_une_page_sans_texte_est_incomplet(creer_pdf):
    resultat = controler_fichier("cours.pdf", creer_pdf([TEXTE_SUFFISANT, "", TEXTE_SUFFISANT]))

    assert resultat.statut is Statut.INCOMPLET
    assert resultat.pages_sans_texte == [2]
    assert "page 2. Cette page est peut-être scannée" in resultat.message
    assert len(resultat.passages) == 3  # le texte lisible reste disponible


def test_plusieurs_pages_sans_texte_sont_toutes_listees(creer_pdf):
    resultat = controler_fichier(
        "cours.pdf", creer_pdf([TEXTE_SUFFISANT, "", TEXTE_SUFFISANT, ""])
    )

    assert resultat.pages_sans_texte == [2, 4]
    assert "pages 2, 4. Ces pages sont peut-être scannées" in resultat.message


def test_une_page_de_moins_de_20_caracteres_compte_comme_sans_texte():
    # D22 : seuil de 20 caractères, testé sur un fichier texte pour une longueur exacte.
    assert controler_fichier("notes.txt", b"a" * 19).statut is Statut.ILLISIBLE
    assert controler_fichier("notes.txt", b"a" * 20).statut is Statut.VALIDE


def test_les_espaces_ne_comptent_pas_comme_du_texte():
    resultat = controler_fichier("notes.txt", b" \n\t" * 30)

    assert resultat.statut is Statut.ILLISIBLE


def test_un_fichier_trop_volumineux_est_refuse():
    resultat = controler_fichier("cours.pdf", b"0" * (TAILLE_MAX_OCTETS + 1))

    assert resultat.statut is Statut.REFUSE
    assert "20 Mo" in resultat.message
    assert resultat.passages == []


def test_un_format_non_pris_en_charge_est_refuse():
    resultat = controler_fichier("cours.docx", b"contenu quelconque")

    assert resultat.statut is Statut.REFUSE
    assert "Formats acceptés" in resultat.message


@pytest.mark.parametrize(
    "contenu",
    [b"ceci n'est pas un pdf", b"%PDF-1.4\n"],
    ids=["pas_un_pdf", "entete_seul"],
)
def test_un_pdf_corrompu_est_illisible(contenu):
    resultat = controler_fichier("cours.pdf", contenu)

    assert resultat.statut is Statut.ILLISIBLE
    assert "endommagé" in resultat.message


def test_un_pdf_tronque_est_illisible(creer_pdf):
    complet = creer_pdf([TEXTE_SUFFISANT, TEXTE_SUFFISANT])

    resultat = controler_fichier("cours.pdf", complet[: len(complet) // 2])

    assert resultat.statut is Statut.ILLISIBLE
    assert "endommagé" in resultat.message


def test_un_texte_dans_un_encodage_inconnu_est_illisible():
    # 0x81 et 0x8D ne sont valides ni en UTF-8 ni en cp1252.
    resultat = controler_fichier("notes.txt", b"Texte \x81\x8d illisible et assez long")

    assert resultat.statut is Statut.ILLISIBLE
    assert "UTF-8" in resultat.message
