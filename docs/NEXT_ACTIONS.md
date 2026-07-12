# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

`V0.1 - MVP reouvert : reprise qualite produit`.

La vision canonique reste `docs/CANONICAL_PRODUCT_VISION.md`. L audit de realite
est `docs/MVP_V01_REALITY_AUDIT.md` et le contrat de sortie est
`docs/MVP_V01_ACCEPTANCE_CONTRACT.md`. ADR-0053 remplace la lecture trop large
de P43 : une scene Fusion observee ne vaut pas acceptance produit.

## Derniere mission terminee

`P52 - Remise a plat V0.1` : retrait du faux statut `MVP accepte`, audit des
ecarts, contrat d acceptation testable et backlog de reprise. Aucun code
fonctionnel n a ete ajoute dans ce lot documentaire.

## Prochaine decision necessaire

`P53 - Surface principale et reference UX` est volontairement en attente d une
courte relecture produit. Le point a confirmer est simple : le Studio local est
la surface complete de saisie et de resultat ; Fusion materialise et exporte,
mais ne devient pas un second editeur incomplet. La palette Fusion doit permettre
d ouvrir ou retrouver clairement le Studio et ne jamais rester sur Chargement.

## Releases bloquees

P43 est reouvert. P44 a P50 restent bloques : aucun arrondi, encoche ou couvercle
ne doit etre implemente avant la nouvelle acceptance V0.1.

## Gate humaine active

Aucune nouvelle preuve Fusion n est demandee maintenant. La prochaine gate Fusion
arrivera uniquement apres P57, sur la scene finale choisie ; l UI et la qualite
du resultat doivent etre prouvees avant.

## Fin de chaque mission

Tests pertinents, `git diff --check`, commit atomique, integration directe dans
`main`, push, puis selection de la mission suivante seulement si elle ferme un
critere du contrat V0.1.
