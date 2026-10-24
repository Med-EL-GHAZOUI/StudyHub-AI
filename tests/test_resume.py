"""Tests du résumé et des notions clés (T2.3). Aucun appel réel à l'API (D32)."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from studyhub.contexte import SYSTEME, CoursTropVolumineux, ProfilEtudiant
from studyhub.controle import ResultatControle, Statut
from studyhub.extraction import Passage
from studyhub.resume import DEMANDE_RESUME, Resume, Segment, generer_resume, texte_avec_pages


def cours_de_trois_pages() -> ResultatControle:
    passages = [
        Passage(1, "Chapitre 1 : les vecteurs du plan."),
        Passage(2, ""),
        Passage(3, "Chapitre 2 : les matrices."),
    ]
    return ResultatControle(Statut.INCOMPLET, "", passages, pages_sans_texte=[2])


def citation(debut: int, fin: int):
    return SimpleNamespace(type="content_block_location", start_block_index=debut, end_block_index=fin)


def bloc_texte(texte: str, *citations):
    return SimpleNamespace(type="text", text=texte, citations=list(citations) or None)


def client_simule(*blocs, nb_tokens=5_000):
    client = MagicMock()
    client.beta.messages.count_tokens.return_value = SimpleNamespace(input_tokens=nb_tokens)
    client.beta.messages.create.return_value = SimpleNamespace(stop_reason="end_turn", content=list(blocs))
    return client


@pytest.mark.parametrize("element", ["Résumé structuré", "Notions à mémoriser", "Prérequis", "Erreurs fréquentes"])
def test_la_demande_reprend_l_etape_2_du_prompt(element):
    # 03 étape 2.
    assert element in DEMANDE_RESUME


def test_generer_resume_envoie_le_cours_avec_citations_et_les_consignes():
    client = client_simule(bloc_texte("Les vecteurs.", citation(0, 1)))

    generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant(matiere="Algèbre"))

    parametres = client.beta.messages.create.call_args.kwargs
    assert parametres["system"] == SYSTEME
    document, demande = parametres["messages"][0]["content"]
    assert document["citations"] == {"enabled": True}
    assert "Matière : Algèbre" in demande["text"]
    assert demande["text"].endswith(DEMANDE_RESUME)
    assert parametres["output_config"] == {"effort": "medium"}


def test_les_citations_sont_converties_en_numeros_de_page():
    client = client_simule(
        bloc_texte("## Résumé\n"),
        bloc_texte("Un vecteur a une norme.", citation(0, 1)),
        bloc_texte(" Les matrices.", citation(1, 3)),  # blocs 1 et 2 = pages 2 et 3
    )

    resume = generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert resume.segments == [
        Segment("## Résumé\n", ()),
        Segment("Un vecteur a une norme.", (1,)),
        Segment(" Les matrices.", (2, 3)),
    ]


def test_les_blocs_de_reflexion_sont_ignores():
    client = client_simule(
        SimpleNamespace(type="thinking", thinking="", signature="abc"),
        bloc_texte("Les vecteurs.", citation(0, 1)),
    )

    resume = generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert resume.segments == [Segment("Les vecteurs.", (1,))]


def test_aucun_avertissement_quand_les_citations_sont_valides():
    client = client_simule(bloc_texte("Les vecteurs.", citation(0, 1)))

    resume = generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert resume.avertissements == []


def test_une_citation_d_une_page_sans_texte_declenche_un_avertissement():
    client = client_simule(bloc_texte("Une affirmation.", citation(1, 2)))

    resume = generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert len(resume.avertissements) == 1
    assert "page 2" in resume.avertissements[0]


def test_une_citation_d_une_page_inexistante_declenche_un_avertissement():
    client = client_simule(bloc_texte("Une affirmation.", citation(5, 6)))

    resume = generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert any("page 6" in avertissement for avertissement in resume.avertissements)


def test_un_resume_sans_aucune_citation_declenche_un_avertissement():
    client = client_simule(bloc_texte("Un résumé sans source."))

    resume = generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert any("ne cite aucune page" in avertissement for avertissement in resume.avertissements)


def test_un_cours_trop_volumineux_est_refuse_avant_tout_envoi():
    # D31 : aucune génération payante n'est lancée.
    client = client_simule(nb_tokens=150_000)

    with pytest.raises(CoursTropVolumineux):
        generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    client.beta.messages.create.assert_not_called()


def test_le_texte_affiche_indique_les_pages_apres_chaque_passage_cite():
    resume = Resume(
        segments=[
            Segment("## Résumé\n", ()),
            Segment("Un vecteur a une norme.", (1,)),
            Segment(" Les matrices.", (2, 3)),
        ],
        avertissements=[],
    )

    assert texte_avec_pages(resume) == "## Résumé\nUn vecteur a une norme. *(p. 1)* Les matrices. *(p. 2, 3)*"


def test_le_vrai_sdk_lit_une_reponse_avec_reflexion_et_citations(monkeypatch):
    # Réponse JSON réaliste, lue par le vrai SDK via un faux serveur local (sans Internet).
    import anthropic
    import httpx2

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-cle-de-test-secrete")
    reponse_messages = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-5-5",
        "content": [
            {"type": "thinking", "thinking": "", "signature": "signature"},
            {"type": "text", "text": "## Résumé structuré\n", "citations": None},
            {
                "type": "text",
                "text": "Les matrices se multiplient ligne par colonne.",
                "citations": [
                    {
                        "type": "content_block_location",
                        "cited_text": "[Page 3]\nChapitre 2 : les matrices.",
                        "document_index": 0,
                        "document_title": "cours.pdf",
                        "start_block_index": 2,
                        "end_block_index": 3,
                    }
                ],
            },
        ],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 1200, "output_tokens": 300},
    }

    def faux_serveur(requete):
        if requete.url.path.endswith("/count_tokens"):
            return httpx2.Response(200, json={"input_tokens": 1200})
        return httpx2.Response(200, json=reponse_messages)

    client = anthropic.Anthropic(
        max_retries=0,
        http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(faux_serveur)),
    )

    resume = generer_resume(client, "cours.pdf", cours_de_trois_pages(), ProfilEtudiant())

    assert resume.segments == [
        Segment("## Résumé structuré\n", ()),
        Segment("Les matrices se multiplient ligne par colonne.", (3,)),
    ]
    assert resume.avertissements == []
