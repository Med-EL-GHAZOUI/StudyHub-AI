# Context Engineering pour un assistant d'étude

## Objectif
Fournir au modèle les informations pertinentes, organisées et vérifiables pour qu'il puisse répondre à partir des cours de l'étudiant.

## 1. Sources de contexte
- Cours PDF, diapositives PowerPoint et notes personnelles.
- Objectifs pédagogiques et programme officiel, s'ils sont disponibles.
- Exercices et corrigés fournis par l'enseignant.
- Références externes fiables, clairement séparées du cours.

## 2. Organisation conseillée
Pour chaque matière, conserver :
- `matiere.md` : nom, niveau, objectifs et prérequis.
- `cours/` : fichiers originaux.
- `notes/` : résumés et notions extraites.
- `exercices/` : exercices classés par chapitre et difficulté.
- `references.md` : bibliographie et liens vérifiés.

## 3. Instructions de contexte
Le modèle doit savoir :
1. Quelle matière et quel chapitre sont étudiés.
2. Quel est le niveau de l'étudiant.
3. Si la réponse doit se limiter au cours ou peut utiliser des sources externes.
4. Quel format de sortie est attendu.
5. Comment signaler une information absente ou ambiguë.

## 4. Règles de fiabilité
- Ne pas inventer le contenu d'un fichier.
- Mentionner la page, la diapositive ou la section lorsque c'est possible.
- Distinguer clairement « selon le cours » et « complément externe ».
- Pour les références externes, fournir titre, auteur ou organisme, date si disponible et URL vérifiable.
- Si le document est illisible ou incomplet, demander une meilleure version ou préciser la limite.

## 5. Gabarit de contexte par matière
```yaml
matiere: "Nom de la matière"
niveau: "Niveau d'étude"
chapitre: "Chapitre étudié"
objectif: "Comprendre, réviser ou préparer un examen"
sources_autorisees:
  - "Cours fourni"
  - "Sources externes fiables si nécessaire"
langue_reponse: "Français"
niveau_detail: "Progressif, avec exemples"
format:
  - "Résumé"
  - "Notions clés"
  - "Exercices"
  - "Corrigé sur demande"
```

## 6. Quand utiliser RAG ?
Pour quelques fichiers, joindre les documents à la conversation peut suffire. Pour une application contenant de nombreux cours, un système RAG peut extraire le texte, le découper en passages, indexer ces passages et récupérer les extraits pertinents pour chaque question. Le RAG aide à retrouver les sources, mais ne garantit pas à lui seul l'exactitude : il faut aussi citer les passages et évaluer les réponses.
