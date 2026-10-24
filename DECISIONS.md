# Journal des décisions — StudyHub AI

Statuts : ✅ validée · ❓ hypothèse à confirmer · ❌ rejetée.
Une décision validée ne change que sur nouvelle validation de l'utilisateur.
Dans ce cas, ajouter une nouvelle entrée qui remplace l'ancienne, sans effacer l'ancienne.

## ✅ Décisions validées

### Issues des fichiers de référence (constatées le 2026-10-24)
| ID | Décision | Source |
|---|---|---|
| D01 | Le cours fourni est la source principale ; ne jamais inventer le contenu d'un fichier. | 01 §4, 03 Contexte |
| D02 | Citer la page, la diapositive ou la section lorsque c'est possible. | 01 §4, 02 §3 |
| D03 | Distinguer « selon le cours » et « complément externe ». | 01 §4, 03 Étape 3 |
| D04 | Aucune référence inventée ; une référence non vérifiée est signalée comme telle. | 03 Étape 3, 02 §4 |
| D05 | Les solutions des exercices sont masquées par défaut. | 03 Étape 4, 02 §2 |
| D06 | Exercices en trois niveaux : facile, intermédiaire, avancé. | 03 Étape 4 |
| D07 | Construction progressive : MVP, puis version suivante. | 02 §6 |
| D08 | Le RAG n'est pas obligatoire pour le MVP. | 01 §6, 02 §1 |
| D09 | Corriger les erreurs récurrentes avant d'ajouter des fonctionnalités. | 05 Critère de mise en production |
| D10 | Langue de réponse par défaut : français. | 01 §5 |

### Arbitrages (validés le 2026-10-24)
| ID | Décision | Résout |
|---|---|---|
| D11 | Sources externes réglées par matière via `sources_autorisees`. Par défaut : cours uniquement. Les sources externes ne sont utilisées que sur demande explicite et sont toujours étiquetées « complément externe ». | C1 : 01 §5 / 02 §4 / 03 Étape 3 |
| D12 | Modes du MVP : fiches de révision → `resume` ; examen blanc → `exercices` niveau avancé. Flashcards et quiz sont reportés à la version suivante. | C2 : 04 / 02 §2 |
| D13 | Classification commune des erreurs : concept, méthode, calcul, inattention. Utilisée par le mode `corrige` et par le suivi des erreurs. | C3 : 04 / 03 Étape 5 / 02 §6 |
| D14 | Le dossier StudyHub AI a son propre dépôt Git, séparé du dépôt du dossier personnel. Dépôt distant : https://github.com/Med-EL-GHAZOUI/StudyHub-AI | Audit Git |

### Choix techniques du MVP (validés le 2026-10-24)
| ID | Décision | Remplace |
|---|---|---|
| D15 | Stack : Python (3.11, installé sur le poste) + Streamlit pour l'interface. | H1 |
| D16 | Fournisseur de LLM : Anthropic (Claude). Le modèle précis est choisi en phase 2. La clé d'API est lue depuis `.env`. | H2 |
| D17 | Un seul utilisateur, sans authentification. | H3 |

### Choix techniques de la phase 1 (validés le 2026-10-24)
| ID | Décision | Remplace |
|---|---|---|
| D18 | Formats acceptés en phase 1 : PDF, `.txt` et `.md`. PPTX et DOCX à la fin du MVP. | H9 |
| D19 | Extraction PDF avec `pypdf`. | H10 |
| D20 | Tests avec `pytest` ; les PDF de test sont générés par les tests eux-mêmes (`fpdf2`). | H11 |
| D21 | Taille maximale d'un fichier importé : 20 Mo. | H12 |
| D22 | Une page avec moins de 20 caractères extraits est considérée comme vide ou scannée. | H13 |
| D23 | Structure du code : `app.py` (interface) + paquet `studyhub/` (logique) + `tests/`. | H14 |

## ❓ Hypothèses à confirmer
| ID | Question | Recommandation actuelle |
|---|---|---|
| H4 | Seuil de mise en production | Moyenne ≥ 8/10 et 100 % des tests négatifs réussis |
| H5 | Section « Sécurité » dans 02 et erreurs techniques dans 02 §4 | Injection de prompt, contrôle des imports, clés d'API, panne et quota du LLM |
| H6 | PDF scannés | MVP : refuser avec un message clair ; OCR plus tard |
| H7 | Vérification des URL de références | Contrôle automatique que le lien répond ; la pertinence reste à juger |
| H8 | Nom « StudyHub AI » dans le README | Ajouter une section consacrée à l'application |
## ❌ Options rejetées
| Option | Raison | Date |
|---|---|---|
| C1-A : cours uniquement, sans réglage possible | Trop rigide ; remplacée par D11 | 2026-10-24 |
| C1-B : sources externes autorisées par défaut | Risque d'invention plus élevé ; remplacée par D11 | 2026-10-24 |
