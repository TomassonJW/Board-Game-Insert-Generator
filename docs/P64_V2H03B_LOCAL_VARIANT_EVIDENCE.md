# P64-V2H03B — Preuve de frontière locale et caps

Statut : `implemented-core`, `automated-validated`, sans routage public.

## Portée vérifiée

Le module pur `container_internal_variants.py` consomme la dérivation
existante sans la modifier. Il produit des variantes locales immuables,
certifiées et bornées pour une future consommation par P64-V2H03C.

Aucun champ `bgig.project.v1`, solveur public, contrôle Fusion ou corps
automatique n'est ajouté.

## Implémentation

- producteur primaire `canonical_v1@1`, équivalent à la dérivation actuelle ;
- producteur `bounded_rectangular_relayout_v1@1`, rectangulaire et technique ;
- digest SHA-256 sur géométrie, contenus, quantités, jeux et sources des jeux ;
- certificat local fail-closed avec codes de rejet stables ;
- déduplication avec alias de provenance et frontière locale de Pareto ;
- budgets immuables, monotones, sérialisables et observables ;
- rotations globales et réservations supérieures exclues de l'identité locale.

## Mesures du corpus déterministe

| Profil | Générées / certifiées | Retenues | Options | États | Essais | Cœur dense | Durée |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rapide | 24 / 24 | 4 | 2 | 32 | 128 | 24 / 231 | 35,613 ms |
| Normal | 48 / 48 | 8 | 4 | 384 | 3 072 | 48 / 231 | 55,880 ms |
| Approfondi | 96 / 96 | 12 | 6 | 3 072 | 36 864 | 96 / 231 | 95,177 ms |

La fixture à quatre cavités possède 21 layouts bruts et est entièrement
énumérée dès Rapide : 22 variantes avec la canonique, 1 doublon, 8 dominées et
4/8/12 retenues.

Les caps globaux, non consommés dans H03B, dérivent des largeurs beam 8/24/64,
des variantes retenues 4/8/12 et des priorités 1/2/4. Les essais ajoutent les
options 2/4/6 et deux rotations. H03C devra mesurer leur consommation réelle.

## Fixtures verrouillées

1. parité canonique simple, H01, H02, H03R et V2H01 ;
2. déduplication et alias de provenance ;
3. rotation globale absente du digest local ;
4. vrai compromis multi-cavités X/Y ;
5. réservation localisée sans effet local ;
6. axes Auto/Cible/Fixe ;
7. jeux asset préservés et overrides externes exclus ;
8. snapshot anonymisé 11 conteneurs / 34 contenus, dont 14 cavités denses.

## Validation

- tests ciblés H03B : 10/10 OK ;
- dérivation historique : 9/9 OK ;
- enveloppes extensibles : 8/8 OK ;
- Ruff ciblé : OK ;
- suite complète : 556/556 OK (166,087 s) ;
- compileall, Ruff ciblé, frontière adsk et diff-check : OK.

## Limites

Aucune variante n'est encore sélectionnée globalement. Le lot ne prouve pas la
solubilité du cas dense. `fusion-validated: false` et
`print-validated: false`.
