# 2026-07-12 - P56 editeur Fusion embarque

## Contexte

ADR-0055 impose l add-in Fusion comme surface produit unique du MVP. P56 devait
remplacer la palette minimale P32 sans reutiliser le prototype web abandonne.

## Changements

- palette a six vues, tables dynamiques et mode simple/avance ;
- bridge bgig.palette.request.v1 / bgig.palette.response.v1 ;
- normalisation, contrats P40/P55 et erreurs dans Python pur ;
- sauvegarde atomique, reprise, import et export locaux ;
- moteur Python pur embarque par l installateur dans l add-in ;
- smoke P56 Fusion-only automatise jusqu a l installation.

## Verifications

- 6 tests bridge : OK ;
- 5 tests DOM : OK ;
- 87 tests Fusion existants : OK ;
- syntaxe JavaScript embarquee : OK ;
- dry-run et installation AppData avec marqueurs runtime : OK ;
- controle visuel Fusion : non observe, runtime Windows bloque par apply deny-read ACLs.

## Impact

P56 est implemente et P57 peut commencer. Aucun statut fusion-validated ou
print-validated n est revendique.

## Suivi

- P57 : solveur de partition et expansion conjointe sans corps automatique.
