"""Contrôle d'un fichier importé et de son extraction (02 étape 3, 02 §4, T1.3)."""

from dataclasses import dataclass, field
from enum import Enum

from pypdf.errors import PyPdfError

from studyhub.extraction import FormatNonPrisEnCharge, Passage, extraire_texte

TAILLE_MAX_OCTETS = 20 * 1024 * 1024  # D21 : 20 Mo
NB_CARACTERES_MIN_PAR_PAGE = 20  # D22 : en dessous, la page est vide ou scannée


class Statut(Enum):
    VALIDE = "valide"
    INCOMPLET = "incomplet"  # une partie des pages n'a pas de texte
    ILLISIBLE = "illisible"  # le fichier a été lu, mais aucun texte exploitable
    REFUSE = "refusé"  # le fichier n'a pas été lu (taille ou format)


@dataclass(frozen=True)
class ResultatControle:
    statut: Statut
    message: str  # vide si le fichier est valide
    passages: list[Passage] = field(default_factory=list)
    pages_sans_texte: list[int] = field(default_factory=list)


def controler_fichier(nom_fichier: str, contenu: bytes) -> ResultatControle:
    """Extrait le texte du fichier et indique s'il est exploitable, avec un message pour l'étudiant."""
    if len(contenu) > TAILLE_MAX_OCTETS:
        taille_mo = len(contenu) / (1024 * 1024)
        return ResultatControle(
            Statut.REFUSE,
            f"Le fichier « {nom_fichier} » fait {taille_mo:.1f} Mo, au-delà de la limite de 20 Mo. "
            "Importez un fichier plus léger, par exemple un chapitre à la fois.",
        )
    if not contenu:
        return ResultatControle(
            Statut.ILLISIBLE,
            f"Le fichier « {nom_fichier} » est vide. Importez un autre fichier.",
        )

    try:
        passages = extraire_texte(nom_fichier, contenu)
    except FormatNonPrisEnCharge as erreur:
        return ResultatControle(Statut.REFUSE, str(erreur))
    except PyPdfError:
        return ResultatControle(
            Statut.ILLISIBLE,
            f"Le fichier « {nom_fichier} » est endommagé ou n'est pas un PDF valide. "
            "Importez une autre version du fichier.",
        )
    except UnicodeDecodeError:
        return ResultatControle(
            Statut.ILLISIBLE,
            f"Le texte de « {nom_fichier} » n'a pas pu être lu (encodage inconnu). "
            "Enregistrez-le en UTF-8, puis importez-le à nouveau.",
        )

    pages_sans_texte = [
        passage.numero
        for passage in passages
        if len(passage.texte.strip()) < NB_CARACTERES_MIN_PAR_PAGE
    ]
    if len(pages_sans_texte) == len(passages):
        return ResultatControle(
            Statut.ILLISIBLE,
            f"Aucun texte n'a pu être extrait de « {nom_fichier} ». "
            "Il s'agit probablement d'un document scanné (image), que l'application ne sait pas encore lire. "
            "Importez une version contenant du texte, par exemple le fichier d'origine.",
            passages,
            pages_sans_texte,
        )
    if pages_sans_texte:
        return ResultatControle(
            Statut.INCOMPLET,
            f"Le texte n'a pas pu être extrait pour : {_lister_pages(pages_sans_texte)}. "
            "Ces pages sont peut-être scannées : les réponses ne pourront pas s'appuyer sur leur contenu.",
            passages,
            pages_sans_texte,
        )
    return ResultatControle(Statut.VALIDE, "", passages)


def _lister_pages(numeros: list[int]) -> str:
    if len(numeros) == 1:
        return f"page {numeros[0]}"
    return "pages " + ", ".join(str(numero) for numero in numeros)
