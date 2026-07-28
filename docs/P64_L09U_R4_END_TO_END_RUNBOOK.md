# P64-L09U-R4 — runbook cavités ouvertes sous plateaux

## Objectif

Corriger le seul défaut bloquant observé dans 0.1.74 : supprimer la matière
imprimée entre un encastrement de plateau et les cavités qu'il recouvre, sans
régression des profondeurs, réservations locales, budgets ou booléens Fusion.

Cible initiale : `0.1.75`.

## Autorités

- `docs/P64_L09U_R3_V_0174_HUMAN_KO_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0100-plateau-amovible-et-cavite-sans-paroi-intermediaire.md` ;
- `docs/DECISIONS/ADR-0099-profondeur-calibree-et-reservations-superieures-locales.md` ;
- `docs/P64_L09U_R3_END_TO_END_RUNBOOK.md`.

## Invariants

- Cavité sans plateau : comportement 0.1.74 inchangé.
- Cavité sous plateau : profondeur, X/Y, orientation et dimensions inchangés.
- Sommet de cavité égal au dessous de la découpe locale responsable.
- Seule une coupe réellement portée par le même conteneur peut abaisser la
  cavité ; une réservation globale située plus haut ne suffit pas.
- Une cavité sans coupe locale reste ouverte sur la face fonctionnelle locale
  de son corps composite, même si celle-ci est sous le sommet global du module.
- Séparation et matière intermédiaire exactement nulles.
- Fond et parois latérales canoniques préservés.
- Réservations disjointes ou empilées toujours locales.
- Plateaux et livrets toujours virtuels.
- Corps BRep transitoire, zéro Combine rectangulaire, rollback et respiration
  entre modules préservés.

## Programme

1. Consigner le KO 0.1.74 et superséder la séparation erronée.
2. Corriger l'ancrage final et publier la continuité dans le certificat,
   l'aperçu, la CAD IR et le plan Fusion.
3. Refuser tout artefact sous plateau contenant une matière intermédiaire.
4. Tester un plateau, plusieurs paliers et toutes les cavités ancrées.
5. Lancer les tests ciblés puis la suite complète autorisée.
6. Rejouer les trois projets personnels en lecture seule, SHA-256 avant/après.
7. Intégrer 0.1.75 dans `main`, vérifier le distant, installer et préparer R4-V.

## Gate R4-V

Thomas vérifie uniquement :

1. sans plateau, les cavités restent ouvertes et calibrées ;
2. avec plateau, chaque cavité recouverte devient visible et accessible dès
   que le plateau est retiré ;
3. aucune dalle ne subsiste entre plateau et cavité ;
4. `CasLimite02+` conserve ses coupes et paliers locaux ;
5. aperçu, Fusion, temps et matérialisation progressive restent conformes.

Codex ne promeut jamais seul `fusion-validated` ou `print-validated`.
