# ADR-0083 — Gate réelle de solvage 3D et requalification de P64-L07

## Statut

Acceptée le 2026-07-24 par GO explicite de Thomas.

## Contexte

P64-L07 a bien audité et exécuté des moteurs externes, mais tous les adapters de
comparaison ont reçu le même sous-problème `external_floor_problem.v1` :
rectangles orthogonaux au fond de la boîte, sur un seul niveau.

Cette réduction est incompatible avec le besoin produit prioritaire : trouver et
appliquer les meilleurs algorithmes pour les cas limites BGIG à forte cardinalité,
en 3D réelle, avec étages, empilement, appuis, réservations, retraits et variantes
locales. Le programme L07 annonçait pourtant des cas à un à trois niveaux.

Le holdout L07 confirme la rupture : 7 cas seulement sur 64 étaient traduisibles
sans perte ; 55 étaient `unsupported`. Les gains HiGHS L07E sont donc valides
uniquement pour une lane de sol rectangulaire. Ils ne justifient ni une victoire
de solveur global, ni une validation Fusion de la capacité 3D, ni une promesse de
vitesse sur les cas denses.

## Décision

1. P64-L07 est requalifié en `benchmark externe partiel de lane de sol`.
   Ses mesures, licences, outils et résultats restent historiques et vérifiables,
   mais son statut `external-benchmark-complete` ne vaut plus pour le solveur
   global BGIG.
2. La gate Fusion P64-L07V est suspendue : elle n'apporterait aucune preuve sur
   le besoin prioritaire et ne doit pas consommer de temps humain.
3. La lane HiGHS 2D reste une optimisation expérimentale et spécialisée. Elle ne
   peut plus être décrite comme le moteur gagnant de BGIG. P64-L08B doit mesurer
   son coût réel et la mettre hors du parcours Auto si elle ralentit ou dégrade un
   cas 3D courant.
4. P64-L08 devient la gate obligatoire avant toute nouvelle revendication de
   progrès de solvage : un benchmark adversarial en 3D complète pour les formes
   rectangulaires T0/T1 actuellement contractées par BGIG.
5. Aucun moteur ne peut gagner globalement par projection 2D, par simplification
   silencieuse ou parce qu'il réussit un unique cas dense. Chaque moteur doit
   déclarer sa portée ; toute contrainte active non représentée produit
   `unsupported` et exclut le moteur du classement de cette famille.
6. T2 à T4 ne sont pas effacés. Ils forment une gate suivante, distincte, dès que
   P45 fournit une représentation et un certificat fidèles. Tant que cette gate
   n'est pas passée, aucune formule ne peut prétendre résoudre « toutes les
   formes BGIG ».

## Gate P64-L08 obligatoire

Un portefeuille n'est intégrable dans le parcours produit que s'il satisfait
toutes les conditions suivantes :

- couverture sémantique de 100 % des familles obligatoires T0/T1 3D ;
- aucune perte de solution certifiée de la baseline sur le corpus ouvert ;
- gain mesuré sur les familles limites, pas seulement sur les cas faciles ;
- performances rapportées par distribution (temps au premier plan certifié,
  P50, P95, mémoire et timeouts), jamais par une moyenne isolée ;
- validation BGIG commune des collisions, appuis, réservations, retraits,
  variantes locales et placements mondes ;
- sélection scellée avant un nouveau holdout indépendant ;
- aucune régression du parcours Rapide ou Normal sur les projets courants ;
- licence, redistribution Windows hors ligne, taille et maintenance acceptées.

Un moteur partiel peut devenir une lane explicitement spécialisée. Il ne peut pas
être promu « meilleur solveur BGIG ».

## Alternatives refusées

- Garder la conclusion L07 car quatre moteurs ont été lancés : les moteurs ont
  été lancés, mais sur le même modèle appauvri ; ce fait ne répond pas à la gate.
- Corriger seulement la communication sans nouveau corpus : cela masquerait le
  défaut de mesure.
- Étendre immédiatement la lane HiGHS 2D : l'extension doit d'abord être
  comparée à des moteurs réellement 3D sous le même contrat sémantique.
- Remplacer le portefeuille interne par un moteur unique : les familles de cas
  peuvent exiger des stratégies complémentaires ; la sélection doit le prouver.

## Conséquences

- Les preuves L07 restent utiles pour l'audit de packaging et comme référence de
  sous-problème, mais sont insuffisantes pour orienter le solveur global.
- Une nouvelle sélection consommera un nouveau holdout ; L06 et L07 restent
  définitivement archivés.
- La mission suivante commence par mesurer le coût de la lane HiGHS installée,
  puis par auditer les capacités 3D réelles des candidats avant tout build lourd.
- Aucun changement de géométrie, tolérance, certificat, CAD, scène ou valeur
  physique n'est autorisé par cette ADR documentaire.

## Suivi

- Correction historique : `docs/P64_L07_SCOPE_CORRECTION.md`.
- Programme exécutable : `docs/P64_L08_REAL_3D_SOLVER_BENCHMARK_PROGRAM.md`.
- Première mission : P64-L08B, diagnostic et quarantaine de la lane 2D.
- `fusion-validated: false`. `print-validated: false`.
