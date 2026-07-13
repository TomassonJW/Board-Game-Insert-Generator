# Next Actions

Derniere mise a jour : 2026-07-13

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P65-M004 - explications de l Apercu et actions finales, palette et package 0.1.19.

## Derniere preuve automatisee

P65-M004 ajoute bgig.preview_explanations.v1 au resultat Python. La palette
traduit score comparatif, appuis, ordre de retrait, residuels et suggestions
sans exposer de codes solveur. Exporter les imprimables est primaire dans
Apercu ; Recalculer et Materialiser dans Fusion restent uniquement dans la
barre persistante. Aucun score, solveur, tolerance, corps ou geometrie n est
modifie.

Preuves : 445 tests automatises verts, syntaxe JavaScript, compilation Python,
git diff --check, installation locale Fusion 0.1.19 et controle des marqueurs verts.
Aucune validation Fusion ni impression reelle n est revendiquee.

## Mission courante

Aucune implementation en cours. P65 est integree dans main ; P66-M000 est la
prochaine mission preparee.

## Prochaine action recommandee

P66-M000 - Quarantaine des complements experimentaux dans la palette.

Statut : ready. Retirer du parcours normal les actions Bac vide, Bloc plein /
cale et Separateur, sans supprimer leur schema, leur loader ou la compatibilite
des anciens projets. Aucun solveur, tolerance, geometrie ou corps automatique ne
change. Package cible : 0.1.20.

Contrat : `docs/P66_TERRA_EXECUTION_CONTRACT.md` et ADR-0061. Apres integration
et tests de P66-M000, P66-M001 prepare les fixtures, le package et la checklist,
puis s arrete a la gate humaine P66-V.

## Releases bloquees

P44-P46 restent bloques jusqu a P66 OK puis acceptation humaine P67. P47-P50
restent bloques jusqu a P46. P68 recueille des observations physiques sans
changer les defaults ; P69 reste bloque jusqu a P50.

## Gate humaine active

P66-M000 et P66-M001 sont des missions bornees sans gate humaine. P66-V demande
ensuite une observation Fusion preparee automatiquement. Apres P66 OK, P67 est
la gate humaine de priorisation avant toute implementation P44.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes. print-validated: false reste obligatoire.
