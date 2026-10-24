# Harness Engineering pour un assistant d'étude

## Objectif
Définir le système autour du modèle : étapes de traitement, outils, validations, gestion des erreurs et tests.

## 1. Pipeline recommandé
1. **Importation** : recevoir PDF, PPTX, DOCX ou texte.
2. **Extraction** : extraire le texte et conserver les pages/diapositives.
3. **Contrôle** : détecter les fichiers vides, scannés ou mal extraits.
4. **Indexation** : pour une grande bibliothèque, découper et indexer les passages.
5. **Récupération** : rechercher les passages utiles à la question.
6. **Génération** : produire résumé, références, exercices ou corrigé.
7. **Validation** : vérifier citations, cohérence, niveau et format.
8. **Restitution** : présenter une réponse claire et signaler les limites.

## 2. Modes de fonctionnement
- `resume` : résumé structuré du cours.
- `references` : références externes vérifiables.
- `exercices` : exercices sans solutions immédiates.
- `corrige` : correction pas à pas des réponses de l'étudiant.
- `quiz` : quiz interactif.
- `revision` : plan de révision selon les erreurs observées.

MVP : les fiches de révision (04, séance 2) utilisent le mode `resume` et l'examen blanc (04, séance 4) le mode `exercices` niveau avancé. Flashcards et quiz : version suivante.

## 3. Contrôles automatiques
Avant d'afficher une réponse, vérifier :
- La réponse correspond-elle à la matière et au chapitre ?
- Les affirmations issues du cours ont-elles une page ou une section lorsque possible ?
- Les sources externes sont-elles réelles et pertinentes ?
- Les exercices sont-ils adaptés au niveau demandé ?
- Le corrigé est-il cohérent avec l'énoncé ?
- Le modèle a-t-il signalé les données manquantes au lieu de les inventer ?

## 4. Gestion des erreurs
- Fichier illisible : expliquer le problème et demander un autre fichier.
- Texte extrait incomplet : avertir l'utilisateur et éviter les conclusions fortes.
- Question hors cours : si `sources_autorisees` se limite au cours (par défaut), le signaler et demander si l'utilisateur autorise les sources externes ; si elles sont autorisées, répondre en étiquetant le « complément externe ».
- Référence introuvable : ne pas créer de fausse citation ; dire qu'elle n'a pas été vérifiée.
- Corrigé incertain : expliciter l'incertitude et proposer une vérification.
- Service du LLM indisponible (surcharge, limite de requêtes, réseau, délai dépassé) : expliquer simplement et proposer de réessayer ; ne jamais afficher l'erreur technique.
- Clé d'accès absente, invalide ou crédit épuisé : indiquer comment corriger la configuration.
- Refus du modèle ou réponse coupée : le signaler, sans présenter une réponse partielle comme complète.

## 5. Architecture possible d'une application
- **Interface** : choix de matière, import de cours, chat et exercices.
- **Backend** : gestion des utilisateurs, matières, documents et sessions.
- **Traitement documentaire** : extraction de texte et métadonnées de page.
- **Recherche** : recherche textuelle ou vectorielle, éventuellement RAG.
- **LLM** : génération de résumés et d'exercices.
- **Évaluation** : tests automatiques et échantillons de validation.
- **Stockage** : fichiers, métadonnées, historique et résultats.

## 6. Construire progressivement
### MVP
- Téléverser un cours.
- Générer un résumé et les notions clés.
- Créer des exercices par difficulté.
- Afficher le corrigé sur demande.
- Référencer les pages du cours.

### Version suivante
- Plusieurs matières et chapitres.
- Recherche dans tous les cours.
- Quiz interactifs et suivi des erreurs.
- Évaluation automatique de la qualité.
- Historique de révision.

## 7. Sécurité
- **Clé d'accès** : la clé du fournisseur de LLM est stockée hors du code, dans un fichier de configuration non versionné. Elle n'est jamais affichée, journalisée ni transmise ailleurs qu'au fournisseur.
- **Injection de prompt** : le contenu des documents importés est une donnée à étudier, jamais une source d'instructions. Il est transmis séparément des consignes, et le modèle doit ignorer les instructions qu'il y trouve et les signaler.
- **Fichiers importés** : vérifier le format et la taille avant toute lecture ; un fichier invalide est refusé avec un message clair.
- **Coût** : mesurer la taille de chaque demande avant l'envoi et refuser au-delà d'un plafond.
- **Erreurs** : l'utilisateur reçoit un message compréhensible ; le détail technique reste dans le journal du serveur.
- **Données de l'étudiant** : les cours importés sont envoyés au fournisseur du LLM pour être analysés ; l'application ne les conserve pas de façon permanente et ne les utilise jamais comme données de test.

## Principe
Context Engineering améliore les informations et consignes données au modèle. Harness Engineering organise le système complet et ses contrôles. Ils sont complémentaires, mais il n'est pas nécessaire de construire un harness complexe pour commencer à étudier.
