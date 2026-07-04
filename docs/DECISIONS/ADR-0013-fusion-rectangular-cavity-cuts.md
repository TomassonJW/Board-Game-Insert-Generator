# ADR-0013 - Coupes Fusion rectangulaires simples par sketch et extrusion cut

## Statut

Accepte

## Date

2026-07-04

## Carte liee

- `P6-M001 - Generer les cavites rectangulaires simples dans Fusion`

## Contexte

Les cavites rectangulaires simples existent deja dans le coeur Python, les
rapports et la CAD IR sous forme `subtract_rectangular_cavity`. La gate humaine
P6-M001 autorise leur premiere execution reelle dans Fusion, mais interdit les
enoches, fonds arrondis, fillets, booleans complexes, STL/3MF et tout recalcul
metier dans l'adaptateur.

L'adaptateur doit donc transformer une operation CAD IR deja resolue en une coupe
Fusion minimale, lisible, mesurable et testable hors Fusion autant que possible.

## Options

1. B-Rep direct : potentiellement precis, mais plus complexe et moins lisible
   pour un premier smoke test.
2. Sketch + extrusion cut simple : proche du chemin deja valide pour les blanks,
   facile a inspecter et documente dans l'API Fusion.
3. Reporter toute coupe et rester sur `planned_only` : plus sur, mais ne prouve
   pas le prochain maillon Fusion autorise.

## Decision

Utiliser `sketch + extrusion cut` pour P6-M001.

L'adaptateur cree un plan XY decale sur le dessus du blank, dessine la footprint
rectangulaire locale de la cavite, puis applique une extrusion cut descendante de
la profondeur CAD IR. La coupe cible explicitement le body du blank via
`participantBodies`.

`local_origin_mm.z` est conserve comme garde de plancher minimale demandee : la
coupe est refusee si la hauteur restante est inferieure a cette valeur. Fusion ne
recalcule ni layout, ni clearances, ni tolerances.

## Consequences

Effets positifs :

- approche coherente avec la generation P4-M003 par sketch et extrusion ;
- plan de generation testable hors Fusion ;
- erreurs actionnables avant appel Fusion pour debordement X/Y, profondeur et
  plancher impossible ;
- coupe limitee au body cible.

Limites et risques :

- la robustesse exacte de l'operation cut doit etre mesuree dans Fusion ;
- la convention top-open ne couvre pas les cavites fermees, laterales ou
  complexes ;
- les features ergonomiques restent abstraites ;
- aucune validation d'impression reelle n'est revendiquee.

## Alternatives refusees

Le B-Rep direct est refuse pour P6-M001 car il ajoute une complexite inutile pour
des cavites rectangulaires simples. Les booleans complexes et geometries courbes
sont refuses car hors gate.

## Suivi

- Tests unitaires hors Fusion sur le plan de coupe et les erreurs de bornes.
- Smoke test manuel Fusion P6-M001V avec `examples/simple_tray.json`.
- Nouvelle gate humaine obligatoire avant encoches, fonds arrondis, fillets,
  booleans complexes ou exports imprimables.
