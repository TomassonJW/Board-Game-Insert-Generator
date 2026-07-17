# ADR-0068 — Portefeuille multi-solveurs et résultats honnêtes

## Statut

Acceptée le 2026-07-17 par GO explicite de Thomas pour documenter et planifier
la suite du solveur. Cette ADR ne vaut pas implémentation.

## Contexte

P64-H01 a amélioré la recherche dense et la répartition X/Y/Z. P64-H02 a ajouté
une diversification bornée après cul-de-sac. Ces incréments conservent toutefois
la même structure générale : arrangements XY, étages Z et ordres de participants.
Des projets Fusion réels continuent à produire un faux `Calcul impossible`
malgré un volume disponible et des solutions visuellement plausibles.

Un essai P64-H03 local, non commité et non intégré, a confirmé qu'augmenter les
ordres ou les seeds ne suffit pas à couvrir les placements 3D libres. Par
ailleurs, un échec d'heuristique est aujourd'hui présenté comme une impossibilité,
ce qui donne une certitude que le moteur ne possède pas.

Le produit doit préserver la vitesse et la régularité du solveur actuel, tout en
offrant une recherche plus robuste et un contrôle de charge compréhensible.

## Options

1. Continuer à ajouter des ordres et des partitions dans le solveur actuel.
2. Remplacer immédiatement le solveur actuel par un unique moteur 3D complexe.
3. Introduire un portefeuille de stratégies sous contrat commun, avec un
   validateur autoritaire et des statuts de résultat honnêtes.
4. Adopter immédiatement un solveur exact externe pour tous les projets.

## Décision

Retenir l'option 3.

Le solveur actuel devient la stratégie rapide `stage_stack`. Deux stratégies 3D
libres sont introduites progressivement : `free_3d_greedy` fondée sur points
extrêmes et espaces maximaux vides, puis `free_3d_beam` conservant plusieurs
états. `portfolio_auto` orchestre les stratégies autorisées par le profil
d'effort et sélectionne seulement des candidats certifiés par un validateur
commun.

Le produit sépare quatre réglages : méthode de calcul, effort, critère de
classement et finition du volume. `Auto intelligent` reste le parcours par
défaut ; les options avancées sont divulguées progressivement.

Les statuts deviennent au minimum :

- `solution_found` ;
- `no_solution_within_budget` ;
- `proven_impossible` ;
- `invalid_input` ;
- `stale_or_cancelled`.

`proven_impossible` est réservé à une contradiction formelle ou à un moteur
exact ayant couvert le domaine qu'il annonce. Un budget heuristique épuisé ne
peut jamais employer ce statut.

Le moteur exact reste une cinquième famille future, limitée aux petits problèmes
et soumise à une ADR de dépendance et à un GO distincts.

## Conséquences

- le chemin rapide et déterministe existant est conservé ;
- le moteur peut progresser par familles indépendantes et comparables ;
- toute stratégie partage entrées, budgets, métriques, candidats et validation ;
- les résultats deviennent plus honnêtes mais certains anciens textes visibles
  doivent évoluer de façon additive et rétrocompatible ;
- une télémétrie structurée est requise avant le nouveau moteur ;
- les critères `accessible`, `impression simple` ou `matière réduite` ne peuvent
  être affichés comme sémantiques réelles sans métriques dédiées ;
- les variantes internes de conteneur sont compatibles avec le contrat commun,
  mais leur sémantique reste propriétaire de P45 ;
- le cœur reste Python pur et Fusion ne recalcule rien ;
- aucune dépendance externe n'est acceptée par cette ADR.

## Alternatives refusées

- L'option 1 est refusée comme trajectoire principale : elle améliore des cas
  locaux sans lever les limites structurelles des étages.
- L'option 2 est refusée : elle sacrifierait un baseline utile et augmenterait le
  risque de régression et le coût des projets simples.
- L'option 4 est refusée à ce stade : coût, dépendance, packaging Fusion et
  limites combinatoires ne sont pas encore justifiés par un benchmark.
- Une grille 3D uniforme comme moteur principal est refusée : son nombre de
  cellules croît cubiquement et impose trop tôt une topologie arbitraire.

## Suivi

- Contrat programme : `docs/P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md`.
- P64-H04 : statuts, télémétrie et corpus de régression.
- P64-H05 : contrat commun et adaptation `stage_stack`.
- P64-H06 : prototype `free_3d_greedy`.
- P64-H07 : `free_3d_beam` et `portfolio_auto`.
- P64-H08 puis P64-V2 : réglages Fusion et validation humaine.
- P64-X01 : éventuel moteur exact après nouvelle ADR et GO.

## Amendement P64-V2H02 — 2026-07-17

Le volume disponible devient une borne publique, pas un certificat. Une marge
strictement positive prouve seulement que la somme des enveloppes minimales ne
dépasse pas le volume utilisable. Elle ne prouve pas l'existence d'un placement
orthogonal respectant formes, jeux, réservations, supports, axes fixes et ordre
de retrait.

Tout résultat issu du sélecteur produit expose donc `bgig.partition_capacity.v1`, y compris
`no_solution_within_budget`. Un échec du portefeuille affiche un statut non
certifié et ses limites de recherche ; seules les contradictions de bornes
formelles peuvent produire `proven_impossible`.

Les profils de beam explorent désormais 1, 2 et 4 priorités de participants pour
Rapide, Normal et Approfondi, avec des largeurs respectives de 8, 24 et 64. Deux
profils ou deux méthodes peuvent légitimement retourner le même meilleur plan ou
le même statut : la différence porte sur le domaine exploré, pas sur une promesse
de résultat différent.

Le cas dense P64-V2H02 conserve une marge théorique d'environ 693,6 cm³ mais sa
combinaison d'enveloppes canoniques et de réservations explicites a été déclarée
infaisable par une relaxation exacte de diagnostic hors produit. Aucune
dépendance externe ni revendication de moteur exact n'est ajoutée. La suite doit
explorer des variantes internes bornées, sous coordination avec P45, plutôt que
masquer l'échec par une fausse solution.
La famille beam conserve en conséquence deux variantes dans chaque effort :
`legacy_ems_v1` avec une priorité, puis `bridge_ems_v2` avec le plafond 1/2/4 du
profil. Cette composition évite qu'un sur-ensemble d'options change le classement
et évince une ancienne solution validée. Les candidats des deux variantes passent
le même certificat et le même classement public.
