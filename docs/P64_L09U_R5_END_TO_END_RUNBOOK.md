# P64-L09U-R5 — runbook accès des cavités partiellement recouvertes

## Objectif

Corriger le seul défaut bloquant observé dans 0.1.75 : une cavité partiellement
recouverte par un plateau doit rester ouverte dans sa portion hors plateau,
sans retirer ses parois ni modifier son calibre.

Cible : 0.1.76.

## Autorités

- `docs/P64_L09U_R4_V_0175_HUMAN_KO_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0100-plateau-amovible-et-cavite-sans-paroi-intermediaire.md` ;
- `docs/DECISIONS/ADR-0101-acces-local-des-cavites-partiellement-recouvertes.md`.

## Invariants

- Cavité, asset et conteneur gardent leurs dimensions, poses et identités.
- Sous plateau, la cavité rejoint toujours directement la découpe locale.
- Hors plateau, seule l'empreinte de la cavité est ouverte jusqu'à la face
  fonctionnelle locale.
- Les parois latérales, le fond et les appuis du plateau sont conservés.
- Plusieurs paliers restent locaux.
- Aucun benchmark, holdout, corpus ou tournoi solveur.
- Les projets personnels restent strictement en lecture seule.

## Programme

1. Consigner le KO humain 0.1.75.
2. Réintroduire les accès verticaux à partir du contrat final de cavité.
3. Borner chaque accès à l'intersection cavité/prisme composite.
4. Arrêter chaque accès au dessous de sa découpe locale ou au sommet local hors
   plateau.
5. Propager ces coupes dans l'aperçu, la CAD IR et le plan Fusion.
6. Tester un chevauchement partiel et plusieurs niveaux locaux.
7. Lancer les tests ciblés puis la suite autorisée.
8. Rejouer les trois projets personnels en lecture seule.
9. Intégrer, installer 0.1.76 et préparer la nouvelle gate humaine.

## Gate R5-V

Thomas vérifie en priorité une cavité partiellement recouverte :

1. sous le plateau, aucune matière intermédiaire ;
2. hors plateau, aucun plafond au-dessus de l'asset ;
3. autour de la cavité, parois et appuis toujours présents ;
4. profondeur, position et aperçu inchangés ;
5. comportement identique sur les autres cas plateau.

`fusion-validated=false`, `print-validated=false` avant ce verdict.
