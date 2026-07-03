# ADR-0009 - Generer les blanks Fusion par esquisse et extrusion

## Statut

Accepte, amende apres smoke test Part Design

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

Le premier smoke test manuel a montre que certains documents Fusion Part Design
refusent la creation de plusieurs composants enfants. Le chemin P4-M003 doit donc
fonctionner dans le composant racine.

## Options

1. Creer des bodies par esquisse rectangulaire puis extrusion dans le composant
   racine.
2. Creer un composant enfant par blank via `Occurrences.addNewComponent`.
3. Creer des bodies directement en B-Rep via `TemporaryBRepManager.createBox`.
4. Reporter la generation reelle et rester au plan `planned_only`.

## Decision

Choisir l'option 1.

L'adaptateur Fusion cree les sketches et bodies dans le composant racine pour
rester compatible avec les documents Fusion Part Design. Chaque rectangle est
dessine aux coordonnees scene `printable_origin_mm` et aux dimensions
`printable_size_mm.x/y`, puis extrude selon `printable_size_mm.z`.

La reference de boite est creee comme esquisse non imprimable, nommee
explicitement comme reference.

Les longueurs de sketch utilisent la conversion controlee millimetres vers
centimetres internes Fusion. La profondeur d'extrusion utilise une expression
explicite en millimetres.

La creation d'un composant Fusion par module reste une option future, mais
seulement apres gate et validation dans un document Assembly compatible.

## Consequences

Effets positifs :

- approche Fusion lisible et proche du flux utilisateur ;
- compatibilite avec les documents Fusion Part Design limites a un seul composant ;
- noms de sketches, features et bodies faciles a inspecter dans le composant
  racine ;
- pas de dependance supplementaire ;
- la couche hors Fusion reste testable ;
- la CAD IR reste la source unique des dimensions.

Effets negatifs et risques :

- l'execution reelle depend de Fusion 360 et reste non testee automatiquement ;
- les sketches/extrusions peuvent exposer des contraintes API non visibles hors
  Fusion ;
- la reference de boite est une esquisse, pas encore un volume transparent ou un
  gabarit avance ;
- la generation ne couvre pas encore cavites, fillets, shells ou exports ;
- les composants enfants sont reportes a une phase Assembly explicite.

## Alternatives refusees

Le B-Rep direct est refuse pour P4-M003 parce qu'il ajoute des contraintes de
persistence et de base features plus larges que le besoin minimal.

Le maintien en `planned_only` est refuse parce que la gate humaine a autorise la
premiere generation exploitable minimale.

La creation de composants enfants par `Occurrences.addNewComponent` est reportee
parce qu'elle echoue dans les documents Fusion Part Design observes pendant le
smoke test manuel.

## Suivi

- `tests/test_fusion_skeleton.py` couvre le chargement CAD IR, le plan de
  generation, la conversion d'unites hors Fusion et l'absence de
  `addNewComponent` dans le chemin P4-M003.
- `fusion_addin/README.md` decrit la procedure de smoke test manuel.
- `P4-M004` ou toute suite Fusion necessite une nouvelle gate humaine et doit
  partir du resultat manuel observe dans Fusion.
