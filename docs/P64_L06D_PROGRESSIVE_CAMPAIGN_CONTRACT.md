# P64-L06D — contrat de campagne progressive autonome

## Objet

P64-L06D exécute le corpus P64-L06B avec les deux comparateurs P64-L06C, classe les lacunes du solveur courant et sélectionne au plus une hypothèse avant l'ouverture du holdout.

La mission ne change ni le solveur produit, ni ses budgets publics, ni ses certificats, ni la géométrie, ni Fusion. Elle peut conclure qu'aucune amélioration ne mérite d'être intégrée.

## Périmètre

La campagne reste limitée aux formes T0/T1 et aux projets du manifest `bgig.solver_benchmark_manifest.v1`. Elle utilise uniquement :

- `current_bgig_minimal_layout` ;
- `internal_exact_floor` pour les petits cas dans sa portée déclarée ;
- un seul worker fonctionnel ;
- les dépendances déjà présentes dans le dépôt.

Les formes T2 à T4, les changements de schéma, de budget, de délai, de certificat, de tolérance, de valeur physique, de finalisation, de CAD, de scène ou de manifest restent interdits.

## Exécution atomique et reprise

Chaque couple cas/comparateur produit un fichier JSON indépendant, puis un checkpoint est remplacé atomiquement. Le checkpoint porte l'identité du run, le SHA de base, la branche, le digest du manifest, le planning, les résultats terminés, le budget consommé, la prochaine action et la raison d'arrêt.

À la reprise :

1. un résultat dont le schéma et le digest sont valides est sauté ;
2. un résultat absent ou corrompu est recalculé une seule fois ;
3. un checkpoint modifié sans mise à jour cohérente de son digest est refusé ;
4. un planning supérieur au plafond explicite est refusé avant calcul.

## Tournoi

L'ordre est fixe :

1. huit régressions historiques ;
2. baseline discovery avec le solveur courant et l'oracle interne ;
3. contrôles diagnostiques discovery, sans les confondre avec des candidats ;
4. au plus trois hypothèses de lanes au même budget ;
5. comparaison sur tuning ;
6. sélection unique et scellée ;
7. ouverture du holdout ;
8. soak seulement si un gain fonctionnel justifie son coût.

Le holdout refuse toute ouverture sans `bgig.solver_benchmark_holdout_selection.v1` valide. La sélection porte un seul identifiant, un digest de candidat et son propre digest d'intégrité.

## Contrôles diagnostiques

Trois transformations monotones peuvent être appliquées uniquement au split discovery :

- autoriser la rotation lorsque le cas demandait son interdiction ;
- retirer les réservations supérieures ;
- appliquer les deux relaxations.

Elles servent à séparer une limite de contrôle d'entrée d'une limite de recherche. Elles ne sont jamais candidates à une intégration produit et ne changent pas la vérité d'un témoin faisable déjà construit.

## Hypothèses de lanes

Trois hypothèses remplacent uniquement les trois lanes du profil Rapide pendant le benchmark :

- `lane_center_quick_v1` ;
- `lane_lowest_quick_v1` ;
- `lane_interleave_quick_v1`.

Les plafonds Rapide, le nombre de lanes, les profils Normal et Approfondi et le certificat commun restent inchangés. Ce branchement reste privé au runner de benchmark : le solveur produit n'est pas modifié.

## Sorties versionnées

Le rapport `bgig.solver_benchmark_campaign_report.v1` conserve :

- les digests de tous les résumés et checkpoints ;
- les comptes par comparaison ;
- les contrôles et hypothèses ;
- le candidat scellé avant holdout ;
- le coût en exécutions cas/comparateur ;
- la décision d'intégration ou de refus ;
- les invariants de frontière.

Le rapport complet est versionné dans `tests/fixtures/p64_l06d_campaign_report.v1.json` et son digest est vérifié par test.

## Gate de décision

Une hypothèse algorithmique est retenue seulement si elle apporte un gain fonctionnel reproductible sans perdre une solution connue, sans contradiction d'oracle, sans certificat rejeté et sans modification des budgets publics.

Si les trois hypothèses restent identiques à la baseline sur discovery et tuning, la sélection autorisée est `no_algorithm_change_v1`. Le holdout mesure alors l'absence de régression et confirme ou infirme la décision négative ; il ne transforme pas l'absence de gain en amélioration.

Statut : `implemented-core`, `automated-validated`.

`fusion-validated: false`. `print-validated: false`.
