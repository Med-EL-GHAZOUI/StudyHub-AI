"""Client Claude : clé d'API, modèle, repli automatique et messages d'erreur en français (T2.1)."""

import logging
import os
from pathlib import Path

import anthropic
from anthropic.types.beta import BetaMessage
from dotenv import load_dotenv

MODELE = "claude-opus-5-5"  # D27
BETA_REPLI = "server-side-fallback-2026-07-01"  # D30
CHEMIN_ENV = Path(__file__).parent.parent / ".env"  # D29

MESSAGE_CLE_ABSENTE = (
    "La clé d'API Anthropic est absente. Copiez le fichier .env.example en .env, "
    "collez votre clé après ANTHROPIC_API_KEY=, puis relancez l'application. "
    "L'import et l'aperçu des cours fonctionnent sans clé."
)

journal = logging.getLogger(__name__)


class ErreurClaude(Exception):
    """Erreur lors d'un appel à Claude ; le message est destiné à l'étudiant (D26)."""


def cle_configuree() -> bool:
    load_dotenv(CHEMIN_ENV)
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def creer_client() -> anthropic.Anthropic:
    if not cle_configuree():
        raise ErreurClaude(MESSAGE_CLE_ABSENTE)
    return anthropic.Anthropic()


def envoyer(client: anthropic.Anthropic, **parametres) -> BetaMessage:
    """Envoie une demande à Claude et renvoie sa réponse complète.

    Lève ErreurClaude, avec un message en français, si l'appel échoue,
    si le modèle refuse ou si la réponse est coupée.
    """
    try:
        reponse = client.beta.messages.create(
            model=MODELE,
            betas=[BETA_REPLI],
            fallbacks="default",
            **parametres,
        )
    except anthropic.APIError as erreur:
        # Le détail technique reste dans le journal du serveur (D24, D26).
        journal.warning("Échec de l'appel à Claude : %r", erreur)
        raise ErreurClaude(_message_pour(erreur)) from erreur

    if reponse.stop_reason == "refusal":
        raise ErreurClaude(
            "Claude a refusé de traiter cette demande. "
            "Reformulez-la ou essayez avec un autre extrait du cours."
        )
    if reponse.stop_reason == "max_tokens":
        raise ErreurClaude(
            "La réponse a été coupée car elle dépassait la longueur maximale. "
            "Essayez avec un chapitre plus court."
        )
    return reponse


def compter_tokens(client: anthropic.Anthropic, **parametres) -> int:
    """Compte les tokens d'une demande avant de l'envoyer (D26, D31). Le comptage est gratuit."""
    try:
        resultat = client.beta.messages.count_tokens(model=MODELE, **parametres)
    except anthropic.APIError as erreur:
        journal.warning("Échec du comptage des tokens : %r", erreur)
        raise ErreurClaude(_message_pour(erreur)) from erreur
    return resultat.input_tokens


def _message_pour(erreur: anthropic.APIError) -> str:
    # Du plus précis au plus général : les sous-classes avant APIStatusError.
    if isinstance(erreur, anthropic.AuthenticationError):
        return (
            "La clé d'API Anthropic est invalide ou a été révoquée. "
            "Vérifiez la valeur de ANTHROPIC_API_KEY dans le fichier .env."
        )
    if isinstance(erreur, anthropic.PermissionDeniedError):
        return "Votre clé d'API n'a pas accès à cette fonctionnalité. Vérifiez les droits de votre compte Anthropic."
    if isinstance(erreur, anthropic.NotFoundError):
        return f"Le modèle {MODELE} n'est pas disponible pour votre compte Anthropic."
    if isinstance(erreur, anthropic.RateLimitError):
        return "Trop de demandes en peu de temps. Patientez une minute, puis réessayez."
    if isinstance(erreur, anthropic.APIStatusError):
        if erreur.status_code == 402 or erreur.type == "billing_error":
            return "Le crédit de votre compte Anthropic est insuffisant. Rechargez-le, puis réessayez."
        if erreur.status_code >= 500:
            return "Le service de Claude est momentanément surchargé ou indisponible. Réessayez dans quelques minutes."
        return "La demande a été rejetée par l'API Anthropic. Le détail est écrit dans le journal du serveur."
    if isinstance(erreur, anthropic.APITimeoutError):
        return "Claude a mis trop de temps à répondre. Réessayez, éventuellement avec un chapitre plus court."
    if isinstance(erreur, anthropic.APIConnectionError):
        return "Impossible de joindre l'API Anthropic. Vérifiez votre connexion Internet."
    return "Une erreur inattendue s'est produite lors de l'appel à Claude. Le détail est écrit dans le journal du serveur."
