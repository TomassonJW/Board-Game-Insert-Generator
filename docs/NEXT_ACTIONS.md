# Next Actions

Dernière mise à jour : 2026-07-18

## Version active

V0.1 reste `mvp-accepted` par P66, `fusion-validated: true` et
`print-validated: false`. P44 poursuit la fondation UX V0.2, mais P44-V reste en
KO contextuel. P64-V2H02R est fusion-validated. P64-V2H03A a fermé l'arbitrage
architectural sans modifier le runtime.

## Dernier état réel

- P44-M009H05 reste `fusion-validated` dans Fusion 0.1.36 ; le package
  initial P44-M007 0.1.37 est supersédé par ses correctifs.
- P44-VH02 a corrigé la suppression directe et le nommage incrémental ; ses
  faits UX restent acceptés contextuellement sans valider le solveur.
- P64-H01 reste `fusion-validated` par
  `P64-H01 Fusion OK 0.1.42 - commit 5865645`.
- P64-V2H02R est `fusion-validated` dans Fusion 0.1.54 par
  `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`.
- La preuve couvre capacité informative, vérité des statuts, budgets, méthodes,
  occlusion et orientation de la vue de dessus.
- Le projet dense de référence reste `no_solution_within_budget` malgré environ
  693,6 cm³ de marge théorique ; cette marge ne prouve pas une disposition.
- ADR-0070 et
  `docs/P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md` fixent la
  frontière : P45 possède la sémantique et la certification locale ; P64
  consomme les variantes certifiées et possède la sélection globale.
- Aucun schéma projet, solveur public, default, jeu, tolérance, valeur physique,
  scène ou matérialisation automatique n'a changé dans P64-V2H03A.

## Prochaine action recommandée

### P64-V2H03B — Frontière locale, certificats et fixtures

P64-V2H03B est la seule mission `ready`.

Périmètre :

1. introduire les types immuables de variante, identité et digest ;
2. extraire la variante `canonical_v1` sans changer ses sorties publiques ;
3. ajouter le producteur technique `bounded_rectangular_relayout_v1` ;
4. certifier localement cavités, contenus, jeux, parois, cloisons et fond ;
5. dédupliquer et construire une petite frontière non dominée ;
6. figer les fixtures de parité, duplication, rotation, cul-de-sac
   multi-cavités, réservation localisée et cas dense anonymisé ;
7. mesurer puis verrouiller les caps Rapide/Normal/Approfondi.

Interdits du lot : branchement dans la sélection publique, nouveau contrôle
Fusion, mode P45, changement de résultat utilisateur, schéma projet, valeur
physique ou scène automatique.

Validation cible : parité canonique aux frontières publiques, digests
déterministes, certificats fail-closed, génération bornée, suite complète,
`compileall`, frontière `adsk` et `git diff --check`.

Modèle conseillé : `gpt-5.6-sol`, raisonnement `xhigh`. Alternative économique :
`gpt-5.6-terra`, raisonnement `max`, avec un risque supérieur de reprise sur les
digests, symétries et invariants de monotonie.

## Lots suivants, non ouverts

1. P64-V2H03C : sélection globale paresseuse, lanes préservées, budgets et
   télémétrie ; bloquée par P64-V2H03B.
2. P64-V2H03V : gate Fusion préparée seulement après C si le comportement
   visible change.
3. P44-V, puis P45/P46 selon leurs contrats et gates.
4. P64-F01 restant / P64-F02 après P46.
5. P64-U01 : progression non modale et annulable.
6. P64-X01 : moteur exact éventuel après benchmark, ADR de dépendance et GO
   distinct.

## Séquence verrouillée

Une seule mission est active. P45 ne commence pas dans P64-V2H03B ; ses futurs
modes et formes restent hors scope. P44-V et P46 restent bloquées. P47-P50
restent bloquées jusqu'à P46 et P69 jusqu'à P50. P68 peut recueillir des faits
réels sans recalibrer les defaults.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans `main` lorsqu'aucune gate humaine n'est ouverte.
Une gate Fusion ne devient jamais une validation d'impression.