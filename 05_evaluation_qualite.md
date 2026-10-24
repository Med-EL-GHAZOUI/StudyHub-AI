# Évaluation de la qualité de l'assistant d'étude

## Objectif
Tester régulièrement si l'assistant produit des réponses utiles, justes et fondées sur les documents fournis.

## Jeu de tests initial
Prépare au moins :
- 5 questions dont les réponses figurent explicitement dans le cours ;
- 3 questions qui nécessitent de relier plusieurs parties ;
- 2 questions dont la réponse est absente du cours ;
- 3 exercices avec solutions vérifiées manuellement ;
- 3 demandes de références externes à vérifier.

## Critères de notation
Noter chaque critère de 0 à 2 :
- **Exactitude** : 0 = faux, 1 = partiellement juste, 2 = correct.
- **Ancrage dans les sources** : 0 = aucune source, 1 = source vague, 2 = page/section pertinente.
- **Clarté** : 0 = incompréhensible, 1 = moyen, 2 = clair.
- **Niveau adapté** : 0 = inadapté, 1 = partiellement adapté, 2 = adapté.
- **Transparence** : 0 = invente ou masque l'incertitude, 1 = limites incomplètes, 2 = limites explicites.

Score maximal : 10 points par réponse.

## Tests négatifs
Vérifier que l'assistant :
- reconnaît lorsqu'une information est absente ;
- n'invente pas de page ou de citation ;
- ne présente pas une source non vérifiée comme certaine ;
- demande des précisions lorsque l'énoncé est incomplet ;
- signale les problèmes d'extraction du document.

## Tableau de suivi
| ID | Question/test | Score /10 | Problème constaté | Correction à apporter |
|---|---|---:|---|---|
| T01 | Question factuelle du cours |  |  |  |
| T02 | Question hors du cours |  |  |  |
| T03 | Exercice avec corrigé |  |  |  |
| T04 | Vérification d'une référence |  |  |  |

## Critère de mise en production
Ne pas considérer le système comme fiable uniquement parce qu'une réponse semble convaincante. Vérifier un échantillon de réponses contre le cours et les références originales. Corriger les erreurs récurrentes avant d'ajouter davantage de fonctionnalités.
