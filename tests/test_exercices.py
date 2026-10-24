"""Tests des exercices (T2.4). Aucun appel réel à l'API (D32)."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from studyhub.contexte import SYSTEME, CoursTropVolumineux, ProfilEtudiant
from studyhub.controle import ResultatControle, Statut
from studyhub.exercices import DEMANDE_EXERCICES, NIVEAUX, Exercice, generer_exercices
from studyhub.extraction import Passage
from studyhub.llm import ErreurClaude


def cours_de_trois_pages() -> ResultatControle:
    passages = [
        Passage(1, "Chapitre 1 : les vecteurs du plan."),
        Passage(2, ""),
        Passage(3, "Chapitre 2 : les matrices."),
    ]
    return ResultatControle(Statut.INCOMPLET, "", passages, pages_sans_texte=[2])


def exercice_json(niveau: str, pages=(1,), objectif="Objectif") -> dict:
    return {
        "niveau": niveau,
        "objectif": objectif,
        "chapitre": "Chapitre 1",
        "enonce": f"Énoncé {niveau}",
        "solution": f"Solution {niveau}",
        "pages": list(pages),
    }


def client_simule(exercices: list[dict] | None = None, texte: str | None = None, nb_tokens=5_000):
    if texte is None:
        texte = json.dumps({"exercices": exercices or []}, ensure_ascii=False)
    client = MagicMock()
    client.beta.messages.count_tokens.return_value = SimpleNamespace(input_tokens=nb_tokens)
    client.beta.messages.create.return_value = SimpleNamespace(
        stop_reason="end_turn",
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=texte)],
    )
    return client


def trois_niveaux() -> list[dict]:
    return [exercice_json(niveau) for niveau in NIVEAUX]


@pytest.mark.parametrize("element", ["facile", "intermédiaire", "avancé", "solution détaillée", "[Page n]"])
def test_la_demande_reprend_l_etape_4_du_prompt(element):
    # 03 étape 4 et D06.
    assert element in DEMANDE_EXERCICES


def test_generer_exercices_demande_une_reponse_structuree_sans_citations():
    client = client_simule(trois_niveaux())

    generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    parametres = client.beta.messages.create.call_args.kwargs
    assert parametres["system"] == SYSTEME
    document, demande = parametres["messages"][0]["content"]
    assert document["citations"] == {"enabled": False}  # incompatibles avec les réponses structurées
    assert demande["text"].endswith(DEMANDE_EXERCICES)
    configuration = parametres["output_config"]
    assert configuration["effort"] == "high"
    assert configuration["format"]["type"] == "json_schema"
    schema_exercice = configuration["format"]["schema"]["properties"]["exercices"]["items"]
    assert schema_exercice["properties"]["niveau"]["enum"] == list(NIVEAUX)
    assert schema_exercice["additionalProperties"] is False


def test_les_exercices_sont_lus_et_tries_par_niveau():
    client = client_simule([exercice_json("avancé"), exercice_json("facile", pages=(1, 3)), exercice_json("intermédiaire")])

    serie = generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert [exercice.niveau for exercice in serie.exercices] == ["facile", "intermédiaire", "avancé"]
    assert serie.exercices[0] == Exercice(
        niveau="facile",
        objectif="Objectif",
        chapitre="Chapitre 1",
        enonce="Énoncé facile",
        solution="Solution facile",
        pages=(1, 3),
    )
    assert serie.avertissements == []


def test_un_niveau_manquant_declenche_un_avertissement():
    client = client_simule([exercice_json("facile"), exercice_json("avancé")])

    serie = generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert any("intermédiaire" in avertissement for avertissement in serie.avertissements)


def test_un_exercice_sans_page_declenche_un_avertissement():
    client = client_simule([exercice_json("facile", pages=()), exercice_json("intermédiaire"), exercice_json("avancé")])

    serie = generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert any("L'exercice 1 n'indique aucune page" in avertissement for avertissement in serie.avertissements)


@pytest.mark.parametrize(("page", "extrait"), [(2, "page 2, dont le texte"), (9, "page 9, qui n'existe pas")])
def test_une_page_douteuse_declenche_un_avertissement(page, extrait):
    client = client_simule([exercice_json("facile", pages=(page,)), exercice_json("intermédiaire"), exercice_json("avancé")])

    serie = generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert any(extrait in avertissement for avertissement in serie.avertissements)


def test_une_reponse_illisible_donne_un_message_en_francais():
    client = client_simule(texte="pas du JSON")

    with pytest.raises(ErreurClaude, match="n'a pas pu être lue"):
        generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())


def test_un_cours_trop_volumineux_est_refuse_avant_tout_envoi():
    client = client_simule(trois_niveaux(), nb_tokens=150_000)

    with pytest.raises(CoursTropVolumineux):
        generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    client.beta.messages.create.assert_not_called()


def test_le_vrai_sdk_lit_une_reponse_structuree(monkeypatch):
    # Réponse JSON réaliste, lue par le vrai SDK via un faux serveur local (sans Internet).
    import anthropic
    import httpx2

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-cle-de-test-secrete")
    texte = json.dumps({"exercices": trois_niveaux()}, ensure_ascii=False)
    reponse_messages = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-5-5",
        "content": [
            {"type": "thinking", "thinking": "", "signature": "signature"},
            {"type": "text", "text": texte},
        ],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 1200, "output_tokens": 800},
    }
    requetes = []

    def faux_serveur(requete):
        requetes.append(requete)
        if requete.url.path.endswith("/count_tokens"):
            return httpx2.Response(200, json={"input_tokens": 1200})
        return httpx2.Response(200, json=reponse_messages)

    client = anthropic.Anthropic(
        max_retries=0,
        http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(faux_serveur)),
    )

    serie = generer_exercices(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert [exercice.niveau for exercice in serie.exercices] == list(NIVEAUX)
    corps_envoye = json.loads(requetes[-1].content)
    assert corps_envoye["output_config"]["format"]["type"] == "json_schema"
