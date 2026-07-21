# P64-L02 — Preuve d’analyse locale contextuelle

Statut : `implemented-core`, `implemented-fusion-bridge`,
`implemented-fusion-ui`, `automated-validated` le 2026-07-21.
`fusion-validated: false`, `print-validated: false`.

Contrats : ADR-0056, ADR-0068, ADR-0069, ADR-0070, ADR-0071, ADR-0073,
`P64_STAGED_CALCULATION_AND_FINISHING_PROGRAM.md` et
`P64_L01_INCREMENTAL_STATE_EVIDENCE.md`.

## Portée livrée

`contextual_local_analysis.py` consomme les snapshots, clés complètes, jetons
de requête, cache LRU et statuts d’invalidation P64-L01. Il enrichit les
frontières certifiées H03B sans modifier leur digest géométrique ni leur
consommation par le solveur global.

Le lot expose dans le cœur et le bridge Fusion :

- une annotation de boîte et de réservation parmi `compatible`,
  `conditional`, `incompatible` ou `unknown` ;
- les orientations X/Y qui satisfont les seules bornes d’axes connues ;
- une compatibilité localisée sous plateau qui reste conditionnelle lorsque la
  position, la rotation ou une coupe doit être tranchée globalement ;
- une frontière Pareto contextuelle déterministe ;
- les représentants UX `Compact`, `Équilibré` et `Bas`, dédupliqués
  lorsqu’une même géométrie porte plusieurs qualités ;
- des bornes globales nécessaires de volume, hauteur, axe et absence de
  frontière, sans placement.

## Sous-scores explicables

Chaque variante conserve séparément :

- efficacité d’enveloppe avec numérateur cavités et dénominateur extérieur ;
- volume extérieur en mm³ ;
- empreinte en mm² ;
- pénalité logarithmique d’aspect ;
- hauteur en mm ;
- complexité avec rangées, cloisons et changements de coupe ;
- compatibilité boîte et réservations, hors total numérique.

`opaque_total` vaut explicitement `null`. Aucun score total ne certifie le
placement, l’ergonomie, la matière ou l’imprimabilité.

## Frontière et résumé progressif

La frontière moteur reste le tableau complet `engine_frontier_variant_digests`.
La Pareto contextuelle et les cartes visibles sont des projections. La palette
peint au plus trois représentants dans `Possibilités d’agencement`, replié par
défaut, puis réserve aux `Options expertes` :

- toutes les variantes retenues ;
- les sous-scores et compatibilités ;
- producteurs, digests et budgets ;
- caps générés/certifiés/retenus ;
- état recalculé ou réutilisé.

Une fixture de quatre cavités conserve huit variantes moteur pour deux cartes
représentatives visibles portant les trois qualités. La shortlist ne limite donc
ni la frontière interne, ni le progressive widening H03C.

## Incrémentalité et absence de solve global

Le bridge garde au plus huit moteurs locaux en mémoire, séparés par document et
profil d’effort. Leur cache reste borné, reconstructible et non persisté dans
`bgig.project.v1`.

Les tests prouvent :

1. modifier un asset recalcule exactement sa frontière et son contexte ;
2. le digest du conteneur voisin reste identique et son analyse est réutilisée ;
3. modifier la boîte réutilise la frontière intrinsèque et renouvelle seulement
   le contexte ;
4. une requête identique ne recalcule aucun conteneur ;
5. `validate_project` n’appelle jamais `solve_partition_plan` ;
6. les bornes réactives portent `placement_performed: false` et
   `proves_global_solution: false` ;
7. `global_solver_invocation_count` reste zéro.

Le timer global historique P44-M007 n’est pas retiré par L02. Cette mutation de
cycle appartient toujours à P64-L03/L03V.

## Validation

- tests cœur, bridge et DOM ciblés : 58/58 ;
- syntaxe JavaScript extraite de la palette : OK ;
- Ruff ciblé : OK avec l’exception E402 historique du module de test bridge ;
- suite complète : 597/597 ;
- `compileall -q src fusion_addin/BoardGameInsertGenerator` : OK ;
- frontière `adsk` du cœur : OK, aucun import ;
- `git diff --check` : OK.

## Limites

- aucune forme, intention ou migration runtime P45 ;
- aucun changement de baseline, EMS, greedy, beam, effort ou classement global ;
- aucune suppression du solve automatique avant L03 ;
- aucune finalisation, cale, remplissage ou harmonisation F01/F02 ;
- aucune scène Fusion créée ou modifiée ;
- aucun résultat nouveau revendiqué pour le cas dense 11 × 34 ;
- aucune preuve Fusion ou impression.

## Suite

P64-L03 peut désormais rendre le solve global explicitement déclenché,
conserver l’ancien résultat comme obsolète, appliquer le progressive widening
sur la frontière complète et séparer placement, finalisation et
matérialisation. P64-L03V restera la gate humaine distincte.
