# Validation Matrix

Cette matrice definit ce qu'une validation prouve, ce qu'elle ne prouve pas et
quel statut elle autorise.

## Niveaux de validation

| Validation | Couvre | Ne couvre pas | Preuve attendue | Statut autorise |
| --- | --- | --- | --- | --- |
| Tests unitaires | Fonctions pures, invariants, cas limites locaux. | Ergonomie, Fusion, impression reelle. | Sortie de `python -m unittest discover -s tests`. | `implemente` pour le comportement teste. |
| Tests CLI | Chargement, execution bout en bout locale, codes de sortie, rapports. | Validite CAD ou impression. | Commande CLI et sortie attendue. | `implemente` pour le flux CLI teste. |
| Tests de non-regression | Stabilite de comportements deja acceptes. | Nouveaux cas non couverts. | Tests ajoutes ou existants passes. | Maintien du statut existant. |
| Validation documentaire | Coherence entre docs, statut, backlog, capability map et ADR. | Exactitude physique ou execution code. | Relecture, checklist, test documentaire. | `planned`, `designed` ou pilotage coherent. |
| Validation geometrique abstraite | Dimensions, cellules, corps imprimables, offsets, CAD IR abstraite. | Faisabilite CAD concrete. | Tests et rapports JSON/Markdown. | `implemented-core`, `implemented-cad-ir` ou `experimental` selon couverture. |
| Validation Fusion 360 | Creation de composants inspectables dans Fusion. | Qualite d'impression reelle. | Rapport Fusion, captures ou notes, dimensions controlees. | `implemented-fusion` ou `fusion-validated`. |
| Validation impression reelle | Ajustement physique, jeux, friction, assemblage. | Generalisation a toutes imprimantes. | Mesures, profil imprimante, filament, slicer, photos ou notes. | `print-validated` localement, puis stabilisation si confirme. |
| Validation ergonomique humaine | Lisibilite, manipulation, setup, comprehension utilisateur. | Correction algorithmique seule. | Retour humain structure ou checklist UX. | Amelioration UX documentee. |

## Statuts de capability

Les statuts de `docs/CAPABILITY_MAP.md` indiquent le niveau de maturite d'une
capacite produit, pas seulement l'existence de code.

- `planned` : capability identifiee mais non specifiee en detail.
- `designed` : contrat ou strategie documentee, sans implementation complete.
- `implemented-core` : moteur Python pur implemente et teste.
- `implemented-cad-ir` : capability transportee dans la CAD IR avec tests.
- `implemented-fusion` : adaptateur Fusion code pour cette capability, sans
  validation manuelle complete.
- `fusion-validated` : sortie observee et mesuree dans Fusion 360.
- `print-validated` : sortie imprimee, mesuree et documentee.
- `deferred` : capability volontairement repoussee.
- `blocked` : gate humaine, dependance ou risque connu bloque l'execution.

Une capability peut progresser par paliers. Par exemple une cavite peut etre
`implemented-cad-ir` alors que la generation Fusion reste `blocked`.
## Categories de preuve

### Valide par code

Un comportement est valide par code quand un test automatise couvre le cas avec
des assertions utiles. Cela ne valide ni Fusion 360 ni l'impression.

### Valide par inspection

Une decision documentaire, une ADR ou un rapport peut etre valide par inspection.
Cette validation est acceptable pour la gouvernance, mais insuffisante pour les
promesses physiques.

### Valide par Fusion

Une sortie Fusion est validee quand elle est creee, inspectee et mesuree dans
Fusion 360. Cela reste une validation CAD, pas une validation d'impression.

### Valide par impression reelle

Une propriete physique est validee seulement par impression et mesure reelle avec
contexte documente : imprimante, filament, buse, hauteur de couche, slicer et
conditions pertinentes.

### Non validable automatiquement

Certaines decisions restent humaines :

- confort de manipulation ;
- choix esthetique structurant ;
- acceptation d'une North Star ;
- publication de release ;
- changement de licence ou visibilite.

## Regles de statut

- `implemente` : code present, tests automatises pertinents passes.
- `experimental` : code present, comportement partiel ou validation incomplete.
- `prevu` : decrit mais non code.
- `a valider par impression reelle` : necessite un prototype physique.

Codex ne doit jamais declarer `implemente` une fonctionnalite dont les tests
pertinents n'ont pas ete lances ou dont les echecs restent non resolus.
## P59 - Preuve avant gate P60

| Element | Preuve automatisee | Statut | Preuve restante |
| --- | --- | --- | --- |
| Plan P57 vers CAD IR | Tests digest, cardinalite, cavites, complements, 50 bodies | implemente | aucune |
| Palette vers adaptateur | Tests materialize/regenerate, IR atomique, compact_only, reponse erreur | implemente | aucune |
| Ownership de scene | Tests registry generate/regenerate/inspect/clear/export et preservation non-BGIG | implemente | observation Fusion P60 |
| Scene geometrique finale | Lecture de la CAD IR par le plan Fusion hors API | implemente | observation et inspection Fusion P60 |
| Impression | aucune promesse physique | print-validated: false | impression future hors V0.1 |
