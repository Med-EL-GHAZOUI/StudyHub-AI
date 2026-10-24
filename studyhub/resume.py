"""Mode `resume` : résumé et notions clés, cités page par page (03 étapes 1-2, T2.3)."""

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
from studyhub.llm import compter_tokens, envoyer

EFFORT = "medium"  # à ajuster avec les mesures de la phase 3
MAX_TOKENS = 16_000

DEMANDE_RESUME = """Analyse ce cours, puis prépare la révision.

1. Identifie la matière, le chapitre et les objectifs, puis donne le plan du contenu.
2. Rédige les sections suivantes, avec ces titres :
   - Résumé structuré
   - Notions à mémoriser : définitions, concepts, formules et méthodes essentiels
   - Prérequis
   - Erreurs fréquentes
   - Exemples simples et progressifs
3. Termine par les passages ambigus, illisibles ou manquants, s'il y en a."""


@dataclass(frozen=True)
class Segment:
    """Morceau de texte de la réponse, avec les pages du cours qui l'appuient (vide si aucune)."""

    texte: str
    pages: tuple[int, ...]


@dataclass(frozen=True)
class Resume:
    segments: list[Segment]
    avertissements: list[str]


def generer_resume(
    client: anthropic.Anthropic, nom_fichier: str, resultat: ResultatControle, profil: ProfilEtudiant
) -> Resume:
    """Demande le résumé à Claude, puis vérifie les pages citées (02 étape 7).

    Lève CoursTropVolumineux avant tout envoi payant si le cours dépasse le plafond (D31),
    et ErreurClaude si l'appel échoue.
    """
    messages = construire_messages(construire_document(nom_fichier, resultat), profil, DEMANDE_RESUME)
    verifier_taille(compter_tokens(client, system=SYSTEME, messages=messages))

    reponse = envoyer(
        client,
        system=SYSTEME,
        messages=messages,
        max_tokens=MAX_TOKENS,
        output_config={"effort": EFFORT},
    )
    segments = [
        Segment(bloc.text, _pages_citees(bloc))
        for bloc in reponse.content
        if bloc.type == "text"
    ]
    return Resume(segments, _verifier_citations(segments, resultat))


def texte_avec_pages(resume: Resume) -> str:
    """Texte Markdown du résumé, avec les pages indiquées après chaque passage cité."""
    morceaux = []
    for segment in resume.segments:
        morceaux.append(segment.texte)
        if segment.pages:
            morceaux.append(f" *(p. {', '.join(str(page) for page in segment.pages)})*")
    return "".join(morceaux)


def _pages_citees(bloc) -> tuple[int, ...]:
    # Le bloc d'indice i correspond à la page i + 1 (D28) ; end_block_index est exclusif.
    pages = set()
    for citation in bloc.citations or []:
        if citation.type == "content_block_location":
            pages.update(range(citation.start_block_index + 1, citation.end_block_index + 1))
    return tuple(sorted(pages))


def _verifier_citations(segments: list[Segment], resultat: ResultatControle) -> list[str]:
    pages_citees = [page for segment in segments for page in segment.pages]
    if not pages_citees:
        return ["Le résumé ne cite aucune page du cours : vérifiez son contenu dans le document original."]
    return verifier_pages(pages_citees, resultat, "Le résumé")
