# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P2-M001 - Formalize simple rectangular layout model

Pourquoi maintenant :

- `P1-M004` ajoute maintenant une boucle CLI courte de diagnostic ;
- le coeur Python pur dispose d'un loader strict, de modeles testes et de
  rapports exploitables ;
- `row_fill` existe mais son contrat d'extension reste implicite ;
- la mission ne touche pas Fusion 360 et prepare les futurs cas limites layout.

Livrable attendu :

- contrat interne documente pour `row_fill`, grille future et colonnes ;
- tests de non-regression layout si necessaire ;
- aucun recalcul de tolerance dans le layout ;
- aucun couplage Fusion 360.

Verification minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Missions suivantes si P2-M001 est terminee

### 2. P2-M002 - Cover row_fill edge cases

Condition :

- lancer seulement apres `P2-M001`.

Objectif :

- tester rotation, retour a la ligne, depassement et priorites ;
- rendre les erreurs de placement previsibles.

## Missions a ne pas lancer tout de suite

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
