# 2026-07-22 — P64-L04A réutilisation locale pré-finalisation

## Mission

Formaliser les réserves issues de l’observation du package 0.1.57, puis livrer
uniquement l’insertion locale à enveloppe fixe. Approfondi et l’attente UX sont
maintenus dans des lots séparés.

## Décision

ADR-0075 accepte une voie pré-finalisation distincte de C01/C02. P45 conserve
les variantes et le certificat local ; P64 conserve les poses monde et rejoue
le certificat global sans recherche.

## Livré

- contrat P64-L04 et ADR-0075 ;
- producteur `incremental_fixed_envelope_v1` borné ;
- fallback vers une variante certifiée de même enveloppe ;
- lifecycle staged, bridge `validate_project` et feedback palette ;
- package 0.1.58 ;
- evidence `P64_L04A_INCREMENTAL_LOCAL_REUSE_EVIDENCE.md` ;
- pilotage synchronisé vers L04B, L04C et L04V.

## Preuves

- tests L04A : 9/9 ;
- bridge : 22/22 ;
- DOM : 34/34 ;
- staged historique : 10/10 ;
- suite complète : 636/636 en 154,576 s ;
- Ruff, py_compile et `node --check` : OK.
- `compileall` et frontière `adsk` : OK ;
- `git diff --check` : OK, avertissements de normalisation CRLF uniquement.

La première tentative de suite complète a été KO car le wrapper ne recevait pas
`PYTHONPATH=src` et parce qu’un repère historique avait été retiré de
`NEXT_ACTIONS.md`. Les deux causes ont été corrigées ; la relance gardée est
verte. Ce KO n’était pas une régression du moteur L04A.

## Limites

- aucun changement de solveur, budget, schéma ou valeur physique ;
- aucun solve global ou scène automatique pendant l’édition locale ;
- producteur rectangulaire, faux négatifs possibles ;
- cas dense 11 × 34 inchangé ;
- `fusion-validated: false`, `print-validated: false`.

## Suite

P64-L04B : incumbent Normal, Approfondi anytime et deadline stricte. Puis
P64-L04C : activité, étape et temps écoulé sans faux pourcentage. P64-L04V
regroupera la prochaine observation Fusion.
