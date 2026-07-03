# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P2-M004 - Exporter un resume de layout comparatif

Pourquoi maintenant :

- `P2-M001` a formalise le contrat de layout rectangulaire simple ;
- `P2-M002` couvre maintenant les cas limites `row_fill` essentiels ;
- `P2-M003` ajoute une strategie `grid` executable et testee ;
- il existe maintenant au moins deux strategies simples a comparer.

Livrable attendu :

- resume comparatif listant strategie, occupation, warnings et score basique ;
- comparaison au moins entre `row_fill` et `grid` ;
- score lisible et non presente comme optimisation globale ;
- tests rapport/exemples.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Missions suivantes si P2-M004 est terminee

### 2. P3-M001 - Classify exposed, internal and functional faces

Condition :

- necessite une revue rapide de gate tolerance avant execution, car la mission
  touche au modele d'offsets et de faces.

Objectif :

- separer faces exposees, voisines, internes, libres et fonctionnelles.

## Missions a ne pas lancer tout de suite

- `P3-M001` sans revue de gate tolerance.
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
