"""Interface Streamlit de StudyHub AI (D15, D23)."""

import logging

import streamlit as st

from studyhub.controle import ResultatControle, Statut, controler_fichier
from studyhub.extraction import FORMATS_ACCEPTES

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

    st.markdown("**Aperçu du texte extrait**")
    for passage in resultat.passages:
        if passage.numero in resultat.pages_sans_texte:
            libelle = f"Page {passage.numero} — aucun texte extrait"
        else:
            libelle = f"Page {passage.numero}"
        with st.expander(libelle):
            # st.text affiche le texte tel quel, sans l'interpréter comme du Markdown (D01).
            st.text(passage.texte)


st.set_page_config(page_title="StudyHub AI")

st.title("StudyHub AI")
st.write("Assistant d'étude : analyse de cours, exercices et corrections.")

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
