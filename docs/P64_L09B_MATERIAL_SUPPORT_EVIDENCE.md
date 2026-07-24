# P64-L09B — preuve du certificat de support matériel

Date : 2026-07-24
Statut : `implemented-core`, `automated-validated`
Validation physique : `print-validated=false`

## Résultat

Le support d'un corps placé au-dessus du sol n'est plus calculé sur la seule
enveloppe XY extérieure du corps inférieur.

Le certificat commun distingue désormais :

- une face pleine pour un corps solide ;
- les rebords réels d'un conteneur ouvert, soit la face extérieure moins les
  cavités qui atteignent son plan supérieur ;
- `supported_on_material` ;
- `bridged_on_material` ;
- `falls_through_opening` ;
- `insufficient_material_support` ;
- `unstable_support_polygon`.

Une proposition n'est certifiée que si la matière en contact couvre au moins le
seuil historique de 25 % et si l'enveloppe convexe des appuis contient la
projection du centre du corps supérieur. Une empreinte qui tient dans une
ouverture avec les jeux applicables et ne rencontre aucune autre matière est
rejetée comme chute.

`has_lid` est volontairement ignoré. Aucun couvercle ne crée une surface
porteuse tant qu'un futur certificat de fermeture ne l'autorise pas.

## Autorité unique

`src/board_game_insert_generator/material_support.py` porte le calcul pur.

Il est consommé par :

- le greedy et le beam internes pendant la recherche ;
- la fermeture continue après chaque croissance candidate ;
- la conversion d'une solution SCIP avant recertification ;
- le contrat de support des plans de niveaux ;
- le validateur géométrique commun avant publication.

Le solveur historique est désormais fail-closed : une géométrie trouvée mais
refusée par le certificat est publiée comme
`no_solution_within_budget`, sans placement matérialisable et sans exception.

## Preuves automatisées

- chute d'un petit conteneur dans une grande ouverture : rejetée ;
- pontage réparti de part et d'autre du centre : accepté ;
- appui de 25 % entièrement d'un seul côté : rejeté comme instable ;
- corps inférieur plein : face complète acceptée ;
- `has_lid=true` sans certificat : ouverture toujours active ;
- validateur commun : rejet explicite de l'appui sur le vide ;
- chemin de recherche : même décision que le certificat de plan ;
- voies greedy, beam, fermeture continue, SCIP et stage-stack : même autorité.

Commandes exécutées :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -p test_material_support.py
python -m unittest discover -s tests -p test_free_3d_greedy_solver.py
python -m unittest discover -s tests -p test_minimal_layout_solver.py
python -m unittest discover -s tests -p test_scip_product_solver.py
python -m unittest discover -s tests
```

Résultat final : 843 tests sur 843 passent.

## Changements de vérité assumés

Des fixtures historiques qui empilaient des bacs ouverts sur une couverture
d'enveloppe XY suffisante mais sur moins de 25 % de matière réelle sont
désormais honnêtement non certifiées. Ce changement est la correction attendue,
pas une preuve d'impossibilité géométrique générale.

## Limites

- surfaces rectangulaires orthogonales seulement ;
- aucune calibration d'épaisseur ou de stabilité physique nouvelle ;
- aucun couvercle porteur ;
- aucune nouvelle pose automatique ;
- aucune modification de budget, runtime SCIP, UI, CAD, tolérance ou cavité ;
- aucune gate Fusion ni impression dans ce lot.

Les actions de validation de toute la chaîne L09 sont maintenues dans
`docs/P64_L09_VALIDATION_UNIFIEE.md`.
