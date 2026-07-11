# Gate P31 - Projection vers des bacs fonctionnels

## Declencheur

P28 transporte bien une selection P21 vers Fusion mais ne cree que des volumes
pleins. P30 les masque de l experience principale et explique honnetement que la
boite visible n est pas encore une piece. Le prochain pas doit donc creer de
vrais receptacles sans deplacer, rescorriger ou reinterpretrer le plan P21.

## Etat actuel prouve

- P21 fournit les origines, tailles, layers et allocations deja resolus.
- P28 les copie dans une CAD IR `rectangular_blank`, sans mur, fond ou cavite.
- Le coeur connait deja `Cavity`, les parois et fonds par defaut, la validation
  des limites de cavite et l operation CAD IR `subtract_rectangular_cavity`.
- L adaptateur Fusion sait planifier puis executer une coupe rectangulaire
  top-open depuis cette operation. Cette capacite ne vaut ni validation Fusion
  du chemin P21, ni validation d impression.

## Options

### A - Un bac ouvert par module selectionne

Chaque module imprimable P21 garde strictement son enveloppe et devient un
corps rectangulaire creux : quatre parois et un fond. Une cavite unique ouverte
en haut est derivee avec les valeurs deja presentes dans `GeometryDefaults`.

- Avantage : conserve le plan P21, reutilise la CAD IR et les coupes Fusion
  existantes, reste testable hors Fusion et donne enfin une piece utilisable.
- Limite : un bac peut contenir plusieurs assets sans les separer ; il ne porte
  ni encoche, ni arrondi, ni couvercle.

### B - Compartiments par asset des P31

Chaque module selectionne est redivise immediatement selon ses allocations P21.

- Avantage : resultat plus specifique a chaque asset.
- Limite : impose un nouveau layout local de compartiments, une regle de
  capacite et des arbitrages multi-assets. Le prototype `quick_asset_box` ne
  peut pas etre copie sans changer le contrat P21.
- Decision : reportee apres la premiere preuve de bac ouvert stable.

### C - Recalculer les cavites dans Fusion

Fusion lirait la selection et deciderait lui-meme des murs, fonds et coupes.

- Avantage : moins de CAD IR apparente.
- Risque : Fusion deviendrait une seconde source de verite et le moteur ne
  serait plus testable seul.
- Decision : refusee par ADR-0042 et ADR-0041.

## Recommandation

Adopter l option A sous le contrat interne
`open_top_tray_from_selected_module.v0`.

Pour chaque module P21 imprimable selectionne :

1. conserver origine et dimensions externes exactement comme P28 ;
2. conserver le corps CAD IR `rectangular_blank` pour rester compatible avec
   l adaptateur Fusion existant ;
3. ajouter une cavite `free` ouverte en haut avec :
   - origine locale `{x: wall, y: wall, z: floor}` ;
   - taille `{x: outer.x - 2*wall, y: outer.y - 2*wall, z: outer.z - floor}` ;
   - `clearance_mm: 0` et source explicite : le bac ne pretend pas ajuster un
     asset particulier ;
4. refuser le module avec un diagnostic structure si une dimension de cavite
   n est pas strictement positive ;
5. exposer les assets associes seulement comme information de tracabilite ;
6. declarer `geometry_status: open_top_tray_candidate` et
   `print_validation_status: not_validated`.

Les valeurs de paroi et de fond deja presentes restent inchangées. Aucun seuil
physique nouveau, aucune tolerance nouvelle, aucun calcul de placement, aucune
encoche, aucun arrondi et aucun mecanisme ne sont introduits.

## Preuves attendues avant Fusion

- test pur de projection : dimensions externes P21 conservees, parois et fond
  preservés, cavite top-open positive ;
- refus structure pour une enveloppe trop petite ;
- test CAD IR : une operation de coupe par bac, frame `body.local` et metadata
  de tracabilite ;
- test du plan Fusion hors API : autant de `cavity_cuts` que de bacs acceptes ;
- regression P28/P21 : aucun score, placement, tolerance ou schema de draft ne
  change ;
- mise a jour Studio : l export expert dit `bac a verifier dans Fusion`, jamais
  `pret a imprimer`.

## Gates suivantes

1. apres implementation : smoke humain Fusion de la premiere cavite provenant
   d une selection P21 ;
2. apres export : premier test slicer puis premiere impression mesuree ;
3. plus tard : compartiments, encoches, formes, couvercles et mecanismes sous
   leurs gates respectives.

## Validation demandee

Valider l option A comme scope P31. La reponse `P31 approuve` autorise la
projection vers des bacs ouverts fonctionnels et ses tests, mais pas encore une
declaration `fusion-validated` ou `print-validated`.
