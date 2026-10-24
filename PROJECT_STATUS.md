# État du projet — StudyHub AI
Dernière mise à jour : 2026-10-24

## Phase actuelle
**Phase 1 — Import et extraction** (en cours)

## Feuille de route
| Phase | Contenu | Statut |
|---|---|---|
| 0 | Fondations : décisions, fichiers de pilotage, dépôt Git, stack | Terminée |
| 1 | Import et extraction (02 étapes 1 à 3) | En cours |
| 2 | Génération MVP (02 §6) | À faire ; trancher H5 (sécurité) avant |
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

Remarque pour T1.3 : un PDF corrompu ou un texte indécodable lève encore une erreur brute. Leur transformation en message clair est prévue dans T1.3.

### T1.3 — Contrôle de l'extraction
Fichier : `studyhub/controle.py`. Règles : 02 §4.
- [ ] Fichier vide ou PDF sans aucun texte → statut « illisible » et message qui explique le problème et demande un autre fichier.
- [ ] PDF dont certaines pages sont sans texte → statut « incomplet », avertissement et liste des pages concernées.
- [ ] Fichier trop volumineux ou PDF corrompu → refus avec message clair, sans plantage.
- [ ] Tests automatiques pour chaque cas ci-dessus.

### T1.4 — Interface d'import
Fichier : `app.py`.
- [ ] La zone de téléversement n'accepte que les formats retenus (D18).
- [ ] Après import : nom du fichier, nombre de pages, statut du contrôle.
- [ ] Aperçu du texte page par page, identique au texte extrait (D01).
- [ ] Messages d'erreur et d'avertissement en français (D10).
- [ ] Vérification manuelle : l'application est lancée avec un fichier de chaque cas de T1.3.

### Critères d'acceptation de la phase 1
- T1.1 à T1.4 terminées selon la définition de « terminé » de CLAUDE.md.
- `pytest` passe, sans aucun cours réel dans les tests.

### Hors périmètre de la phase 1
Appel au LLM, résumé, exercices, PPTX et DOCX (D18), OCR (H6), stockage permanent des cours.

## Prochaine action
T1.3 — Contrôle de l'extraction.

## Problèmes connus
- Réseau parfois lent vers PyPI : la première installation a échoué par expiration du délai. D'où l'option `--timeout 120` dans la commande d'installation de CLAUDE.md.
