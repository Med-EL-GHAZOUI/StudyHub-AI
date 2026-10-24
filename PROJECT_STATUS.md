# État du projet — StudyHub AI
Dernière mise à jour : 2026-10-24

## Phase actuelle
**Phase 2 — Génération MVP** (en cours)

## Feuille de route
| Phase | Contenu | Statut |
|---|---|---|
| 0 | Fondations : décisions, fichiers de pilotage, dépôt Git, stack | Terminée |
| 1 | Import et extraction (02 étapes 1 à 3) | Terminée |
| 2 | Génération MVP (02 §6) | En cours |
| 3 | Harness d'évaluation (05) | À faire ; trancher H4 (seuil) avant ; bloque la phase 4 (D09) |
| 4 | Version suivante (02 §6) | À faire |

## Phase 0 : tâches (terminée)
- [x] Audit des fichiers README et 01 à 05
- [x] Arbitrage des contradictions C1, C2, C3 (D11 à D13)
- [x] Création de CLAUDE.md, DECISIONS.md, PROJECT_STATUS.md
- [x] Report de D11 à D13 dans 01, 02 et 03
- [x] Dépôt Git propre au projet + .gitignore (D14)
- [x] Trancher H1 (stack), H2 (LLM), H3 (utilisateurs) : D15 à D17
- [x] Compléter la section « Commandes » de CLAUDE.md

## Phase 1 : tâches
Objectif : importer un cours, extraire son texte en conservant les numéros de page, et détecter les fichiers vides, scannés ou mal extraits (02 §1, étapes 1 à 3). Aucun appel au LLM dans cette phase.

### T1.1 — Mise en place de l'environnement ✅ (2026-10-24)
Fichiers : `requirements.txt`, `requirements-dev.txt` (versions figées), `.env.example`, `app.py` (page minimale), `studyhub/__init__.py`, `pytest.ini`, `tests/test_app.py`, `.claude/launch.json` (lancement depuis Claude Code).
- [x] Les commandes de la section « Commandes » de CLAUDE.md fonctionnent toutes.
- [x] `streamlit run` affiche une page titrée « StudyHub AI » (vérifié dans le navigateur et par `tests/test_app.py`).
- [x] `pytest` s'exécute sans erreur (1 test réussi).
- [x] `.env.example` contient `ANTHROPIC_API_KEY=` sans valeur ; `.env` n'est pas suivi par Git (`git check-ignore`).

### T1.2 — Extraction du texte avec numéros de page ✅ (2026-10-24)
Fichiers : `studyhub/extraction.py`, `tests/test_extraction.py`, `tests/conftest.py` (génération des PDF de test).
- [x] Un PDF de 3 pages donne 3 passages numérotés 1, 2, 3, chacun avec le texte de sa page.
- [x] Un fichier `.txt` ou `.md` donne un passage unique numéroté 1 (UTF-8, ou encodage Windows ancien cp1252).
- [x] Un format non pris en charge produit une erreur explicite (`FormatNonPrisEnCharge`) qui liste les formats acceptés.
- [x] Tests automatiques pour chaque cas ci-dessus (10 tests, plus le test de T1.1).

### T1.3 — Contrôle de l'extraction ✅ (2026-10-24)
Fichiers : `studyhub/controle.py`, `tests/test_controle.py`. Règles : 02 §4.
Point d'entrée pour l'interface : `controler_fichier(nom, contenu)`, qui renvoie un statut (valide, incomplet, illisible, refusé), un message en français, les passages et les pages sans texte.
- [x] Fichier vide ou PDF sans aucun texte → statut « illisible » et message qui explique le problème et demande un autre fichier.
- [x] PDF dont certaines pages sont sans texte → statut « incomplet », avertissement et liste des pages concernées ; le texte des autres pages reste disponible.
- [x] Fichier trop volumineux (> 20 Mo, D21) ou format non pris en charge → statut « refusé » ; PDF corrompu ou tronqué, texte d'encodage inconnu → statut « illisible ». Message clair dans tous les cas, sans plantage.
- [x] Tests automatiques pour chaque cas ci-dessus (13 tests, dont le seuil de 20 caractères de D22).

