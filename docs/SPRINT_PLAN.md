# Sprint Plan

## Objectif 2 a 4 semaines

Obtenir une premiere version utile du moteur Python pur, sans promettre un
produit fini.

La cible est un moteur capable de :

- lire une configuration locale ;
- valider les dimensions principales ;
- generer un layout rectangulaire simple ;
- appliquer des tolerances intelligibles ;
- produire un rapport lisible ;
- preparer l'integration Fusion 360 sans la coder trop tot.

## Hors scope du sprint

- Integration Fusion 360 executable.
- Export STL/3MF.
- Cavites avancees.
- Modules composites.
- Couvercles, charnieres et mecanismes.
- Assistant de conception.
- Validation par impression reelle complete.

## Semaine 1 - Socle moteur et validation

Missions candidates :

- `P0-M004` - Dry-run autonomous mission selection.
- `P1-M001` - Consolidate core data models.
- `P1-M002` - Harden config loading and validation.

Resultat attendu :

- contrat de donnees Phase 1 plus clair ;
- erreurs de configuration plus actionnables ;
- tests unitaires renforces ;
- documentation d'invariants mise a jour.

## Semaine 2 - Layout rectangulaire simple

Missions candidates :

- `P2-M001` - Formalize simple rectangular layout model.
- `P2-M002` - Cover row_fill edge cases.

Resultat attendu :

- comportement `row_fill` documente ;
- cas limites couverts ;
- limites d'optimisation explicites ;
- aucune confusion entre cellule theorique et corps imprimable.

## Semaine 3 - Tolerances explicables et rapports

Missions candidates :

- `P3-M001` - Classify exposed, internal and functional faces.
- `P3-M002` - Apply tolerance rules from face classification.
- `P1-M003` - Improve CLI reporting.

Resultat attendu :

- raisons d'offset visibles ;
- rapports plus utiles pour debug et futur Fusion ;
- statut clair entre implemente, experimental et a valider physiquement.

## Semaine 4 - Readiness Fusion sans implementation profonde

Missions candidates :

- `P4-M000` - Prepare Fusion 360 integration gate report.
- `P4-M001` - Definir le contrat de representation intermediaire CAD.

Resultat attendu :

- rapport de gate Fusion ;
- criteres humains de demarrage Fusion ;
- contrat CAD-agnostic esquisse ou documente ;
- decision explicite avant tout adaptateur.

## Definition de reussite du sprint

Le sprint reussit si :

- les tests Python passent ;
- les exemples CLI restent reproductibles ;
- les prochaines missions sont claires ;
- Fusion 360 reste hors du coeur ;
- les tolerances physiques restent marquees comme non validees par impression ;
- le depot est reprenable par un agent sans contexte oral.
