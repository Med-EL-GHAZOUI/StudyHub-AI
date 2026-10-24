"""Interface Streamlit de StudyHub AI (D15, D23)."""

import logging

import streamlit as st

from studyhub.contexte import CoursTropVolumineux, ProfilEtudiant
from studyhub.controle import ResultatControle, Statut, controler_fichier
from studyhub.extraction import FORMATS_ACCEPTES
from studyhub.llm import MESSAGE_CLE_ABSENTE, ErreurClaude, cle_configuree, creer_client
from studyhub.resume import generer_resume, texte_avec_pages

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
    afficher_resume(nom_fichier, resultat)

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


def afficher_resume(nom_fichier: str, resultat: ResultatControle) -> None:
    cle_presente = cle_configuree()
    if st.button(
        "Générer le résumé",
        disabled=not cle_presente,
        help=None if cle_presente else "Configurez d'abord la clé d'API (voir la barre latérale).",
    ):
        with st.spinner("Claude prépare le résumé du cours…"):
            try:
                resume = generer_resume(creer_client(), nom_fichier, resultat, profil_saisi())
            except (ErreurClaude, CoursTropVolumineux) as erreur:
                st.error(str(erreur))
            except Exception:
                # D24 : filet de sécurité, étendu à la génération.
                journal.exception("Erreur inattendue pendant la génération du résumé de %s", nom_fichier)
                st.error("Une erreur inattendue s'est produite pendant la génération du résumé. Réessayez.")
            else:
                # Conservé entre deux actions : Streamlit réexécute la page à chaque clic.
                st.session_state["resume"] = (nom_fichier, resume)

    memorise = st.session_state.get("resume")
    if memorise and memorise[0] == nom_fichier:
        resume = memorise[1]
        st.markdown("**Résumé et notions clés**")
        for avertissement in resume.avertissements:
            st.warning(avertissement)
        st.markdown(texte_avec_pages(resume))


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
