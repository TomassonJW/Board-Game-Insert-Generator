# P64-L09U-R9 — handoff de récupération de performance

## Mandat

Thomas autorise explicitement un nouveau Goal autonome, de bout en bout, pour
retrouver la meilleure performance de calcul possible sans dégrader le résultat
Fusion désormais jugé conforme.

Le nouveau clavardage :

- utilise `gpt-5.6-sol` avec raisonnement `max` ;
- crée immédiatement un Goal Codex sans budget de tokens inventé ;
- ne redemande pas de GO entre les missions atomiques normales ;
- travaille exclusivement en français courant et tutoie Thomas ;
- part d'un nouveau worktree créé depuis le `origin/main` vérifié après
  intégration de ce handoff ;
- vérifie lui-même chemin réel, branche, `HEAD`, `origin/main`, divergence,
  propreté et worktrees étrangers avant toute mutation ;
- ne touche jamais un worktree étranger.

## Verdict humain à ne pas redécouvrir

La candidate 0.1.79 est :

- `human-positive` pour la géométrie, l'ordre, les dispositions et le pipeline
  strictement soustractif ;
- `human-KO` pour la performance de calcul ;
- `human-positive-partial` globalement ;
- `fusion-validated=false` ;
- `print-validated=false`.

Thomas ne doit pas rejouer R8. La preuve est :
`docs/P64_L09U_R8_V_0179_HUMAN_POSITIVE_PERFORMANCE_KO_EVIDENCE.md`.

## Faits autoritaires

- Temps antérieur attendu par Thomas : environ `4 s`.
- Temps courant observé : environ `1 min 30`.
- `CasLimite02+` : Normal `22,823 s` sans solution, Long `61,799 s` sans
  solution, Approfondi maximal `90,991 s` avec solution, soit `175,613 s`
  cumulées avant le premier résultat lors de la gate 0.1.78.
- `CasLimite02++` : Approfondi maximal `87,192 s` avec solution.
- Finition observée : environ `2,1 s`.
- Matérialisation observée : environ `0,8 s`.
- Le profil Approfondi maximal autorise actuellement `180 s`.
- Les replays locaux instrumentés montrent une recherche sans complétion,
  jusqu'à `9 019` états et `19 342` essais de pose sur le repli interne.
- La télémétrie de lane est absente des réponses SCIP qui réussissent en
  Approfondi ; cette lacune doit être corrigée avant toute conclusion causale.
- Aucun signe de fuite mémoire ou de rejet tardif dominant n'a été observé.

## Grille et précision

La grille produit est déjà `0,1 mm`.

L'epsilon numérique interne, généralement `0,0001 mm`, n'est pas un pas de
recherche. Il sert aux comparaisons flottantes et aux contrôles topologiques.
Il est interdit de :

- grossir l'epsilon pour gagner du temps ;
- dégrader la grille produit ;
- arrondir seulement l'affichage ;
- introduire une nouvelle valeur physique ;
- présenter la grille comme un gain de performance sans mesure.

## Objectif produit

Réduire autant que raisonnablement possible le temps jusqu'à la première
solution certifiée sur les deux cas autoritaires, en visant le retour vers
l'ordre de grandeur historique de quelques secondes, sans promettre un seuil
non encore démontré.

La mission ne se contente pas d'une baisse marginale si un goulet dominant
reste identifiable et corrigeable dans le scope. Elle s'arrête lorsque :

- le chemin dominant est compris et mesuré ;
- les optimisations simples et robustes dans le scope sont épuisées ;
- poursuivre exigerait une dette, une dépendance, un changement de contrat ou
  une décision humaine structurante ;
- ou le gain résiduel devient faible face au risque de régression.

## Invariants non négociables

Le résultat fonctionnel courant est la référence :

- mêmes enveloppes minimales ;
- même ordre automatique petit-dessous/grand-dessus ;
- mêmes dispositions et géométrie fonctionnelle sur les deux projets, sauf
  divergence explicitement justifiée, documentée et soumise à Thomas ;
- mêmes profondeurs locales `2/4/6 mm` ;
- mêmes cavités, accès et parois minimales ;
- même grille produit `0,1 mm` ;
- même pipeline de conteneurs finalisés puis soustractions plates ;
- volume positif plat `0 mm³` ;
- unions plates `0` ;
- nouveaux corps imprimables plats `0` ;
- aperçu, certificat, CAD IR, plan Fusion et BRep cohérents ;
- BRep transitoire, rollback et projets personnels préservés.

Une optimisation ne peut pas :

- augmenter un plafond de temps ou de candidats pour masquer la lenteur ;
- retourner une solution non certifiée ;
- convertir un timeout en impossibilité ;
- supprimer une lane ou une capacité sans preuve de dominance sûre ;
- modifier silencieusement l'ordre de recherche si cela change le résultat
  fonctionnel retenu ;
- exploiter un cache périmé ou un témoin incompatible ;
- déplacer le coût vers la finalisation ou la matérialisation.

## Projets personnels strictement en lecture seule

- `C:\Users\janko\Documents\BGIG\projects\CasLimite02+.bgig.json`
  - SHA-256 :
    `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC`
