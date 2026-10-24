"""Tests du client Claude (T2.1). Aucun appel réel à l'API (D32)."""

import json
import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import anthropic
import httpx2
import pytest

from studyhub import llm
from studyhub.llm import ErreurClaude, cle_configuree, creer_client, envoyer

CLE_DE_TEST = "sk-ant-cle-de-test-secrete"
REQUETE = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


@pytest.fixture(autouse=True)
def restaurer_la_cle():
    # load_dotenv écrit directement dans os.environ : on remet l'état initial après chaque test.
    avant = os.environ.get("ANTHROPIC_API_KEY")
    yield
    if avant is None:
        os.environ.pop("ANTHROPIC_API_KEY", None)
    else:
        os.environ["ANTHROPIC_API_KEY"] = avant


@pytest.fixture
def sans_cle(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(llm, "CHEMIN_ENV", tmp_path / ".env")  # fichier absent


@pytest.fixture
def avec_cle(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", CLE_DE_TEST)
    monkeypatch.setattr(llm, "CHEMIN_ENV", tmp_path / ".env")


def erreur_http(classe, statut, type_erreur=None):
    corps = {"error": {"type": type_erreur}} if type_erreur else None
    return classe("détail technique", response=httpx2.Response(statut, request=REQUETE), body=corps)


def client_qui_leve(erreur):
    client = MagicMock()
    client.beta.messages.create.side_effect = erreur
    return client


def client_qui_repond(stop_reason="end_turn"):
    client = MagicMock()
    client.beta.messages.create.return_value = SimpleNamespace(stop_reason=stop_reason, content=[])
    return client


def test_sans_cle_creer_client_explique_comment_la_configurer(sans_cle):
    assert not cle_configuree()
    with pytest.raises(ErreurClaude, match=r"\.env"):
        creer_client()


def test_la_cle_est_lue_depuis_le_fichier_env(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    fichier_env = tmp_path / ".env"
    fichier_env.write_text(f"ANTHROPIC_API_KEY={CLE_DE_TEST}\n", encoding="utf-8")
    monkeypatch.setattr(llm, "CHEMIN_ENV", fichier_env)

    assert cle_configuree()
    assert isinstance(creer_client(), anthropic.Anthropic)


def test_une_cle_vide_compte_comme_absente(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    monkeypatch.setattr(llm, "CHEMIN_ENV", tmp_path / ".env")

    assert not cle_configuree()


def test_envoyer_utilise_le_modele_et_le_repli_automatique():
    client = client_qui_repond()

    envoyer(client, max_tokens=100, messages=[{"role": "user", "content": "Bonjour"}])

    parametres = client.beta.messages.create.call_args.kwargs
    assert parametres["model"] == "claude-opus-5-5"  # D27
    assert parametres["fallbacks"] == "default"  # D30
    assert parametres["betas"] == ["server-side-fallback-2026-07-01"]
    assert parametres["max_tokens"] == 100


def test_le_vrai_sdk_construit_la_requete_attendue(avec_cle):
    # Vrai client du SDK, branché sur un faux serveur local : vérifie la requête HTTP réelle.
    requetes = []

    def faux_serveur(requete):
        requetes.append(requete)
        corps = {"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}
        return httpx2.Response(529, json=corps)

    client = anthropic.Anthropic(
        max_retries=0,
        http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(faux_serveur)),
    )

    with pytest.raises(ErreurClaude, match="surchargé"):
        envoyer(client, max_tokens=100, messages=[{"role": "user", "content": "Bonjour"}])

    corps_envoye = json.loads(requetes[0].content)
    assert corps_envoye["model"] == "claude-opus-5-5"
    assert corps_envoye["fallbacks"] == "default"
    assert "server-side-fallback-2026-07-01" in requetes[0].headers["anthropic-beta"]


def test_envoyer_renvoie_la_reponse_quand_tout_va_bien():
    client = client_qui_repond()

    reponse = envoyer(client, max_tokens=100, messages=[])

    assert reponse.stop_reason == "end_turn"


@pytest.mark.parametrize(
    ("erreur", "extrait_attendu"),
    [
        (erreur_http(anthropic.AuthenticationError, 401), "clé d'API Anthropic est invalide"),
        (erreur_http(anthropic.PermissionDeniedError, 403), "n'a pas accès"),
        (erreur_http(anthropic.NotFoundError, 404), "modèle"),
        (erreur_http(anthropic.RateLimitError, 429), "Trop de demandes"),
        (erreur_http(anthropic.APIStatusError, 402, "billing_error"), "crédit"),
        (erreur_http(anthropic.OverloadedError, 529), "surchargé"),
        (erreur_http(anthropic.InternalServerError, 500), "surchargé"),
        (erreur_http(anthropic.BadRequestError, 400), "rejetée"),
        (anthropic.APITimeoutError(request=REQUETE), "trop de temps"),
        (anthropic.APIConnectionError(request=REQUETE), "connexion Internet"),
    ],
    ids=[
        "cle_invalide", "acces_refuse", "modele_introuvable", "limite_de_requetes", "credit",
        "surcharge", "erreur_serveur", "demande_rejetee", "delai_depasse", "reseau",
    ],
)
def test_chaque_erreur_de_l_api_donne_un_message_en_francais(erreur, extrait_attendu):
    with pytest.raises(ErreurClaude) as resultat:
        envoyer(client_qui_leve(erreur), max_tokens=100, messages=[])

    assert extrait_attendu in str(resultat.value)
    assert "détail technique" not in str(resultat.value)


def test_un_refus_du_modele_donne_un_message_en_francais():
    with pytest.raises(ErreurClaude, match="refusé"):
        envoyer(client_qui_repond(stop_reason="refusal"), max_tokens=100, messages=[])


def test_une_reponse_coupee_donne_un_message_en_francais():
    with pytest.raises(ErreurClaude, match="coupée"):
        envoyer(client_qui_repond(stop_reason="max_tokens"), max_tokens=100, messages=[])


def test_la_cle_n_apparait_dans_aucun_message(avec_cle, monkeypatch):
    erreurs = [
        erreur_http(anthropic.AuthenticationError, 401),
        erreur_http(anthropic.BadRequestError, 400),
        anthropic.APIConnectionError(request=REQUETE),
    ]
    messages = []
    for erreur in erreurs:
        with pytest.raises(ErreurClaude) as resultat:
            envoyer(client_qui_leve(erreur), max_tokens=100, messages=[])
        messages.append(str(resultat.value))
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(ErreurClaude) as resultat:
        creer_client()
    messages.append(str(resultat.value))

    assert all(CLE_DE_TEST not in message for message in messages)
