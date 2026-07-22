# ADR-0076 — Insertion pré-finalisation d’un nouveau conteneur dans le vide global

## Statut

Acceptée le 2026-07-22 après le retour humain globalement KO de P64-L04V et le
GO explicite du programme correctif P64-L05. Cette décision ouvre P64-L05A.
Elle ne vaut ni validation Fusion ni validation d’impression.

## Contexte

P64-L04A sait modifier l’intérieur d’un conteneur en conservant son enveloppe et
son placement monde. ADR-0075 imposait toutefois un solve global dès qu’un
nouveau conteneur apparaissait. Le retour humain L04V montre une dissymétrie
produit : BGIG exploite le volume libre interne d’un conteneur, mais invalide le
plan lorsqu’un nouveau petit conteneur pourrait tenir dans le volume global
restant sans déplacer ses voisins.

Les volumes résiduels affichés ne constituent pas une preuve géométrique : les
zones maximales peuvent se chevaucher. Le nouveau chemin doit donc travailler
sur les placements certifiés réels, puis rejouer le certificat global commun.

## Options

### A — Toujours relancer le portefeuille global

Simple, mais perd un plan monde déjà certifié et peut ne pas retrouver un
agencement pourtant extensible.

### B — Placer le nouveau conteneur dans une zone résiduelle affichée

Rapide, mais non sûr : les zones affichées peuvent se chevaucher et ne prouvent
ni dégagement, ni appui, ni compatibilité avec les réservations supérieures.

### C — Recherche d’insertion bornée à monde fixe puis recertification complète

Les placements existants restent identiques. Un producteur déterministe teste
des variantes locales certifiées et des positions de contact déduites des corps
réels. Chaque candidat admissible est soumis au certificat minimal commun.

## Décision

Retenir l’option C pour P64-L05A.

La tentative est autorisée seulement si :

1. le plan source minimal est courant, intègre et certifié ;
2. la boîte, les réservations, les réglages géométriques globaux, les
   compléments et tous les anciens contenus restent inchangés ;
3. exactement un nouveau groupe de conteneur est ajouté ;
4. tous les nouveaux contenus appartiennent exclusivement à ce groupe ;
5. les frontières locales P45 courantes sont complètes et certifiées ;
6. le certificat P64 accepte le plan complet après insertion.

Le producteur considère au plus 12 variantes, 16 384 positions de contact et
64 recertifications globales. Ces caps sont observables. Il n’appelle ni le
portefeuille global, ni le finaliseur, ni la CAD, ni Fusion.

Une réussite publie :

- status: container_placed_in_global_void ;
- existing_placements_reused: true ;
- existing_world_placements_changed: false ;
- new_world_placement_added: true ;
- global_solver_invocation_count: 0 ;
- un nouveau digest de plan et une provenance versionnée.

Un échec ne prouve jamais l’impossibilité. L’ancien plan devient obsolète et
l’action explicite « Calculer l’agencement minimal » reste le fallback.

## Frontière P45 / P64

P45 possède les variantes internes, dimensions minimales et certificats locaux
du nouveau conteneur. P64 possède l’énumération de sa pose monde, la conservation
des voisins et le certificat du plan complet. Aucune sémantique de forme locale,
tolérance ou valeur physique n’est déplacée.

## Conséquences

### Positives

- un nouveau conteneur peut exploiter un vide global certifiable sans casser un
  arrangement existant ;
- les zones résiduelles restent informatives et ne deviennent pas une autorité ;
- le chemin est déterministe, borné, observable et fail-closed ;
- aucune mutation automatique de scène n’est introduite.

### Limites

- la première version accepte un seul nouveau conteneur par édition ;
- l’énumération de contacts peut produire des faux négatifs ;
- elle n’améliore pas encore le solveur depuis zéro ;
- le plan témoin persistant, les captures DEV et l’optimisation sur corpus
  appartiennent respectivement à L05C, L05B et L05D.

## Alternatives refusées

- apprendre ou modifier automatiquement l’algorithme depuis Fusion ;
- traiter le volume résiduel affiché comme une baie garantie ;
- déplacer silencieusement un voisin ;
- relancer automatiquement le solveur global après échec ;
- matérialiser ou finaliser automatiquement le plan recertifié.

## Validation

Le contrat exécutable est
docs/P64_L05A_GLOBAL_VOID_CONTAINER_REUSE_CONTRACT.md.
La preuve automatisée est
docs/P64_L05A_GLOBAL_VOID_CONTAINER_REUSE_EVIDENCE.md.

fusion-validated: false, print-validated: false.