- `C:\Users\janko\Documents\BGIG\projects\CasLimite02++.bgig.json`
  - SHA-256 :
    `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743`

SHA avant et après chaque replay. Ne jamais sauvegarder, modifier, normaliser
en place ou versionner ces fichiers. Toute variante temporaire vit dans
`<worktree>/.codex-work` puis est supprimée.

## Parcours obligatoire

Lire d'abord :

1. `AGENTS.md`
2. `docs/PILOTAGE_CURRENT.md`
3. `docs/NEXT_ACTIONS.md`
4. `docs/HUMAN_GATES.md`
5. `docs/P64_L09U_R8_V_0179_HUMAN_POSITIVE_PERFORMANCE_KO_EVIDENCE.md`
6. `docs/P64_L09U_R9_PERFORMANCE_RECOVERY_HANDOFF.md`
7. `docs/P64_L09U_R8_A_SUBTRACTIVE_PIPELINE_DIAGNOSTIC_EVIDENCE.md`
8. `docs/P64_L09U_R8_F_END_TO_END_FIDELITY_EVIDENCE.md`
9. ADR-0103, ADR-0104 et ADR-0105
10. les sources/tests des budgets, du calcul étagé, du solveur minimal, des
    variantes internes, du solveur SCIP, des piles réservées, de la
    certification, de la finalisation et de la télémétrie Fusion.

### R9-A — diagnostic causal, sans correctif prématuré

1. Reconstituer le chemin exact qui passe d'environ `4 s` à `87–91 s`.
2. Séparer préparation, projection sans éléments plats, SCIP, lanes internes,
   certification, finalisation et matérialisation.
3. Corriger d'abord la télémétrie manquante si elle empêche l'attribution du
   succès à une lane ou un solveur.
4. Mesurer candidats bruts/uniques, états, essais, complétions, rejets,
   appels solveur, temps et mémoire.
5. Déterminer si le coût vient principalement de la formulation SCIP, de
   symétries, de candidats redondants, d'un mauvais incumbent, de recherches
   répétées, de certification répétée ou d'une politique d'arrêt tardive.
6. Comparer les options selon simplicité, robustesse, maintenance,
   testabilité, gain probable et risque fonctionnel.

Ne pas relancer un calcul long à l'aveugle. Utiliser le wrapper gardé du skill
`windows-command-resilience`, avec heartbeat et timeout métier.

### R9-B — décision

Créer une ADR avant tout changement algorithmique structurant. Elle doit
privilégier, selon les mesures :

- génération et déduplication plus précoces des candidats ;
- élimination sûre des symétries ;
- propagation plus précoce des contraintes dures ;
- incumbent/warm start compatible et recertifié ;
- arrêt dès qu'une solution certifiée satisfaisant le contrat produit est
  obtenue, si l'optimisation de rang supplémentaire n'a pas d'autorité produit ;
- suppression d'un travail répété démontré.

Ne retenir aucune option uniquement parce qu'elle paraît plus rapide.

### R9-C et suivantes — petits incréments

Pour chaque incrément :

1. écrire un test de non-régression fonctionnelle et de télémétrie ;
2. implémenter le plus petit changement causal ;
3. lancer les tests ciblés avec `PYTHONPATH=src` ;
4. rejouer uniquement les observations autorisées et comparer avant/après ;
5. vérifier digests, solution, géométrie et temps ;
6. documenter honnêtement le gain ou l'absence de gain ;
7. committer puis intégrer dans `main` avant l'incrément suivant.

Le Goal va jusqu'à une nouvelle candidate Fusion installée automatiquement.
Thomas ne reçoit que la recette humaine finale de vérification de performance
et de non-régression géométrique.

## Mesure autorisée

Le scope n'autorise aucun nouveau benchmark, holdout, corpus ou tournoi
solveur. Les seules mesures produit sont les deux projets personnels exacts,
en lecture seule, et les fixtures/tests déterministes déjà versionnés.

Une comparaison avant/après ciblée n'est pas une autorisation d'élargir le
corpus ni de sélectionner un moteur par tournoi.

## Validation et Git

- Utiliser `windows-command-resilience` avant les lots de commandes, tests
  longs et clôtures Git.
- Commandes PowerShell séquentielles, timeouts explicites, aucun lancement
  parallèle.
- Tests ciblés d'abord avec `PYTHONPATH=src`.
- Puis suite autorisée complète, en excluant exactement les douze modules
  interdits déjà documentés avant import.
- `git diff --check`, revue du diff, tests pertinents, commit propre.
- Intégration directe dans `main` et vérification de `origin/main`.
- Ne jamais toucher ou nettoyer un worktree étranger.
- Git/GitHub normal est autorisé de bout en bout sans nouveau GO.

## Critère de clôture

Le Goal n'est terminé que si :

- le goulet causal est démontré ;
- la télémétrie explique chaque succès et chaque arrêt ;
- le gain avant/après est versionné sans extrapolation ;
- aucune régression fonctionnelle ou géométrique n'est observée ;
- les tests ciblés et la suite autorisée sont verts ;
- le code, les preuves et le pilotage sont intégrés dans `origin/main` ;
- la nouvelle candidate Fusion est installée et vérifiée ;
- une recette humaine finale courte est prête.
