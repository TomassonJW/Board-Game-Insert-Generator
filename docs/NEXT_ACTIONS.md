# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P2-M002 - Cover row_fill edge cases

Pourquoi maintenant :

- `P2-M001` a formalise le contrat de layout rectangulaire simple ;
- `row_fill` est maintenant la seule strategie implementee explicite ;
- les identifiants `grid` et `columns` sont reserves mais non executables ;
- la prochaine faiblesse utile est la couverture des cas limites de placement.

Livrable attendu :

- tests de rotation autorisee et refusee ;
- tests de retour a la ligne ;
- tests d'erreur quand le placement depasse la boite ;
- tests de stabilite des priorites et de l'ordre source.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Missions suivantes si P2-M002 est terminee

### 2. P2-M003 - Ajouter une strategie grille explicite

Condition :

- lancer seulement apres `P2-M002` si aucun comportement `row_fill` fragile n'a
  ete decouvert.

Objectif :

- implementer une strategie `grid` explicite, documentee et testee.

## Missions a ne pas lancer tout de suite

- `P2-M003` tant que `P2-M002` n'est pas terminee.
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
