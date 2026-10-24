"""Mode `exercices` : trois niveaux, solution affichée sur demande (03 étape 4, T2.4)."""

import json
from dataclasses import dataclass

import anthropic

from studyhub.contexte import (
    SYSTEME,
    ProfilEtudiant,
    construire_document,
    construire_messages,
    verifier_pages,
    verifier_taille,
)
from studyhub.controle import ResultatControle
from studyhub.llm import ErreurClaude, compter_tokens, envoyer

NIVEAUX = ("facile", "intermédiaire", "avancé")  # D06
EFFORT = "high"  # des solutions justes demandent plus de réflexion ; à ajuster en phase 3
MAX_TOKENS = 16_000

DEMANDE_EXERCICES = """Crée une série d'exercices sur ce cours, avec deux exercices par niveau :
- facile : définitions et compréhension ;
- intermédiaire : application des notions ;
- avancé : problèmes combinés et questions de type examen.

Pour chaque exercice, indique l'objectif, le chapitre concerné, l'énoncé, une solution détaillée étape par étape, et les numéros des pages du cours sur lesquelles il s'appuie (repère « [Page n] » du document). L'étudiant ne verra la solution que s'il la demande. L'énoncé et la solution peuvent utiliser le format Markdown."""

# Réponse structurée. L'API n'accepte pas les citations avec ce format : les pages sont donc
# demandées dans le JSON, d'après les repères « [Page n] » du document.
SCHEMA = {
    "type": "object",
    "properties": {
        "exercices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "niveau": {"type": "string", "enum": list(NIVEAUX)},
                    "objectif": {"type": "string"},
                    "chapitre": {"type": "string"},
                    "enonce": {"type": "string"},
                    "solution": {"type": "string"},
                    "pages": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["niveau", "objectif", "chapitre", "enonce", "solution", "pages"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["exercices"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class Exercice:
    niveau: str
    objectif: str
    chapitre: str
    enonce: str
    solution: str
    pages: tuple[int, ...]


@dataclass(frozen=True)
class SerieExercices:
    exercices: list[Exercice]  # triés du niveau facile au niveau avancé
    avertissements: list[str]


def generer_exercices(
    client: anthropic.Anthropic, nom_fichier: str, resultat: ResultatControle, profil: ProfilEtudiant
) -> SerieExercices:
    """Demande les exercices à Claude, puis vérifie les niveaux et les pages (02 étape 7).

    Lève CoursTropVolumineux avant tout envoi payant si le cours dépasse le plafond (D31),
    et ErreurClaude si l'appel échoue ou si la réponse est illisible.
    """
    document = construire_document(nom_fichier, resultat, citations=False)
    messages = construire_messages(document, profil, DEMANDE_EXERCICES)
    verifier_taille(compter_tokens(client, system=SYSTEME, messages=messages))

    reponse = envoyer(
        client,
        system=SYSTEME,
        messages=messages,
        max_tokens=MAX_TOKENS,
        output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
    )
    exercices = sorted(_lire_exercices(reponse), key=lambda exercice: NIVEAUX.index(exercice.niveau))
    return SerieExercices(exercices, _verifier(exercices, resultat))


def _lire_exercices(reponse) -> list[Exercice]:
    try:
        texte = next(bloc.text for bloc in reponse.content if bloc.type == "text")
        return [
            Exercice(
                niveau=element["niveau"],
                objectif=element["objectif"],
                chapitre=element["chapitre"],
                enonce=element["enonce"],
                solution=element["solution"],
                pages=tuple(element["pages"]),
            )
            for element in json.loads(texte)["exercices"]
        ]
    except (StopIteration, json.JSONDecodeError, KeyError, TypeError) as erreur:
        raise ErreurClaude("La réponse de Claude n'a pas pu être lue. Réessayez la génération.") from erreur


def _verifier(exercices: list[Exercice], resultat: ResultatControle) -> list[str]:
    niveaux_presents = {exercice.niveau for exercice in exercices}
    avertissements = [
        f"Aucun exercice de niveau « {niveau} » n'a été produit."
        for niveau in NIVEAUX
        if niveau not in niveaux_presents
    ]
    for numero, exercice in enumerate(exercices, start=1):
        if not exercice.pages:
            avertissements.append(
                f"L'exercice {numero} n'indique aucune page du cours : vérifiez qu'il porte bien sur le cours."
            )
        avertissements.extend(verifier_pages(list(exercice.pages), resultat, f"L'exercice {numero}"))
    return avertissements
