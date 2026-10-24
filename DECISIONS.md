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
| D24 | Filet de sécurité dans l'interface : une erreur inattendue pendant la lecture d'un fichier affiche un message générique en français au lieu d'une erreur technique ; le détail est écrit dans le journal du serveur. | Problème connu de T1.3 |
| D25 | Exception à D10 acceptée pour le MVP : les messages et libellés intégrés de Streamlit restent en anglais (refus d'un format non autorisé ou d'un fichier de plus de 20 Mo, boutons « Upload », « Deploy »). Les messages produits par l'application restent en français. (Validée le 2026-10-24.) | Problème connu de T1.4 |

### Choix de la phase 2 (validés le 2026-10-24)
| ID | Décision | Remplace |
|---|---|---|
| D26 | Sécurité : (1) la clé d'API reste dans `.env`, n'est jamais affichée, journalisée ni commitée ; (2) le cours est envoyé dans un bloc « document » séparé des consignes, et les consignes précisent que ce document est une donnée à étudier et que ses éventuelles instructions ne doivent pas être suivies (injection de prompt) ; (3) les tokens sont comptés avant l'envoi, avec un plafond (D31) ; (4) chaque erreur de l'API donne un message en français (clé invalide, limite de requêtes, surcharge, réseau, délai dépassé, refus, réponse coupée). Le texte à reporter dans 02 (section « Sécurité ») sera proposé à part. | H5 |
| D27 | Modèle : Claude Opus 5.5 (`claude-opus-5-5`), défini par une seule constante dans le code. | H15 |
| D28 | Envoi du cours : le texte extrait en phase 1, un bloc de contenu par page, citations activées. Une page sans texte reçoit la mention « [page sans texte extrait] » pour garder la numérotation. | H16 |
| D29 | Chargement de la clé avec `python-dotenv`, depuis `.env`. | H17 |
| D30 | Repli automatique d'Anthropic activé en cas de refus du modèle (`fallbacks: "default"`). | H18 |
| D31 | Plafond de 100 000 tokens envoyés par demande ; au-delà, refus avec un message proposant d'importer un seul chapitre. | H19 |
| D32 | Tests automatiques avec un Claude simulé (gratuits, sans Internet) ; un seul essai réel en fin de phase (T2.7), sur accord préalable de l'utilisateur, coût annoncé avant. | H20 |
| D33 | La correction des réponses de l'étudiant (03 étape 5, mode `corrige`) fait partie de la phase 2. | H21 |
| D34 | D26 est reportée dans 02 : erreurs techniques ajoutées en §4, nouvelle section §7 « Sécurité ». Nouvelle règle incluse : les cours importés sont envoyés au fournisseur du LLM, ne sont pas conservés de façon permanente et ne servent jamais de données de test. À réexaminer avant la phase 4, qui prévoit un historique (02 §6) et un stockage (02 §5). (Validée le 2026-10-24.) | Proposition de T2.2 |

## ❓ Hypothèses à confirmer
| ID | Question | Recommandation actuelle |
|---|---|---|
| H4 | Seuil de mise en production | Moyenne ≥ 8/10 et 100 % des tests négatifs réussis |
| H6 | PDF scannés | MVP : refuser avec un message clair ; OCR plus tard |
| H7 | Vérification des URL de références | Contrôle automatique que le lien répond ; la pertinence reste à juger |
| H8 | Nom « StudyHub AI » dans le README | Ajouter une section consacrée à l'application |
## ❌ Options rejetées
| Option | Raison | Date |
|---|---|---|
| C1-A : cours uniquement, sans réglage possible | Trop rigide ; remplacée par D11 | 2026-10-24 |
| C1-B : sources externes autorisées par défaut | Risque d'invention plus élevé ; remplacée par D11 | 2026-10-24 |
