# P64-L09S-V - recette de gate Fusion humaine

## Statut historique clos

- Gate : `human-KO` apres les observations et variantes locales du 2026-07-26.
- Package `0.1.69` : `do-not-run`.
- Acquis conserves : jauge fluide, minima des cas de base et cavite orientee.
- Successeur : P64-L09T, puis nouvelle gate humaine P64-L09T-V.
- Preuve : `docs/P64_L09S_V_0169_HUMAN_KO_EVIDENCE.md`.
- `fusion-validated=false`, `print-validated=false`.

La recette ci-dessous est conservee comme historique de l'observation 0.1.69.
Elle ne doit plus etre executee.

- Gate : historique, observee puis refusee.
- Ancien package observe : `0.1.69`.
- Packages `0.1.65`, `0.1.66`, `0.1.67` et `0.1.68` :
  `human-KO`, `do-not-run`.
- Preparateur canonique : `scripts/fusion/prepare_p64_l09sv_gate.ps1`.
- Benchmark, holdout et corpus : interdits.
- Impression : `print-validated=false`.

Codex installe le package, la fixture publique, le runtime SCIP et les reglages utiles avant de demander une action a Thomas. Thomas ne lance aucune commande PowerShell.

## Preconditions preparees par Codex

- le SHA integre dans `main` correspond au marqueur installe ;
- le manifeste installe annonce `0.1.69` ;
- les marqueurs `p64-l09s-v3`, piles au sol reservees, pool minimal,
  reconstruction des frontieres et finaliseur `v8` sont presents ;
- l'evenement `bgig_palette_operation_ready` est present et le polling
  periodique du pont Python est absent ;
- SCIP produit est configure dans l add-in ;
- la fixture publique et le recu de preflight sont installes ;
- les budgets Calcul et Finalisation sont visibles et reactifs.

## 1. Smoke public

1. Recharge completement BGIG `0.1.69` et ouvre Atelier de rangement.
2. Verifie les couleurs : Calculer bleu, Finaliser orange, Materialiser vert ; les etats desactives restent explicites.
3. Ouvre la fixture publique preparee et calcule en Normal.
4. Verifie l enveloppe minimale `23.2 x 23.2 x 31.6 mm`, le gap autorise sous plateau et une croissance artificielle nulle.
5. Finalise puis materialise : plan courant, residuel imprimable nul, annexes soudees, encoches exactes et un composant utilisateur par proprietaire.

## 2. CasLimite01 avec plateaux

1. Ouvre le projet local `CasLimite01` avec ses 18 conteneurs et son plateau
   central a 100 %, sans modifier les dimensions.
2. Choisis Calcul Normal et Finition Normal, puis lance Calculer.
3. Observe la jauge : elle avance environ chaque seconde, sans saut 4 -> 10,
   7 -> 20 ni gel jusqu'au retour.
4. Le calcul avec plateau doit produire un plan certifie. La voie bornee de
   piles au sol ou SCIP peut gagner ; le certificat commun reste l'autorite.
5. Aucun volume minimal ne diminue, aucun axe fixe ne change et aucun
   conteneur ne grandit pour fabriquer un support.
6. Finalise. Exige un `finalized_plan` courant,
   `printable_residual_volume_mm3=0` et aucune annonce de succes sur echec.
7. Materialise et verifie les 18 conteneurs, les encoches plateau et l'absence
   de corps utilisateur correspondant au plateau virtuel.

## 3. CasLimite02 avec deux plateaux

1. Ouvre le projet local `CasLimite02` avec plateau et livret, puis calcule en
   Normal.
2. Avant finition, confirme que le bac de cartes debout garde sa profondeur de
   cavite canonique `63.6 mm`.
3. Finalise en Rapide. Exige un `finalized_plan` courant, les certificats
   valides et `printable_residual_volume_mm3=0`.
4. Materialise et mesure la cavite finale du bac de cartes debout : `67.6 mm`
   pour le projet courant, jamais environ `24 mm`; le fond reste `2.2 mm`.
5. Controle un seul composant utilisateur par proprietaire, unions avant
   coupes et encoches seulement sur les corps atteignant le plan reserve et
   chevauchant son empreinte.

## 4. Verite UX et diagnostics

- Le bouton Materialiser ne s active qu apres un vrai plan materialisable courant.
- Un timeout ou rejet conserve le plan minimal et affiche le motif reel.
- Aucun `finalized_plan_ready` ou `Projet accepte` n apparait sans plan final recertifie.
- Les diagnostics identifient le candidat minimal choisi, le nombre de tentatives et la lane SCIP lorsque pertinente.
- Calculer reste bleu, Finaliser orange ou violet, Materialiser vert.
- La jauge disparait au repos et reste fluide pendant le calcul natif.

## 5. Verdict

La gate aurait ete `human-OK` seulement si le smoke public, `CasLimite01` avec un puis plusieurs plateaux, et `CasLimite02` avec deux plateaux passaient tous du calcul a la materialisation.

Tout echec de calcul avec plateau, rabotage de minimum, croissance de support, residuel non nul, faux succes, annexe separee, encoche hors cible, identite stale ou erreur Fusion donne `human-KO` immediat.

La gate ne vaut jamais validation d impression : `print-validated=false`.

## Historique

- `0.1.65` : support artificiel sous plateau et faux succes de finition, `human-KO`.
- `0.1.67` : `CasLimite01` ne calcule plus avec plateau et `CasLimite02` ne finalise pas, `human-KO`.
- `0.1.68` : calcul avec plateau encore KO sur `CasLimite01`, cavite cartes
  rabotee et jauge gelee, `human-KO`.
- Preuves : `docs/P64_L09S_V_0167_HUMAN_KO_EVIDENCE.md` et
  `docs/P64_L09S_V_0168_HUMAN_KO_EVIDENCE.md`.
