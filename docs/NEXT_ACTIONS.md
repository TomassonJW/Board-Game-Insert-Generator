# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable.

## Mission suivante recommandee

### 1. P0-M002 - Ajouter une verification documentaire de base

Pourquoi maintenant :

- la gouvernance vient d'etre ajoutee ;
- les prochains agents doivent etre alertes si un fichier critique manque ;
- c'est une petite mission testable qui securise l'autopilotage.

Livrable attendu :

- un test ou script local qui verifie l'existence des fichiers de pilotage ;
- un message clair si `AGENTS.md`, `docs/STATUS.md`, `docs/ROADMAP.md`,
  `docs/BACKLOG.md` ou `docs/NEXT_ACTIONS.md` manque ;
- documentation courte dans `docs/QUALITY_RULES.md`.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Missions suivantes si P0-M002 est terminee

### 2. P1-M001 - Consolider les modeles de donnees de base

Objectif :

- verifier que les dataclasses actuelles couvrent bien le contrat Phase 1 ;
- ajouter ou documenter les invariants non evidents ;
- eviter de coder des comportements futurs seulement decoratifs.

Point d'attention :

- ne pas introduire de validation dans tous les constructeurs sans arbitrage ;
- si le contrat de modele change fortement, creer une ADR.

### 3. P2-M002 - Couvrir les cas limites de `row_fill`

Objectif :

- securiser le layout deja implemente avant d'ajouter de nouvelles strategies.

Cas a couvrir :

- rotation autorisee ;
- module trop grand ;
- passage a une nouvelle ligne ;
- priorites ;
- quantites ;
- messages d'erreur.

### 4. P3-M001 - Classifier explicitement les faces

Objectif :

- rendre le modele de tolerance plus explicable ;
- preparer les modules composites et les rapports detaillees.

## Missions a ne pas lancer tout de suite

- Generation Fusion 360 de blanks tant que le contrat intermediaire n'est pas
  stabilise.
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
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances.
