# Validation Matrix

Cette matrice definit ce qu'une validation prouve, ce qu'elle ne prouve pas et
quel statut elle autorise.

## Niveaux de validation

| Validation | Couvre | Ne couvre pas | Preuve attendue | Statut autorise |
| --- | --- | --- | --- | --- |
| Tests unitaires | Fonctions pures, invariants, cas limites locaux. | Ergonomie, Fusion, impression reelle. | Sortie de `python -m unittest discover -s tests`. | `implemente` pour le comportement teste. |
| Tests CLI | Chargement, execution bout en bout locale, codes de sortie, rapports. | Validite CAD ou impression. | Commande CLI et sortie attendue. | `implemente` pour le flux CLI teste. |
| Tests de non-regression | Stabilite de comportements deja acceptes. | Nouveaux cas non couverts. | Tests ajoutes ou existants passes. | Maintien du statut existant. |
| Validation documentaire | Coherence entre docs, statut, backlog et ADR. | Exactitude physique ou execution code. | Relecture, checklist, futur test documentaire. | `prevu` ou pilotage coherent. |
| Validation geometrique abstraite | Dimensions, cellules, corps imprimables, offsets. | Faisabilite CAD concrete. | Tests et rapports JSON/Markdown. | `implemente` ou `experimental` selon couverture. |
| Validation Fusion 360 | Creation de composants inspectables dans Fusion. | Qualite d'impression reelle. | Rapport Fusion, captures ou notes, dimensions controlees. | `experimental` ou jalon Fusion accepte. |
| Validation impression reelle | Ajustement physique, jeux, friction, assemblage. | Generalisation a toutes imprimantes. | Mesures, profil imprimante, filament, slicer, photos ou notes. | `a valider par impression reelle` puis stable localement si confirme. |
| Validation ergonomique humaine | Lisibilite, manipulation, setup, comprehension utilisateur. | Correction algorithmique seule. | Retour humain structure ou checklist UX. | Amelioration UX documentee. |

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
