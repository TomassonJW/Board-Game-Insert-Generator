# P64-L09U-R8-B — preuve de décision du pipeline soustractif

Date : 2026-07-28.

Statut : `done-architecture`, `ADR-0105-accepted`,
`P64-L09U-R8-C-ready`, `fusion-validated=false`,
`print-validated=false`.

## Décision

ADR-0105 retient une séparation obligatoire :

```text
plan minimal
-> conteneurs finalisés et géométrie positive figée
-> passe d'encastrement uniquement soustractive
-> aperçu / CAD IR / Fusion / BRep
```

La matière finale vaut :

```text
conteneurs finalisés - union des encastrements locaux
```

## Invariants exécutables

- volume positif lié aux éléments plats : `0 mm³` ;
- corps positif lié aux éléments plats : `0` ;
- union positive liée aux éléments plats : `0` ;
- digest de géométrie positive inchangé par la passe plate ;
- profondeur locale exacte `4/2/6 mm` ;
- intervalle métier identique à l'outil BRep ;
- cavités, accès, fonds, parois, ordre automatique et grille `0,1 mm`
  préservés.

Une égalité entre volume ajouté et volume à couper n'est plus une preuve
d'absence de matière positive.

## Compatibilité

Le solveur, les budgets, les valeurs physiques, le BRep transitoire, la
persistance unique et le rollback ne changent pas.

ADR-0105 remplace uniquement :

- l'exécution depuis `cad_origin_mm` / `cad_size_mm` d'ADR-0098 ;
- l'extension CAD évoquée par ADR-0102 ;
- le certificat amont fondé sur une compensation de volumes.

ADR-0095 à ADR-0097 restent hors scope.

## Découpage

1. R8-C : prouver la frontière minimale sans géométrie positive plate ;
2. R8-D : produire les conteneurs finalisés et figer leur digest positif ;
3. R8-E : produire et exécuter les seules soustractions ;
4. R8-F : prouver la fidélité de bout en bout ;
5. R8-G : préparer et installer la candidate.

Aucun benchmark, holdout, corpus, tournoi, package ou code produit n'est
modifié par R8-B.

Décision :
`docs/DECISIONS/ADR-0105-conteneurs-finalises-et-encastrements-strictement-soustractifs.md`.

Diagnostic :
`docs/P64_L09U_R8_A_SUBTRACTIVE_PIPELINE_DIAGNOSTIC_EVIDENCE.md`.
