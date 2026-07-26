# P64-L09S-V - recette de gate Fusion humaine

## Statut courant

- Gate : obligatoire, humaine, non encore observee.
- Package unique autorise : `0.1.68`.
- Packages `0.1.65` et `0.1.67` : `human-KO`, `do-not-run`.
- Preparateur canonique : `scripts/fusion/prepare_p64_l09sv_gate.ps1`.
- Benchmark, holdout et corpus : interdits.
- Impression : `print-validated=false`.

Codex installe le package, la fixture publique, le runtime SCIP et les reglages utiles avant de demander une action a Thomas. Thomas ne lance aucune commande PowerShell.

## Preconditions preparees par Codex

- le SHA integre dans `main` correspond au marqueur installe ;
- le manifeste installe annonce `0.1.68` ;
- les marqueurs `p64-l09s-v2`, pool minimal, reconstruction des frontieres et finaliseur `v8` sont presents ;
- SCIP produit est configure dans l add-in ;
- la fixture publique et le recu de preflight sont installes ;
- les budgets Calcul et Finalisation sont visibles et reactifs.

## 1. Smoke public

1. Recharge completement BGIG `0.1.68` et ouvre Atelier de rangement.
2. Verifie les couleurs : Calculer bleu, Finaliser orange, Materialiser vert ; les etats desactives restent explicites.
3. Ouvre la fixture publique preparee et calcule en Normal.
4. Verifie l enveloppe minimale `23.2 x 23.2 x 31.6 mm`, le gap autorise sous plateau et une croissance artificielle nulle.
5. Finalise puis materialise : plan courant, residuel imprimable nul, annexes soudees, encoches exactes et un composant utilisateur par proprietaire.

## 2. CasLimite01 avec plateaux

1. Ouvre le projet local `CasLimite01` sans le modifier hors ajout/retrait des plateaux necessaires au scenario.
2. Confirme le succes de reference sans plateau, puis ajoute un plateau et calcule en Approfondi.
3. Recommence avec plusieurs plateaux.
4. Les deux calculs avec plateau doivent trouver une solution certifiee via la lane SCIP, puis recertifier les vrais prismes reserves.
5. Aucun volume minimal ne diminue, aucun axe fixe ne change et aucun conteneur ne grandit pour fabriquer un support.
6. Un gap sous plateau est admis. Une intersection avec un prisme reserve doit etre rejetee, jamais masquee.
7. Finalise puis materialise chaque variante retenue. Exige un plan courant, un residuel nul et aucune annonce de succes sur echec.

## 3. CasLimite02 avec deux plateaux

1. Ouvre le projet local `CasLimite02` avec ses deux plateaux et calcule.
2. Finalise avec le budget visible choisi. Le pool borne peut retenir un autre plan minimal certifie, mais une seule date limite totale s applique.
3. Exige `finalized_plan` courant, certificats produit et composite valides, et `printable_residual_volume_mm3=0`.
4. Verifie que `c2` conserve exactement son axe X fixe et que chaque union finale contient son enveloppe minimale source.
5. Materialise et controle : un seul composant utilisateur par proprietaire, annexes XY soudees par vraie face, unions avant coupes, encoches seulement sur les corps atteignant le plan reserve et chevauchant son empreinte.

## 4. Verite UX et diagnostics

- Le bouton Materialiser ne s active qu apres un vrai plan materialisable courant.
- Un timeout ou rejet conserve le plan minimal et affiche le motif reel.
- Aucun `finalized_plan_ready` ou `Projet accepte` n apparait sans plan final recertifie.
- Les diagnostics identifient le candidat minimal choisi, le nombre de tentatives et la lane SCIP lorsque pertinente.

## 5. Verdict

La gate est `human-OK` seulement si le smoke public, `CasLimite01` avec un puis plusieurs plateaux, et `CasLimite02` avec deux plateaux passent tous du calcul a la materialisation.

Tout echec de calcul avec plateau, rabotage de minimum, croissance de support, residuel non nul, faux succes, annexe separee, encoche hors cible, identite stale ou erreur Fusion donne `human-KO` immediat.

La gate ne vaut jamais validation d impression : `print-validated=false`.

## Historique

- `0.1.65` : support artificiel sous plateau et faux succes de finition, `human-KO`.
- `0.1.67` : `CasLimite01` ne calcule plus avec plateau et `CasLimite02` ne finalise pas, `human-KO`.
- Preuve : `docs/P64_L09S_V_0167_HUMAN_KO_EVIDENCE.md`.