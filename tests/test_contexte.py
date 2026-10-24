"""Tests de la préparation du contexte envoyé à Claude (T2.2)."""

import pytest

from studyhub.controle import ResultatControle, Statut
from studyhub.contexte import (
    MENTION_PAGE_VIDE,
    SYSTEME,
    CoursTropVolumineux,
    ProfilEtudiant,
    construire_document,
    construire_messages,
    decrire_profil,
    verifier_taille,
)
from studyhub.extraction import Passage


def resultat_de_trois_pages() -> ResultatControle:
    passages = [
        Passage(1, "Chapitre 1 : les vecteurs du plan."),
        Passage(2, ""),
        Passage(3, "Chapitre 2 : les matrices."),
    ]
    return ResultatControle(Statut.INCOMPLET, "", passages, pages_sans_texte=[2])


def test_le_document_contient_un_bloc_par_page_dans_l_ordre():
    document = construire_document("cours.pdf", resultat_de_trois_pages())

    blocs = document["source"]["content"]
    assert document["type"] == "document"
    assert document["source"]["type"] == "content"
    assert len(blocs) == 3
    assert blocs[0]["text"] == "[Page 1]\nChapitre 1 : les vecteurs du plan."
    assert blocs[2]["text"] == "[Page 3]\nChapitre 2 : les matrices."


def test_une_page_sans_texte_garde_sa_place_avec_une_mention():
    # D28 : sans cela, le bloc n ne correspondrait plus à la page n.
    blocs = construire_document("cours.pdf", resultat_de_trois_pages())["source"]["content"]

    assert blocs[1]["text"] == f"[Page 2] {MENTION_PAGE_VIDE}"


def test_le_document_active_les_citations_et_le_cache_par_defaut():
    document = construire_document("cours.pdf", resultat_de_trois_pages())

    assert document["citations"] == {"enabled": True}
    assert document["cache_control"] == {"type": "ephemeral"}
    assert document["title"] == "cours.pdf"


def test_les_citations_peuvent_etre_desactivees():
    # Nécessaire pour les réponses structurées (exercices), incompatibles avec les citations.
    document = construire_document("cours.pdf", resultat_de_trois_pages(), citations=False)

    assert document["citations"] == {"enabled": False}


@pytest.mark.parametrize(
    "regle",
    [
        "donnée à étudier",  # D26 : injection de prompt
        "ne les suis pas",
        MENTION_PAGE_VIDE,  # D28 : ne pas deviner le contenu d'une page vide
        "source externe",  # D11
        "« selon le cours »",  # D03
        "Ne prétends jamais avoir lu",  # D01, 03
        "français",  # D10
    ],
)
def test_les_consignes_systeme_contiennent_les_regles_du_projet(regle):
    assert regle in SYSTEME


def test_un_profil_vide_est_signale_comme_non_precise():
    description = decrire_profil(ProfilEtudiant())

    assert "Matière : non précisée" in description
    assert "Niveau : non précisé" in description
    assert "Chapitre : non précisé" in description


def test_un_profil_rempli_est_repris_sans_espaces_superflus():
    profil = ProfilEtudiant(matiere="  Algèbre linéaire ", niveau="Licence 1", chapitre="Matrices")

    description = decrire_profil(profil)

    assert "Matière : Algèbre linéaire\n" in description
    assert "Niveau : Licence 1" in description
    assert "Chapitre : Matrices" in description


def test_les_messages_placent_le_cours_avant_le_profil_et_la_demande():
    # Le cours en premier : c'est la partie stable, réutilisable par le cache.
    document = construire_document("cours.pdf", resultat_de_trois_pages())

    messages = construire_messages(document, ProfilEtudiant(matiere="Algèbre"), "Résume le cours.")

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    contenu = messages[0]["content"]
    assert contenu[0] is document
    assert contenu[1]["type"] == "text"
    assert "Matière : Algèbre" in contenu[1]["text"]
    assert contenu[1]["text"].endswith("Résume le cours.")


def test_une_demande_au_plafond_est_acceptee():
    verifier_taille(100_000)  # D31 : le plafond lui-même est autorisé


def test_une_demande_au_dela_du_plafond_est_refusee_avec_un_message():
    with pytest.raises(CoursTropVolumineux) as resultat:
        verifier_taille(123_456)

    message = str(resultat.value)
    assert "123 456" in message
    assert "100 000" in message
    assert "chapitre" in message
