# ADR-0009 - Generer les blanks Fusion par esquisse et extrusion

## Statut

Accepte

## Date

2026-07-03

## Carte liee

- `P4-M003 - Generer des blanks rectangulaires Fusion`

## Contexte

`P4-M001` a defini une CAD IR agnostique et `P4-M002` a isole le squelette
Fusion. `P4-M003` doit creer la premiere geometrie Fusion minimale sans
recalculer layout, offsets ou tolerances.

La generation doit rester simple : une reference de boite et des blanks
rectangulaires inspectables. Elle ne doit pas introduire cavites, couvercles,
fillets, exports ou validation physique.

## Options

1. Creer des bodies par esquisse rectangulaire puis extrusion.
2. Creer des bodies directement en B-Rep via `TemporaryBRepManager.createBox`.
3. Reporter la generation reelle et rester au plan `planned_only`.

## Decision

Choisir l'option 1.

L'adaptateur Fusion cree un composant par blank, place ce composant a l'origine
`printable_origin_mm`, dessine un rectangle local aux dimensions
`printable_size_mm.x/y`, puis extrude selon `printable_size_mm.z`.

La reference de boite est creee comme esquisse non imprimable, nommee
explicitement comme reference.

Les longueurs de sketch utilisent la conversion controlee millimetres vers
centimetres internes Fusion. La profondeur d'extrusion utilise une expression
explicite en millimetres.

## Consequences

Effets positifs :

- approche Fusion lisible et proche du flux utilisateur ;
- noms de composants et bodies faciles a inspecter ;
- pas de dependance supplementaire ;
- la couche hors Fusion reste testable ;
- la CAD IR reste la source unique des dimensions.

Effets negatifs et risques :

- l'execution reelle depend de Fusion 360 et reste non testee automatiquement ;
- les sketches/extrusions peuvent exposer des contraintes API non visibles hors
  Fusion ;
- la reference de boite est une esquisse, pas encore un volume transparent ou un
  gabarit avance ;
- la generation ne couvre pas encore cavites, fillets, shells ou exports.

## Alternatives refusees

Le B-Rep direct est refuse pour P4-M003 parce qu'il ajoute des contraintes de
persistence et de base features plus larges que le besoin minimal.

Le maintien en `planned_only` est refuse parce que la gate humaine a autorise la
premiere generation exploitable minimale.

## Suivi

- `tests/test_fusion_skeleton.py` couvre le chargement CAD IR, le plan de
  generation et la conversion d'unites hors Fusion.
- `fusion_addin/README.md` decrit la procedure de smoke test manuel.
- `P4-M004` ou toute suite Fusion necessite une nouvelle gate humaine et doit
  partir du resultat manuel observe dans Fusion.