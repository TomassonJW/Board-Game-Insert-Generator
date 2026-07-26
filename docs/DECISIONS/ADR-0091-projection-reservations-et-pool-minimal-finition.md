# ADR-0091 - projection des reservations hautes et pool minimal de finition

## 1. Statut

Acceptee le 2026-07-26 dans le Goal P64-L09S. Cette decision complete ADR-0089 et ADR-0090 sans modifier les tolerances physiques.

## 2. Contexte

Deux echecs humains differents subsistent dans `0.1.67`. Un cas dense resolu par SCIP sans plateau devient introuvable des qu une reservation haute est ajoutee. Un autre cas calcule avec deux plateaux mais la finition rejette les corps composites a axe fixe ou s arrete sur le seul plan minimal selectionne.

Une reservation plateau/livret ne doit jamais fabriquer un porteur, reduire un minimum ou remplacer le solveur 3D complexe. Une finition ne peut reussir qu avec une couverture exacte et un plan courant recertifie.

## 3. Decision

1. Quand des reservations hautes existent, le calcul peut chercher d abord sur une projection sans plateau/livret, avec les memes conteneurs, variantes, minima, axes fixes et contraintes de boite.
2. SCIP reste la lane externe du calcul 3D complexe. La projection peut l appeler une seule fois ; la passe reservee suivante reutilise les candidats et ne relance pas SCIP.
3. Chaque candidat projete est recertifie contre les vrais prismes reserves avant publication. Un conflit est un rejet ferme. Aucun conteneur ne grandit pour soutenir un plateau et un gap sous plateau reste permis.
4. Le solveur conserve au plus douze plans minimaux certifies et distincts, classes par les criteres existants. Le plan selectionne reste le premier candidat.
5. La finalisation essaie ce pool sous une seule date limite totale. Chaque tentative conserve ses motifs d arret et ne prolonge jamais le budget choisi.
6. Si les frontieres de variantes ne sont pas transmises par l appelant, la finalisation les reconstruit avec le contrat produit courant avant de certifier les corps.
7. Chaque corps final, coeur plus annexes XY soudees, contient son enveloppe minimale source. Les axes fixes restent exactement fixes. Aucune rotation, variante ou finition ne peut raboter un minimum.
8. Un succes exige un `finalized_plan` courant, un residuel imprimable nul, les certificats produit et composite valides, puis une materialisation fidele.

## 4. Consequences

Le cas dense avec plateau beneficie du placement SCIP faisable sans imposer au solveur une geometrie de support interdite, mais reste refuse si ce placement traverse reellement un prisme reserve.

La finition peut choisir un autre plan minimal certifie sans recalcul illimite. Le cout reste borne par douze candidats et une date limite partagee. La telemetrie indique le candidat choisi et chaque tentative.

Le resultat peut etre `no_solution_within_budget` plus souvent qu une deformation silencieuse. Ce comportement est volontaire.

## 5. Alternatives rejetees

- Agrandir en Z un conteneur pour atteindre le plateau : interdit par ADR-0089.
- Reduire une enveloppe minimale ou ignorer un axe fixe : perte physique inadmissible.
- Relancer SCIP pour chaque passe reservee ou chaque candidat de finition : budget non borne et attente UX trompeuse.
- Finaliser uniquement le plan minimal classe premier : insuffisant pour les fermetures complexes.
- Valider un composite avec les seules enveloppes generiques : faux rejet des variantes et axes fixes.

## 6. Validation

La validation automatisee couvre l unique appel SCIP projete, la recertification des reservations, le pool borne, la date limite historique, le residuel nul, les unions composites, les minima et les axes fixes. La validation produit finale reste humaine dans Fusion sur `CasLimite01` et `CasLimite02`. `print-validated=false`.