# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P1-M001 - Consolidate core data models

Pourquoi maintenant :

- `P0-M005` stabilise maintenant le format des ADR ;
- la Phase 0 dispose des garde-fous suffisants pour reprendre le developpement
  produit ;
- les dataclasses actuelles contiennent deja des concepts futurs qu'il faut
  clarifier avant de durcir le chargement et la validation ;
- la mission est la premiere carte produit `ready` et ne lance pas Fusion 360.

Livrable attendu :

- invariants explicites pour `BoxSpec`, `ModuleRequest`, `ToleranceProfile`,
  `Cell` et `PrintableBody` ;
- tests de creation valides et invalides ;
- documentation de modele alignee avec les concepts reellement implementes.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Missions suivantes si P1-M001 est terminee

### 2. P1-M002 - Harden config loading and validation

Condition :

- lancer seulement apres `P1-M001`.

Objectif :

- rendre le chargement et la validation plus precis ;
- couvrir champs inconnus, types invalides et cas limites.

### 3. P2-M001 - Formalize simple rectangular layout model

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
