
# P32 - Palette Fusion implementee

## Etat

- Date : 2026-07-11.
- Statut : `implemented-fusion-palette`, `fusion-smoke-required`, `print-validated: false`.
- Decision appliquee : ADR-0042, Studio principal et Fusion secondaire.

## Resultat

- La palette locale `BGIG - Atelier de rangement` devient l ouverture normale de l add-in.
- Elle affiche trois cartes simples : design, scene Fusion, fabrication.
- Les actions sont bornees a la previsualisation, la mise a jour explicite, l export et l ouverture volontaire des reglages experts.
- Les erreurs techniques sont repliees dans le detail technique ; la vue normale ne montre pas de dump de telemetrie.

## Preuves hors Fusion

- `python -m unittest discover -s tests -p test_fusion_skeleton.py` : 87 tests OK.
- `python -m py_compile fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.py fusion_addin/BoardGameInsertGenerator/fusion_skeleton.py` : OK.
- `git diff --check` : OK.

## Gate restante

Un smoke humain doit encore confirmer dans Fusion que la palette apparait, se rafraichit, ouvre le recours expert et applique/exporte la scene sans casser le document utilisateur.
