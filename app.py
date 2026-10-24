"""Interface Streamlit de StudyHub AI (D15, D23)."""

import logging

import streamlit as st

from studyhub.contexte import CoursTropVolumineux, ProfilEtudiant
from studyhub.controle import ResultatControle, Statut, controler_fichier
from studyhub.exercices import NIVEAUX, SerieExercices, generer_exercices
from studyhub.extraction import FORMATS_ACCEPTES
from studyhub.llm import MESSAGE_CLE_ABSENTE, ErreurClaude, cle_configuree, creer_client
from studyhub.resume import Resume, generer_resume, texte_avec_pages

TITRES_NIVEAUX = {"facile": "Facile", "intermédiaire": "Intermédiaire", "avancé": "Avancé (type examen)"}  # D12

journal = logging.getLogger(__name__)


def afficher_resultat(nom_fichier: str, resultat: ResultatControle) -> None:
    st.subheader(nom_fichier)
    if resultat.passages:
        st.markdown(f"Pages : {len(resultat.passages)}")

    if resultat.statut is Statut.VALIDE:
        st.success("Fichier lisible : le texte a été extrait de toutes les pages.")
    elif resultat.statut is Statut.INCOMPLET:
        st.warning(resultat.message)
    else:
        st.error(resultat.message)
        return

    afficher_formulaire_profil()
    afficher_generations(nom_fichier, resultat)

    st.markdown("**Aperçu du texte extrait**")
    for passage in resultat.passages:
        if passage.numero in resultat.pages_sans_texte:
            libelle = f"Page {passage.numero} — aucun texte extrait"
        else:
            libelle = f"Page {passage.numero}"
        with st.expander(libelle):
            # st.text affiche le texte tel quel, sans l'interpréter comme du Markdown (D01).
            st.text(passage.texte)


def afficher_formulaire_profil() -> None:
    # 01 §3. Les clés conservent les valeurs saisies d'une action à l'autre.
    st.markdown("**Votre contexte d'étude**")
    st.text_input("Matière", key="matiere", placeholder="Ex. : Algèbre linéaire")
    st.text_input("Niveau d'étude", key="niveau", placeholder="Ex. : Licence 1")
    st.text_input("Chapitre étudié (facultatif)", key="chapitre", placeholder="Vide : tout le document")


def profil_saisi() -> ProfilEtudiant:
    return ProfilEtudiant(
        matiere=st.session_state.get("matiere", ""),
        niveau=st.session_state.get("niveau", ""),
        chapitre=st.session_state.get("chapitre", ""),
    )


def afficher_generations(nom_fichier: str, resultat: ResultatControle) -> None:
    profil = profil_saisi()
    colonne_resume, colonne_exercices = st.columns(2)
    with colonne_resume:
        bouton_de_generation(
            "Générer le résumé",
            "Claude prépare le résumé du cours…",
            "resume",
            nom_fichier,
            lambda client: generer_resume(client, nom_fichier, resultat, profil),
        )
    with colonne_exercices:
        bouton_de_generation(
            "Générer des exercices",
            "Claude prépare les exercices…",
            "exercices",
            nom_fichier,
            lambda client: generer_exercices(client, nom_fichier, resultat, profil),
        )

    resume = resultat_memorise("resume", nom_fichier)
    if resume:
        afficher_resume(resume)
    serie = resultat_memorise("exercices", nom_fichier)
    if serie:
        afficher_exercices(serie)


def bouton_de_generation(libelle: str, attente: str, cle_session: str, nom_fichier: str, generer) -> None:
    cle_presente = cle_configuree()
    if st.button(
        libelle,
        disabled=not cle_presente,
        help=None if cle_presente else "Configurez d'abord la clé d'API (voir la barre latérale).",
    ):
        with st.spinner(attente):
            try:
                # Conservé entre deux actions : Streamlit réexécute la page à chaque clic.
                st.session_state[cle_session] = (nom_fichier, generer(creer_client()))
            except (ErreurClaude, CoursTropVolumineux) as erreur:
                st.error(str(erreur))
            except Exception:
                # D24 : filet de sécurité, étendu à la génération.
                journal.exception("Erreur inattendue pendant « %s » pour %s", libelle, nom_fichier)
                st.error("Une erreur inattendue s'est produite pendant la génération. Réessayez.")


def resultat_memorise(cle_session: str, nom_fichier: str):
    memorise = st.session_state.get(cle_session)
    if memorise and memorise[0] == nom_fichier:
        return memorise[1]
    return None


def afficher_resume(resume: Resume) -> None:
    st.markdown("**Résumé et notions clés**")
    for avertissement in resume.avertissements:
        st.warning(avertissement)
    st.markdown(texte_avec_pages(resume))


def afficher_exercices(serie: SerieExercices) -> None:
    st.markdown("**Exercices**")
    for avertissement in serie.avertissements:
        st.warning(avertissement)
    for niveau in NIVEAUX:
        exercices = [(numero, exercice) for numero, exercice in enumerate(serie.exercices, start=1) if exercice.niveau == niveau]
        if not exercices:
            continue
        st.markdown(f"#### {TITRES_NIVEAUX[niveau]}")
        for numero, exercice in exercices:
            pages = ", ".join(str(page) for page in exercice.pages) or "aucune"
            st.markdown(f"**Exercice {numero} — {exercice.objectif}**  \n*{exercice.chapitre} · p. {pages}*")
            st.markdown(exercice.enonce)
            # D05 : la solution reste repliée tant que l'étudiant ne la demande pas.
            with st.expander("Voir la solution"):
                st.markdown(exercice.solution)


# Barre latérale ouverte au démarrage, pour que l'état de la clé d'API reste visible.
st.set_page_config(page_title="StudyHub AI", initial_sidebar_state="expanded")

st.title("StudyHub AI")
st.write("Assistant d'étude : analyse de cours, exercices et corrections.")

# Vérification locale uniquement : aucun appel à l'API, et la clé n'est jamais affichée (D26).
if cle_configuree():
    st.sidebar.success("Clé d'API Anthropic configurée.")
else:
    st.sidebar.warning(MESSAGE_CLE_ABSENTE)

fichier = st.file_uploader(
    "Importer un cours (PDF, .txt ou .md, 20 Mo maximum)",
    type=list(FORMATS_ACCEPTES),
)

if fichier is not None:
    try:
        resultat = controler_fichier(fichier.name, fichier.getvalue())
    except Exception:
        # D24 : filet de sécurité. Le détail technique va dans le journal du serveur.
        journal.exception("Erreur inattendue pendant le contrôle de %s", fichier.name)
        st.error(
            "Une erreur inattendue s'est produite pendant la lecture du fichier. "
            "Essayez un autre fichier ou une autre version de ce cours."
        )
    else:
        afficher_resultat(fichier.name, resultat)
