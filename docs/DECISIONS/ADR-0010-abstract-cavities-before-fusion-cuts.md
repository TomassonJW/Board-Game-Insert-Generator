# ADR-0010 - Cavites abstraites avant coupes Fusion

## Statut

Accepte

## Date

2026-07-04

## Carte liee

- `P5-M001 - Modeliser les cavites simples`

## Contexte

La gate humaine apres P4-M004/P4-M006 autorise une progression P5 limitee au
coeur Python pur, a la configuration, aux rapports et a la CAD IR. Le projet doit
commencer a decrire des modules creusables sans generer encore de cavites reelles
dans Fusion 360.

Le risque principal est de laisser l'adaptateur Fusion inventer ou recalculer la
geometrie de cavite. Cela casserait la frontiere moteur/adaptateur deja etablie.

## Options

1. Ajouter directement des coupes Fusion.
2. Ajouter seulement une note documentaire sans modele code.
3. Modeliser les cavites dans le coeur Python et les transporter dans la CAD IR
   comme operations abstraites non executees.

## Decision

Retenir l'option 3.

Une cavite simple est un volume rectangulaire local au module, avec origine,
dimensions, type fonctionnel, clearance et commentaire optionnel. Elle est validee
contre l'enveloppe externe du module, les parois X/Y minimales et le fond minimal.

La CAD IR serialise ces cavites dans `body.cavities` et ajoute une operation
abstraite `subtract_rectangular_cavity`. Cette operation porte explicitement
`fusion_generation: not_implemented` et ne doit pas etre executee par l'add-in
Fusion actuel.

## Consequences

Effets positifs :

- le moteur Python reste la source de verite ;
- les rapports expliquent les cavites prevues ;
- `export-cad-ir` peut transporter les futures coupes sans changer le layout ;
- Fusion peut rester limite aux blanks rectangulaires tant qu'une gate n'autorise
  pas les operations soustractives.

Risques et limites :

- P5-M001 ne prouve pas la faisabilite CAD reelle d'une coupe ;
- les dimensions sont validees abstraitement, pas par impression ;
- les clearances de cartes, tokens, des et meeples devront etre raffinees dans
  des missions suivantes.

## Alternatives refusees

- Couper directement dans Fusion : refuse, car la gate suivante exige un rapport
  avant toute extrusion cut/boolean reelle.
- Documentation seule : refuse, car l'objectif P5 demande un flux testable
  configuration -> rapports -> CAD IR.

## Suivi

- `P5-M002` peut specialiser les logements cartes/cartes sleevees.
- `P5-M003` peut specialiser les bacs tokens/des/meeples.
- Toute generation Fusion reelle de cavites doit declencher une gate humaine avec
  etat du moteur, etat CAD IR, operation Fusion envisagee, risques et smoke test.