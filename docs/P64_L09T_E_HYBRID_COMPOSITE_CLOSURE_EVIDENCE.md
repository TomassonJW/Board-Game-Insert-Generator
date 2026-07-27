# P64-L09T-E — preuve de fermeture hybride composite

Date : 2026-07-27.

Statut : `automated-validated`.

`fusion-validated=false`, `print-validated=false`.

## Objectif vérifié

La finition composite ne dépend plus d'une partition rectangulaire brute
complète. Elle reprend le meilleur pré-remplissage rectangulaire continu,
décompose son résiduel selon les faces des corps, de la boîte et des
réservations, puis attribue chaque cellule imprimable à un propriétaire
admissible sans déplacer le placement minimal qui porte la cavité.

L'ordre appliqué est :

1. conserver les corps minimaux et leurs poses monde ;
2. conserver les extensions rectangulaires déjà trouvées ;
3. absorber d'abord les cellules situées au-dessus d'un propriétaire par une
   extension rectangulaire locale ;
4. rattacher le résiduel restant par une vraie face verticale X ou Y ;
5. supprimer uniquement le jeu interne entre propriétaire et annexe ;
6. préserver les jeux entre propriétaires et les réservations supérieures ;
7. refuser toute cellule sans propriétaire valide.

## Décomposition et attribution

Les espaces vides maximaux du pré-remplissage peuvent se chevaucher. La
fermeture les transforme en cellules orthogonales disjointes avant toute
attribution. Les plans des minima, des extensions et des réservations restent
des frontières de découpe ; ils ne sont plus fusionnés prématurément.

Le choix déterministe compare :

- le nombre de propriétaires possibles ;
- le nombre d'annexes et un indicateur de coins ;
- l'aire de couture ;
- le déséquilibre de volume ajouté ;
- la plus longue face commune ;
- l'identité stable du propriétaire et de la cellule.

Une extension verticale locale découpe le prisme du propriétaire sur
l'empreinte de la cellule puis relève cette colonne depuis le même bas Z. Les
autres morceaux restent connectés par des faces verticales X/Y : aucune annexe
Z seule n'est publiée.

## Jeux et réservations

Le certificat `bgig.xy_composite_partition_certificate.v2` distingue :

- le résiduel imprimable, qui doit atteindre exactement zéro ;
- les corridors de jeu externes, conservés comme vides techniques ;
- le jeu interne propriétaire/annexe, ramené à `0.0 mm` ;
- les réservations supérieures, qui restent exclues de toute matière ;
- les poses minimales et poses de cavité, inchangées.

Les fins corridors de largeur égale au jeu externe entre deux propriétaires
ne sont donc ni remplis ni présentés comme un échec de fermeture.

## Frontière volontaire avec P64-L09T-F

E produit et certifie la géométrie hybride réelle. Le finaliseur l'évalue
désormais après l'échec rectangulaire, avec son pré-remplissage continu réel.

Le certificat produit commun, le CAD IR composite et l'adaptateur Fusion
restent la mission F. Jusqu'à leur livraison, le parcours conserve l'ancienne
fermeture composite matérialisable lorsqu'elle existe. Si seule la nouvelle
géométrie v2 réussit, le résultat expose honnêtement
`xy_composite_product_certificate_v2_required` et ne publie aucun plan
partiel.

Cette frontière décrit l'état livré par E. P64-L09T-F la ferme désormais :
la v2 est recertifiée directement, publiée dans le plan produit et traduite
dans la CAD IR sans retour à la fermeture v1. La preuve courante est
`docs/P64_L09T_F_COMPOSITE_CAD_EVIDENCE.md`.

## Preuves automatisées

| Cas | Résultat |
| --- | --- |
| Extension rectangulaire avant annexe | cellule supérieure absorbée par `rectangular_z_extension` |
| Trou intérieur | résiduel fermé, minima et poses de cavité inchangés |
| Espace de bord | couture interne soudée sans translation du propriétaire |
| Deux propriétaires possibles | même digest et propriétaire stable avec ordre d'entrée inversé |
| Corridor externe | jeu exact conservé entre les deux propriétaires |
| Réservation supérieure | aucun prisme composite n'entre dans la réservation |
| Couture interne | jeu interne `0.0 mm`, volume de jeu repris mesuré |
| Liaison Z seule, flottante, arête ou point | cellule refusée sans faux succès |
| Timeout borné | `xy_composite_deadline_reached` et placement minimal inchangé |
| Fixture produit plateau | proposition hybride v2 certifiée ; ancien chemin v1 maintenu jusqu'à F |

## Fichiers de comportement concernés

- `src/board_game_insert_generator/xy_composite_closure.py`
- `src/board_game_insert_generator/coupled_finalization.py`
- `tests/test_xy_composite_closure.py`
- `tests/test_fusion_palette_project.py`

## Validation exécutée

- Gate ciblée fermeture hybride, pool plateau, parcours end-to-end historique,
  calcul staged et diagnostics : `45/45`, OK en `15.252 s`.
- Régression ciblée du nouveau motif de résiduel sans propriétaire : `1/1`,
  OK.
- Gate globale autorisée : `860/860`, OK en `280.807 s`, avec un test SCIP
  natif ignoré.

La première gate globale a signalé l'ancien motif attendu par un test et le
manifeste non canonique du module d'adaptateurs benchmark après le passage du
finaliseur à `v9`. Le motif a été aligné sur le résiduel réel. L'artefact
benchmark n'a pas été régénéré : ce douzième module rejoint les onze modules
benchmark/corpus/tournoi déjà exclus pendant P64-L09T.

Aucun benchmark, holdout, tournoi, corpus solveur ou artefact canonique associé
n'a été exécuté ou recalculé.

## Limites et suite

- Au commit E, la nouvelle géométrie v2 n'était pas encore publiée dans le
  CAD IR ; cette limite historique est levée par F.
- Aucun package ou add-in Fusion n'est installé en E.
- 0.1.69 reste `human-KO`, `do-not-run`.
- P64-L09T-F doit maintenant certifier et matérialiser fidèlement ces corps
  composites, unions avant cavités et coupes.