### T1.4 — Interface d'import ✅ (2026-10-24)
Fichiers : `app.py`, `.streamlit/config.toml` (limite de 20 Mo, statistiques d'usage désactivées), `tests/test_app.py`.
- [x] La zone de téléversement n'accepte que les formats retenus (D18). Streamlit refuse lui-même les autres extensions.
- [x] Après import : nom du fichier, nombre de pages, statut du contrôle.
- [x] Aperçu du texte page par page, identique au texte extrait (D01) : affichage brut, sans interprétation du Markdown.
- [x] Messages d'erreur et d'avertissement de l'application en français (D10). Voir la limite dans « Problèmes connus ».
- [x] Filet de sécurité (D24) : une erreur inattendue affiche un message générique et le détail va dans le journal du serveur.
- [x] Vérification manuelle dans un navigateur avec un fichier de chaque cas : valide, incomplet, scanné, corrompu, vide, `.md`, `.docx`, plus de 20 Mo.
- [x] Tests automatiques de l'interface (8 tests au total dans `tests/test_app.py`).

### Critères d'acceptation de la phase 1 ✅
- [x] T1.1 à T1.4 terminées selon la définition de « terminé » de CLAUDE.md.
- [x] `pytest` passe (31 tests), sans aucun cours réel dans les tests.

### Hors périmètre de la phase 1
Appel au LLM, résumé, exercices, PPTX et DOCX (D18), OCR (H6), stockage permanent des cours.

## Phase 2 : tâches
Objectif : à partir du cours importé, générer résumé et notions clés avec les pages, des exercices sur 3 niveaux avec solution sur demande, et corriger les réponses de l'étudiant (02 §6, 03, D33). Décisions : D26 à D33.

### T2.1 — Client Claude ✅ (2026-10-24)
Fichiers : `studyhub/llm.py`, `tests/test_llm.py`, `app.py` (état de la clé dans la barre latérale), `requirements.txt` (`anthropic` 2.3.0, `python-dotenv` 1.2.4). Chargement de la clé (D29), modèle (D27), repli automatique (D30), traduction des erreurs en français (D26).
Point d'entrée pour la suite : `creer_client()` et `envoyer(client, **parametres)`, qui lève `ErreurClaude` avec un message pour l'étudiant.
- [x] Sans clé, un message clair s'affiche dans la barre latérale (ouverte au démarrage) et rien ne plante. Vérifié dans le navigateur et par les tests.
- [x] Chaque type d'erreur donne son message français, y compris le crédit insuffisant (402) : clé invalide, accès refusé, modèle introuvable, limite de requêtes, surcharge ou erreur serveur, demande rejetée, délai dépassé, réseau, refus du modèle, réponse coupée. Testé avec un Claude simulé.
- [x] Le vrai SDK construit la requête attendue (modèle, `fallbacks: "default"`, en-tête bêta), vérifié avec un faux serveur local, sans Internet.
- [x] La clé n'apparaît jamais dans un message.

### T2.2 — Préparation du contexte ✅ (2026-10-24)
Fichiers : `studyhub/contexte.py`, `tests/test_contexte.py`, `studyhub/llm.py` (`compter_tokens`), `app.py` (formulaire), tests ajoutés dans `tests/test_llm.py` et `tests/test_app.py`.
- [x] Le cours devient un document avec un bloc par page : le bloc *n* correspond à la page *n*, et les pages sans texte gardent leur place (D28). Chaque bloc commence par « [Page n] », pour que Claude connaisse les numéros même sans citations (réponses structurées de T2.4).
- [x] Les consignes système reprennent 03, 01 §4, D01, D03, D10, D11 et la règle anti-injection (D26). Elles ne contiennent rien de variable, pour que le cache du cours reste valable.
- [x] Formulaire matière / niveau / chapitre (01 §3), affiché pour un cours lisible ; les valeurs sont conservées d'une action à l'autre. Vérifié par les tests d'interface, pas encore dans le navigateur.
- [x] Au-delà de 100 000 tokens, `verifier_taille` refuse la demande avec un message (D31). Le comptage (`compter_tokens`, gratuit) est prêt ; il sera appelé avant chaque génération à partir de T2.3.
- [x] Le vrai SDK envoie bien le document page par page (test avec un faux serveur local).

### T2.3 — Résumé et notions clés (mode `resume`)
- [ ] Résumé structuré, notions à mémoriser, prérequis, erreurs fréquentes (03 étape 2), chaque point cité avec sa page.
- [ ] Une page citée qui n'existe pas ou qui est sans texte déclenche un avertissement ; une absence totale de citation aussi.

### T2.4 — Exercices (mode `exercices`)
- [ ] Réponse structurée : niveau, objectif, chapitre, énoncé, solution, pages.
- [ ] Les 3 niveaux sont présents (D06) ; la solution est cachée derrière « Voir la solution » (D05) ; examen blanc = niveau avancé (D12).

### T2.5 — Correction des réponses (mode `corrige`, D33)
- [ ] Évaluation, explication, solution détaillée et catégorie d'erreur : concept, méthode, calcul ou inattention (D13).
- [ ] La catégorie fait toujours partie des 4 valeurs ; jamais de note seule sans explication (03 étape 5).

### T2.6 — Interface et mémoire de session
- [ ] Les résultats restent affichés entre deux actions (import, génération, solution dépliée).
- [ ] Les limites sont signalées (02 étape 8) ; les tokens consommés sont affichés.

### T2.7 — Vérification réelle (D32)
- [ ] Coût annoncé et accepté par l'utilisateur avant de lancer.
- [ ] Essai avec la clé de l'utilisateur sur un cours libre de droits ; chaque page citée est vérifiée à la main dans le PDF ; coût réel noté.

### Critères d'acceptation de la phase 2
- T2.1 à T2.7 terminées selon la définition de « terminé » de CLAUDE.md.
- `pytest` passe sans aucun appel réel à l'API.

### Hors périmètre de la phase 2
Références externes (D11), quiz et flashcards (D12), historique et suivi des erreurs (phase 4), évaluation chiffrée de la qualité (phase 3).

## Prochaine action
T2.3 — Résumé et notions clés.
Pour T2.7 seulement : l'utilisateur crée lui-même `.env` avec sa clé d'API Anthropic. La clé ne doit jamais être partagée dans la conversation.

## Problèmes connus
- Les messages et libellés intégrés de Streamlit sont en anglais : refus d'un format non autorisé ou d'un fichier de plus de 20 Mo, boutons « Upload », « Deploy ». C'est accepté pour le MVP (D25). Le libellé de la zone d'import annonce les formats et la limite en français.
- Réseau parfois lent vers PyPI : la première installation a échoué par expiration du délai. D'où l'option `--timeout 120` dans la commande d'installation de CLAUDE.md.
