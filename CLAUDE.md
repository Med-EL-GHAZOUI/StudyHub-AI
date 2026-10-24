# CLAUDE.md — StudyHub AI

Instructions pour l'agent de développement. Ce fichier décrit **comment construire** l'application.
Le **comportement de l'assistant d'étude** est défini dans les fichiers 01 à 05.

## Fichiers de référence
| Fichier | Rôle | Modification par l'agent |
|---|---|---|
| `01_context_engineering.md` à `05_evaluation_qualite.md` | Référence produit | Uniquement sur proposition validée par l'utilisateur |
| `README.md` | Présentation du projet | Sur validation |
| `DECISIONS.md` | Décisions validées et hypothèses | Pour consigner une décision validée par l'utilisateur |
| `PROJECT_STATUS.md` | État du projet et tâches | À chaque fin de tâche |

- Lire `PROJECT_STATUS.md` et `DECISIONS.md` au début de chaque session.
- En cas de contradiction entre fichiers : ne pas trancher seul. Citer les passages, proposer des options, attendre la validation.
- Toujours distinguer règle existante, nouvelle proposition, décision validée et hypothèse.

## Cycle de travail (une tâche à la fois)
1. **Planifier** : prendre une tâche de `PROJECT_STATUS.md` et relire ses critères d'acceptation. S'ils manquent, les proposer avant de coder.
2. **Implémenter** : limiter les changements à la tâche.
3. **Tester** : écrire ou mettre à jour les tests automatiques, puis les exécuter.
4. **Vérifier** : contrôler chaque critère d'acceptation. Si la tâche touche la génération de contenu, contrôler aussi `01` §4 (fiabilité) et la grille de `05`.
5. **Documenter** : mettre à jour `PROJECT_STATUS.md`. Consigner toute nouvelle décision dans `DECISIONS.md` après validation.

## Définition de « terminé »
Une tâche est terminée seulement si :
- tous ses critères d'acceptation sont vérifiés ;
- les tests passent, sortie de la commande à l'appui ;
- aucune règle des fichiers 01 à 05 ni de `DECISIONS.md` n'est contredite ;
- `PROJECT_STATUS.md` est à jour.

Sinon, dire précisément ce qui manque ou échoue. Ne jamais annoncer un succès non vérifié.

## Commandes
Stack : Python 3.11 + Streamlit (D15). Commandes PowerShell, depuis la racine du projet.
L'environnement virtuel est appelé directement (`.venv\Scripts\python`), sans activation, pour éviter les blocages de la politique d'exécution de PowerShell.
- Créer l'environnement (une seule fois) : `python -m venv .venv`
- Installer : `.venv\Scripts\python -m pip install -r requirements.txt -r requirements-dev.txt`
- Lancer : `.venv\Scripts\python -m streamlit run app.py`
- Tester : `.venv\Scripts\python -m pytest`

## Sécurité du développement
- Les clés d'API et autres secrets vont dans `.env`, jamais dans le code ni dans Git. Fournir un `.env.example` sans valeurs réelles.
- Pour les tests, utiliser des documents libres de droits placés dans `tests/fixtures/`, jamais des cours réels de l'étudiant.
- Ne commiter que dans le dépôt du projet, et seulement à la demande de l'utilisateur.

## Accompagnement
L'utilisateur est développeur débutant. Expliquer chaque choix technique simplement, avancer par petites étapes, donner les commandes exactes à exécuter.
