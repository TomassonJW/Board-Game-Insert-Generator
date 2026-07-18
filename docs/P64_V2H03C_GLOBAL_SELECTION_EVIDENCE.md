# P64-V2H03C — Preuve de sélection globale paresseuse

Date : 2026-07-18
Statut : `implemented-core`, `automated-validated`
Fusion validated : `false`
Print validated : `false`

## Résultat

H03C consomme les frontières locales certifiées de H03B dans le beam free-3D.
Le portefeuille canonique complet reste exécuté en premier. Le fallback variantes
ne s'ouvre qu'en l'absence de candidat canonique communément certifié.

Chaque état beam porte directement la variante du conteneur placé. Aucun produit
cartésien préalable des affectations n'est construit. La fermeture continue
préserve cette identité, reconstruit les cavités de la variante retenue, puis le
validateur produit commun certifie le plan complet. Un certificat global H03C
vérifie en plus l'unicité, la complétude et la liaison aux certificats locaux.

## Budgets consommés

Les caps H03B deviennent exécutoires sans modifier les budgets H07 historiques :

| Effort | Variantes/expansion | États variante | Essais variante-placement |
| --- | ---: | ---: | ---: |
| Rapide | 2 | 32 | 128 |
| Normal | 4 | 384 | 3 072 |
| Approfondi | 6 | 3 072 | 36 864 |

Normal rejoue le préfixe Rapide ; Approfondi rejoue Rapide puis Normal. Les
digests des lanes préservées restent identiques. Atteindre un cap produit
`no_solution_within_budget`, jamais une preuve d'impossibilité.

## Fixtures et mesures locales

Mesures indicatives sur ce checkout ; les caps ci-dessus, pas le temps mural,
constituent le contrat.

| Fixture | Effort | Résultat | États / essais | Observation |
| --- | --- | --- | ---: | --- |
| Cul-de-sac multi-cavités, deux conteneurs | Rapide | `solution_found` | 5 / 16 | Deux relayouts non canoniques certifiés donnent le plan global. |
| Réservation localisée | Normal | `solution_found` | Quick 3 / 16, Normal 5 / 32 | Quick est rejeté après fermeture ; Normal retient une autre cavité locale compatible. |
| Cas sous-dimensionné mais valide | Rapide | `no_solution_within_budget` | 2 / 24 | Aucune fausse impossibilité. |
| Mécanisme dense anonymisé 11 × 34 | Rapide | `no_solution_within_budget` | 7 / 128 | Arrêt borné et honnête. |
| Même mécanisme dense | Normal | `no_solution_within_budget` | Normal 295 / 3 072 | Le préfixe Rapide reste identique. |
| Même mécanisme dense | Approfondi | `no_solution_within_budget` | Deep 3 072 / 9 264 | Cap d'états atteint ; aucune solubilité n'est revendiquée. |

Temps observés : 18,104 ms pour le cul-de-sac direct, 17,660 ms pour la
réservation localisée, 43,153 ms / 193,325 ms / 1 035,119 ms pour le mécanisme
dense en Rapide / Normal / Approfondi. Le portefeuille complet résout le
cul-de-sac en 21,124 ms après trois familles canoniques sans candidat certifié.

## Traçabilité publique

Le plan public reste sur `bgig.project.v1` et les méthodes H08 existantes. Quand
le fallback est exécuté, le diagnostic secondaire expose :

- lanes, budgets variante et beam, compteurs et limites atteintes ;
- frontières par conteneur, rejets locaux, déduplication, dominance et digests ;
- variantes du plan retenu et certificats local/global ;
- `canonical_portfolio_completed_first: true` ;
- `cartesian_product_materialized: false` ;
- arrêt par solution, budget, annulation ou entrée invalide.

Les succès canoniques ne portent aucune trace H03C supplémentaire et conservent
leur fast path. Aucun contrôle expert n'est ajouté à la palette.

## Vérifications

- 10 tests H03C : fixtures 4 à 10, monotonie, déterminisme, annulation, fallback,
  projection publique et certificat global ;
- 23 tests variantes ciblés : OK ;
- 7 tests portefeuille historiques : OK ;
- 18 tests free-3D ciblés : OK ;
- suite complète : 566/566 OK en 150,895 s ;
- Ruff sur les sources et tests H03C : OK.

Les contrôles de clôture `compileall`, exemple CLI, frontière `adsk` et diff-check
sont exécutés avant intégration et consignés dans le rapport de mission.

## Limites

H03C prouve que des enveloppes locales alternatives peuvent débloquer un vrai
cul-de-sac multi-cavités. Il ne prouve pas que le cas dense 11 × 34 est soluble :
même Approfondi s'arrête honnêtement sans certificat. Il n'ajoute ni forme P45,
ni solveur exact, ni valeur physique, ni tolérance, ni default, ni corps ou scène
automatique.

Une marge volumique positive reste une condition nécessaire seulement. Toute
revendication Fusion exige P64-V2H03V ; toute revendication d'impression exige
une impression réelle distincte.
