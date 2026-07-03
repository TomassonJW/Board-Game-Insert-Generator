# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P0-M004 - Dry-run autonomous mission selection

Pourquoi maintenant :

- le protocole d'autonomie vient d'etre ajoute ;
- il faut verifier que la boucle selectionne correctement une mission sans
  supervision constante ;
- c'est une mission documentaire courte, sans developpement produit profond ;
- elle teste les gates avant de relancer les phases moteur.

Livrable attendu :

- rapport de dry-run indiquant les fichiers lus ;
- mission `ready` selectionnee ;
- dependances et gates verifiees ;
- criteres d'acceptation relus ;
- decision explicite de ne pas implementer dans ce dry-run.

Verification minimale :

```powershell
git diff --check
```

## Missions suivantes si P0-M004 est terminee

### 2. P0-M002 - Ajouter une verification documentaire de base

Objectif :

- automatiser un controle simple des fichiers de pilotage critiques ;
- securiser l'autopilotage contre une documentation manquante.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

### 3. P1-M001 - Consolidate core data models

Objectif :

- verifier que les dataclasses actuelles couvrent bien le contrat Phase 1 ;
- ajouter ou documenter les invariants non evidents ;
- eviter de coder des concepts futurs seulement decoratifs.

Point d'attention :

- ne pas introduire de validation dans tous les constructeurs sans arbitrage ;
- si le contrat de modele change fortement, creer une ADR.

### 4. P2-M002 - Cover row_fill edge cases

Objectif :

- securiser le layout deja implemente avant d'ajouter de nouvelles strategies.

Cas a couvrir :

- rotation autorisee ;
- module trop grand ;
- passage a une nouvelle ligne ;
- priorites ;
- quantites ;
- messages d'erreur.

### 5. P3-M001 - Classify exposed, internal and functional faces

Objectif :

- rendre le modele de tolerance plus explicable ;
- preparer les modules composites et les rapports detailles.

## Missions a ne pas lancer tout de suite

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
