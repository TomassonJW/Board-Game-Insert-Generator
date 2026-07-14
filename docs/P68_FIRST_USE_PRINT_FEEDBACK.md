# P68 - Boucle de premiers inserts imprimes et retours mesures

Statut : `planned-after-p66`, `human-print-observation`,
`does-not-change-default-tolerances`.

## Role

P68 recueille les premiers retours d usage et d impression de vrais inserts
BGIG. Il est distinct de P50 : P50 calibre les mecanismes de couvercle V0.3 ;
P68 apprend sur les bacs ouverts, cavites, plateaux encastres et ergonomies V0.1
ou V0.2.

P68 n est pas un pretexte pour declarer toutes les imprimantes compatibles ni
pour modifier les tolerances globales. Une mesure locale peut devenir une
proposition de calibration, soumise ensuite a une decision humaine distincte.

## Protocole minimal

Pour chaque insert imprime, consigner :

- commit/package BGIG et fichier projet ;
- imprimante, filament, buse, hauteur de couche et profil slicer ;
- dimensions prevues et mesurees des bacs et cavites ;
- jeu plateau/livret, retrait des cartes/tokens et stabilite ;
- qualite des coins, chanfreins, encoches et fonds quand ils existent ;
- poids, duree d impression, deformations, echecs et photos utiles ;
- statut `measured_local_ok`, `measured_local_ko` ou `retest_required`.

## Lien avec P67 et P44-P50

Les impressions peuvent etre realisees des que P66 est acceptee, y compris pour
un usage personnel immediat. Elles restent des observations locales tant que le
rapport n est pas complete. P67-V a choisi la fondation UX ; les mesures P68
nourrissent notamment le contrat de jeux P44-M008, les geometries P45 et la
gate P46 sans changer silencieusement les defaults. P68 ne
bloque pas formellement P47, mais ses mesures doivent etre examinees avant toute
calibration fonctionnelle P50. P69 utilise ensuite ces retours dans la revue
UI/UX exhaustive apres V0.3.

## Sortie

Un rapport `docs/P68_FIRST_USE_PRINT_REPORT.md` est cree pour chaque lot de
tests physiques. Il ne change aucun statut global sans revue humaine.
