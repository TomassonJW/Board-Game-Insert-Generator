# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. Gate tolerance - decision avant P3-M002

Pourquoi maintenant :

- `P3-M001` a ajoute une classification explicite des faces dans le coeur Python
  pur ;
- les rapports exposent maintenant ces classifications comme metadonnees ;
- les dimensions imprimables des exemples existants restent inchangees ;
- `P3-M002` appliquerait les regles de tolerance depuis ces roles et peut donc
  modifier le calcul dimensionnel.

Decision humaine attendue :

- autoriser, limiter ou reporter `P3-M002 - Apply tolerance rules from face
  classification` ;
- confirmer si la mission peut modifier le calcul d'offsets ;
- confirmer que les valeurs de tolerance par defaut restent inchangees, sauf
  validation explicite separee.

Validation attendue :

- nouvelle validation humaine de la gate `Changement du modele de tolerance` si
  `P3-M002` modifie les dimensions finales ou les valeurs appliquees.

## Missions suivantes si la gate est validee

### 2. P3-M002 - Apply tolerance rules from face classification

Condition :

- lancer seulement apres validation humaine explicite du perimetre dimensionnel.

Objectif :

- appliquer les jeux selon la classification explicite des faces, en gardant les
  raisons d'offset visibles.

## Missions a ne pas lancer tout de suite

- `P3-M002` sans validation humaine si le calcul dimensionnel change.
- Generation Fusion 360 de blanks tant que le contrat intermediaire n'est pas
  stabilise et que `P4-M000` n'a pas produit de rapport de gate.
- Cavites complexes tant que les parois minimales et clearances ne sont pas
  formalisees.
- Assistant de conception tant que plusieurs strategies de layout n'existent pas.
- Packaging produit tant que des exemples imprimes reels ne sont pas disponibles.

## Fin de chaque mission

Avant de terminer :

- mettre a jour `docs/STATUS.md` ;
- mettre a jour `docs/BACKLOG.md` ;
- remplacer cette liste par les prochaines actions reelles ;
- ajouter une ADR si une decision structurante a ete prise ;
- ajouter une entree de log si l'orientation ou le statut a change ;
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances ;
- committer proprement si le depot a ete modifie.
