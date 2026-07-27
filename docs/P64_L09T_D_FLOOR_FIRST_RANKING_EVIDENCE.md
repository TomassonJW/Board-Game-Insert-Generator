# P64-L09T-D — preuve du classement plancher d'abord

Date : 2026-07-27.

Statut : `automated-validated`.

`fusion-validated=false`, `print-validated=false`.

## Objectif vérifié

Le calcul ne choisit plus une pile compacte avant une disposition basse
uniquement parce que son volume englobant est plus petit. Il compare des plans
complets déjà certifiés selon l'ordre lexicographique suivant :

1. nombre de conteneurs élevés ;
2. somme de leurs bases Z ;
3. volume des conteneurs élevés ;
4. hauteur gênante cumulée sous les réservations supérieures ;
5. empreinte du plan ;
6. nombre de piles élevées ;
7. volume compact, vide interne, hauteur, fragmentation, contacts et appui ;
8. préférence de taille relative des supports, puis identité stable.

La faisabilité, l'appui, les réservations et le certificat commun restent des
contraintes dures en amont de ce classement.

## Absence de règle gloutonne

La lane spécialisée qui construit des piles sous une réservation conserve son
ordre historique pendant l'exploration intermédiaire. Cela protège les états
compacts nécessaires lorsqu'une affectation naïve de tous les conteneurs au sol
ne peut pas être emballée.

Une fois tous les conteneurs affectés, la lane classe les états complets selon
la politique plancher d'abord, tente jusqu'à huit candidats bornés et transmet
chaque candidat trouvé au certificat commun. La pile devient donc un choix
possible, jamais une obligation prématurée ni une interdiction.

## Diagnostics et identité

Les composantes sont publiées dans :

- `minimal_layout.metrics` et `summary.score_breakdown` ;
- `minimal_layout.search_provenance.ranking_axes` ;
- `minimal_layout.search_provenance.selected.floor_first_rank` ;
- chaque entrée du pool borné de candidats de finition ;
- les axes persistés du witness certifié ;
- la télémétrie de la lane de piles réservées.

La version fonctionnelle du solveur minimal devient `p64-l09t-d-v1` et celle
de la lane spécialisée `reserved-floor-stacks-v2`. Les anciennes identités de
witness ne peuvent donc pas être confondues avec ce nouveau rang. À entrées et
budget contractuel identiques, les tests obtiennent le même plan, le même rang
et le même digest déterministe.

## Preuves automatisées

| Cas | Résultat |
| --- | --- |
| Trois conteneurs tiennent au sol | zéro conteneur élevé, zéro base Z cumulée et zéro volume élevé |
| Plan au sol large contre pile très compacte | le plan au sol gagne avant toute mesure de compacité |
| Une pile est physiquement nécessaire | la solution reste trouvée, soutenue et matérialisable |
| Un choix local au sol pourrait bloquer l'emballage | les états intermédiaires compacts restent explorés ; la préférence produit n'est appliquée qu'aux états complets |
| Cas limite anonymisé de 18 conteneurs sous plateau | plusieurs candidats complets sont conservés et ordonnés par conteneurs élevés, bases Z puis volume élevé |
| Deux plans ont les mêmes élévations mais gênent différemment un plateau | la gêne la plus faible gagne avant l'empreinte compacte |
| Même projet et même budget | sélection et digest fonctionnel déterministes |
| Witness persistant | douze axes finis et complets sont scellés puis vérifiés au chargement |

## Fichiers de comportement concernés

- `src/board_game_insert_generator/free_3d_plan_adapter.py`
- `src/board_game_insert_generator/minimal_layout_solver.py`
- `src/board_game_insert_generator/reserved_floor_stack_solver.py`
- `src/board_game_insert_generator/certified_plan_witness.py`
- `tests/test_minimal_layout_solver.py`
- `tests/test_reserved_floor_stack_solver.py`
- `tests/test_certified_plan_witness.py`

## Validation exécutée

- Gate ciblée calcul minimal, lane réservée, witness, cycle staged,
  réservations, réutilisations explicites, diagnostics et solveurs 3D :
  `107/107`, OK en `64.958 s`.
- Lane SCIP produit : `19/19`, OK, avec l'intégration native volontairement
  ignorée dans cet environnement.
- Contrats documentaires et pilotage : `10/10`, OK.
- Gate globale autorisée : `863/863`, OK en `286.898 s`, avec un test ignoré.

La première exécution de la gate globale avait un chemin local incomplet pour
`fusion_addin` et produisait onze erreurs d'import, sans échec de comportement.
Après correction du seul harnais temporaire, la même sélection est entièrement
verte. Le harnais a ensuite été supprimé.

Les onze modules benchmark/corpus/tournoi solveur sont explicitement exclus.
Aucun benchmark, holdout ou artefact canonique associé n'a été exécuté ou
recalculé.

## Limites et suite

- Le classement améliore la sélection des plans minimaux ; il ne ferme pas le
  résiduel de finition.
- 0.1.69 reste `human-KO`, `do-not-run`.
- Aucun package ou add-in Fusion n'est installé en D.
- La mission E doit maintenant livrer la fermeture hybride réelle sans déplacer
  les cavités.
