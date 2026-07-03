# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P0-M002 - Ajouter une verification documentaire de base

Pourquoi maintenant :

- le dry run `P0-M004` a confirme que le depot est pilotable par documents ;
- il manque encore un garde-fou automatise contre les fichiers de pilotage
  absents ou incomplets ;
- la mission est petite, testable et sans gate humaine ;
- elle renforce l'autonomie sans demarrer de developpement produit profond.

Livrable attendu :

- test ou script local verifiant les fichiers de pilotage critiques ;
- messages d'erreur lisibles si un document obligatoire manque ;
- mise a jour courte de `docs/QUALITY_RULES.md` si le controle documentaire est
  ajoute aux regles qualite.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Missions suivantes si P0-M002 est terminee

### 2. P0-M005 - Stabiliser le format des ADR

Objectif :

- confirmer ou completer le template ADR ;
- eviter que les prochaines decisions structurantes soient documentees de facon
  heterogene.

### 3. P1-M001 - Consolidate core data models

Objectif :

- verifier que les dataclasses actuelles couvrent bien le contrat Phase 1 ;
- ajouter ou documenter les invariants non evidents ;
- eviter de coder des concepts futurs seulement decoratifs.

Point d'attention :

- ne pas introduire de validation dans tous les constructeurs sans arbitrage ;
- si le contrat de modele change fortement, creer une ADR.

### 4. P1-M002 - Harden config loading and validation

Condition :

- lancer seulement apres `P1-M001`.

Objectif :

- rendre le chargement et la validation plus precis ;
- couvrir champs inconnus, types invalides et cas limites.

### 5. P2-M001 - Formalize simple rectangular layout model

Condition :

- lancer seulement apres `P1-M001`.

Objectif :

- formaliser le modele rectangulaire simple avant de couvrir plus largement les
  cas limites `row_fill`.

## Missions a ne pas lancer tout de suite

- `P1-M002` tant que `P1-M001` n'est pas terminee.
- `P2-M001` tant que `P1-M001` n'est pas terminee.
- `P2-M002` tant que `P2-M001` n'est pas terminee.
- `P3-M001` tant que `P2-M002` n'est pas terminee.
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
