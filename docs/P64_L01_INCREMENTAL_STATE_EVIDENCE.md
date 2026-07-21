# P64-L01 — Preuve d'état dérivé incrémental

Statut : `implemented-core`, `automated-validated` le 2026-07-21.
`fusion-validated: false`, `print-validated: false`.

Contrats : ADR-0056, ADR-0071, ADR-0070, ADR-0073 et
`P64_STAGED_CALCULATION_AND_FINISHING_PROGRAM.md`.

## Portée livrée

`incremental_project_state.py` ajoute une frontière cœur pure, sans `adsk` et
sans branchement dans la palette actuelle :

- snapshots normalisés et digests SHA-256 déterministes ;
- clés complètes versionnées pour résolution asset, frontière conteneur,
  annotation de contexte, agencement global et finalisation ;
- graphe d'invalidation par asset, conteneur, boîte, réservation et réglage
  solveur ;
- états `current` / `stale` qui conservent l'ancien artefact en lecture seule ;
- jetons de requête locale à identité unique et usage unique ;
- cache LRU reconstructible à capacité obligatoire ;
- télémétrie structurée des invalidations, hits, misses et évictions.

Le module ne lance aucun producteur, aucune dérivation, aucun solveur et aucune
matérialisation. Le cycle P44-M007 existant reste inchangé jusqu'à P64-L03/L03V.

## Identités et fail-closed

Les dépendances sont séparées afin d'éviter les invalidations globales
artificielles :

- source physique asset, pose et defaults réellement hérités ;
- paramètres locaux du conteneur, fill elements affectés et defaults hérités ;
- membres ordonnés par identifiant stable ;
- géométrie intrinsèque distincte du contexte boîte/réservations ;
- méthode, version, effort et classement globaux ;
- politique, budget et version de finalisation.

Une clé partielle ou un digest non SHA-256 est refusé. Une version différente
produit un miss. Une liste de résolutions assets incomplète ou comportant un
membre étranger est refusée. Le cache copie les valeurs à l'entrée et à la
sortie : un consommateur ne peut pas muter silencieusement l'artefact conservé.

## Matrice d'invalidation vérifiée

| Mutation | Résolution asset | Frontière intrinsèque | Contexte | Global/final/scène |
| --- | --- | --- | --- | --- |
| dimension, quantité ou pose | asset seul | conteneur propriétaire | propriétaire | stale |
| paramètre ou fill local | inchangée | propriétaire seul | propriétaire | stale |
| déplacement d'asset | réutilisée | ancien + nouveau | ancien + nouveau | stale |
| boîte | réutilisée | réutilisée | tous | stale |
| default asset | héritiers seuls | conteneurs héritiers | concernés | stale |
| default paroi/fond | inchangée | groupes héritiers | concernés | stale |
| override local | inchangée | propriétaire seul | propriétaire | stale |
| méthode/classement | inchangée | réutilisée | réutilisé | stale |

L'ancien digest matérialisé est conservé après invalidation mais son statut
devient `stale` et `can_materialize` devient faux. Aucune scène n'est modifiée.

## Fixtures automatisées

`tests/test_incremental_project_state.py` couvre 16 tests :

1. déterminisme des snapshots, non-mutation source et parité de dérivation ;
2. version producteur et clés complètes fail-closed ;
3. ensemble exact des résolutions membres ;
4. capacité LRU, éviction et immutabilité des valeurs ;
5. édition asset ciblée avec global/final/scène obsolètes ;
6. édition conteneur sans réécriture des résolutions assets ;
7. déplacement d'asset avec exactement deux frontières invalidées ;
8. boîte modifiée avec réutilisation des géométries intrinsèques ;
9. default asset limité aux héritiers ;
10. override local sans voisin invalidé ;
11. fill element local limité à son conteneur ;
12. default conteneur limité aux groupes héritiers ;
13. réponse tardive rejetée après nouvelle révision ;
14. identité de requête non forgeable et usage unique ;
15. réglage solveur invalidant seulement les étapes globales ;
16. corpus de cinquante conteneurs où une édition invalide exactement un asset,
    une frontière et un contexte.

Le corpus 50 conteneurs est une preuve de cardinalité et de déterminisme du
graphe, pas une revendication de performance Fusion ni une validation du cas
dense 11 × 34.

## Validation

- tests ciblés L01 : 16/16 ;
- test de continuité Fusion-only : 6/6 ;
- Ruff ciblé : OK ;
- suite complète : 587/587 ;
- `compileall` : OK ;
- frontière `adsk` du cœur : OK ;
- `git diff --check` : OK.

## Limites

- aucune analyse locale n'est encore planifiée automatiquement ;
- aucun cache n'est persisté dans `bgig.project.v1` ;
- aucune annotation contextuelle, Pareto ou shortlist UI L02 n'est livrée ;
- aucun timer de solve global n'est supprimé avant L03/L03V ;
- aucune valeur physique, forme P45, budget solveur ou résultat dense ne change ;
- aucune preuve Fusion ou impression n'est revendiquée.

## Suite

P64-L02 peut consommer ces clés et états pour produire annotations contextuelles,
sous-scores et représentants progressifs. P64-L02 ne doit ni limiter le moteur
au top 3 visible, ni lancer le solve global après une édition.
