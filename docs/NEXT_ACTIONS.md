# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

`V0.1 - MVP reouvert : editeur premium et solveur d enveloppes extensibles`.

La vision canonique est `docs/CANONICAL_PRODUCT_VISION.md`. ADR-0053 retire la
fausse acceptance P43. ADR-0054 fixe la semantique centrale : les assets
calibrent les cavites ; les enveloppes des bacs demandes absorbent le volume
restant dans leurs parois et fonds ; aucun micro-remplissage automatique.

## Derniere mission terminee

`P53 - Contrat cavites fixes et enveloppes extensibles` : vision, geometrie,
contrat MVP et backlog corriges. P39/P40 restent reutilisables ; la strategie de
residus automatiques P41/P42 est obsolete pour le produit.

## Prochaine mission prete

`P54 - Architecture UX de l editeur premium`.

Resultat attendu : une reference visuelle et interactionnelle complete avant le
code frontend. Elle couvre toutes les saisies demandees, le mode simple et les
parametres avances, les etats du parcours et la passerelle Fusion. Aucune nouvelle
question de surface n est demandee : l editeur premium est l interface produit
complete ; Fusion materialise, controle et exporte.

## Releases bloquees

P44 a P50 restent bloques jusqu a P60 : aucune esthetique V0.2 ni couvercle V0.3
avant l acceptance du comportement V0.1 corrige.

## Gate humaine active

Aucune gate active maintenant. Le prochain retour humain obligatoire sera le
smoke Fusion P60, une fois l editeur, le solveur, le resultat et la CAD deja
prouves automatiquement.

## Fin de chaque mission

Tests pertinents, `git diff --check`, commit atomique, integration directe dans
`main`, push, puis mission suivante seulement si ses dependances sont terminees.
