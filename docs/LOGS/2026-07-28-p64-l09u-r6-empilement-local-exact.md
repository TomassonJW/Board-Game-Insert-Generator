# 2026-07-28 — P64-L09U-R6, empilement local exact

## Contexte

La gate 0.1.76 est close en `human-KO`, `do-not-run`. Elle a conservé les
progrès R5, mais une micro-partie de cavité perdait les `6 mm` des deux
éléments plats et deux empreintes différentes ne produisaient pas deux
encastrements locaux cohérents.

## Décision

ADR-0102 formalise une partition XY atomique et des intervalles Z locaux. Les
zones disjointes ne cumulent rien ; les intersections cumulent uniquement les
éléments présents ; chaque intervalle reste identifiable jusqu'au plan Fusion.

## Résultat automatisé

- finaliseur v12 ;
- candidate 0.1.77 ;
- digest de preflight
  `de55e8e85652ecb6d01e44b7494b7adc7f92ee2472c8e3c6874836f93823f6b6` ;
- suite autorisée `909/909`, un test SCIP ignoré ;
- trois replays personnels exacts en lecture seule ;
- SHA source inchangé :
  `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC`.

## Statut

`P64-L09U-R6-automated-validated`, `installed-local`,
`P64-L09U-R6-V-ready-human-gate`, package 0.1.77 du commit `e81737d`,
`fusion-validated=false`, `print-validated=false`.
