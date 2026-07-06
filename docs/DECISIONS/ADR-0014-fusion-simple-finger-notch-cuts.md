# ADR-0014 - Fusion simple finger notch cuts

Date : 2026-07-06

Statut : accepted for implementation, manual Fusion validation required.

## Contexte

`P5-M004` a ajoute des features ergonomiques abstraites dans les cavites :
`finger_notch`, `side_notch`, `center_notch`, `half_moon_notch` et
`rounded_floor`. Ces features sont exportees en CAD IR par
`describe_cavity_feature`.

`P6-M001` a prouve la chaine Fusion pour des cavites rectangulaires simples. La
gate humaine suivante autorise uniquement `P6-M002` : generation Fusion reelle
d'encoches de doigts simples, sans fonds arrondis, fillets, booleans complexes,
geometrie courbe revendiquee, STL/3MF ou recalcul metier dans Fusion.

## Decision

L'adaptateur Fusion execute les encoches simples de paroi comme des coupes
rectangulaires issues directement de la CAD IR.

- Les kinds supportes sont `finger_notch`, `side_notch`, `center_notch` et
  `half_moon_notch` quand leur placement cible une paroi simple.
- `half_moon_notch` reste une intention abstraite cote moteur ; Fusion cree
  seulement une coupe rectangulaire de bounding box, signalee par
  `geometry_approximation: rectangular_bounding_cut`.
- `rounded_floor` reste non execute.
- Fusion consomme `position_mm`, `size_mm`, `cavity_id` et `placement` deja
  serialises en CAD IR. Fusion ne recalcule ni layout, ni tolerances, ni offset.
- Les garde-fous hors Fusion refusent une encoche qui cible une cavite absente,
  deborde de la cavite, depasse la hauteur utile ou traverse plus que l'epaisseur
  de paroi disponible.
- L'execution reelle dans Fusion reste limitee au body cible via
  `participantBodies`.

## Consequences

Le pipeline peut maintenant produire une aide de prise en main simple inspectable
dans Fusion, mais cette aide n'est pas encore une demi-lune geometrique reelle.
Elle doit etre presentee comme une coupe rectangulaire de paroi.

La validation automatisee couvre la preparation, le plan de generation, les
garde-fous et l'absence de dependance `adsk` dans le coeur Python. La creation et
la mesure dans Fusion restent `manual validation required` tant que Thomas n'a
pas lance le smoke test P6-M002.

La generation de demi-lunes reelles, fonds arrondis, fillets, conges ou autres
operations courbes reste sous gate humaine separee.

## Alternatives refusees

- Generer une demi-lune reelle des maintenant : refuse, car cela introduirait
  une geometrie courbe et des booleans plus fragiles que le perimetre autorise.
- Ignorer toutes les features jusqu'aux fillets : refuse, car une coupe
  rectangulaire simple prouve la chaine sans elargir la complexite.
- Recalculer l'encoche dans Fusion depuis la config BGIG : refuse, car Fusion
  doit consommer la CAD IR et rester un adaptateur de sortie.
