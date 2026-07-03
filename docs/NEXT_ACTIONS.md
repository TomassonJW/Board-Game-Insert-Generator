# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P2-M003 - Ajouter une strategie grille explicite

Pourquoi maintenant :

- `P2-M001` a formalise le contrat de layout rectangulaire simple ;
- `P2-M002` couvre maintenant les cas limites `row_fill` essentiels ;
- `grid` est un identifiant reserve mais encore non executable ;
- la prochaine etape utile est d'ajouter une deuxieme strategie simple avant de
  pouvoir comparer des variantes.

Livrable attendu :

- strategie `grid` documentee et testee ;
- refus explicite des grilles impossibles ;
- exemple JSON minimal si le schema existant suffit ;
- aucun couplage Fusion 360.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Missions suivantes si P2-M003 est terminee

### 2. P2-M004 - Exporter un resume de layout comparatif

Condition :

- lancer seulement apres `P2-M003`.

Objectif :

- comparer au moins `row_fill` et `grid` avec un score basique explicable.

## Missions a ne pas lancer tout de suite

- `P2-M004` tant que `P2-M003` n'est pas terminee.
- `P3-M001` tant que les strategies de layout Phase 2 ne sont pas suffisamment
  stabilisees.
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
