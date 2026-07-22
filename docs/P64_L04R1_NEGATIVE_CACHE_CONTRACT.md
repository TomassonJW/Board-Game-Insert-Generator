# P64-L04R1 — Cache négatif et temps de calcul honnêtes

Date : 2026-07-22
Statut : implemented-core, implemented-fusion-bridge, implemented-fusion-ui, automated-validated

## Problème observé

La gate humaine P64-L04V a révélé deux faits distincts sur le projet réel
« Mon insert » :

- un résultat négatif no_solution_within_budget pouvait satisfaire une nouvelle
  action explicite par cache hit, sans relancer la recherche ;
- la palette affichait alors 0 s, temps de restitution du cache, comme si une
  nouvelle recherche avait été exécutée.

Le diagnostic hors Fusion a reproduit un premier échec Approfondi en environ
8 secondes puis le même échec en 4 ms par cache hit.

## Décision

Le cache global staged ne conserve désormais que des plans minimaux complets et
certifiés. Un résultat négatif reste observable pour la requête courante, mais il
n'est jamais écrit dans le cache et ne peut donc pas satisfaire une nouvelle
action explicite.

Chaque résultat staged expose un objet additif
bgig.calculation_timing.v1 :

- result_source : fresh_search, certified_cache ou local_reuse ;
- search_elapsed_ms : durée du calcul frais ayant produit le résultat ;
- request_elapsed_ms : durée de la requête staged courante ;
- retrieval_elapsed_ms : durée de restitution, seulement pour un cache hit.

Le bridge copie cette provenance dans l'activité terminale. La palette distingue
« Recherche » de « Cache », puis détaille « Recherche initiale » et
« Restitution cache ». Un cache hit ne peut provenir que d'un plan certifié.

## Invariants

- chaque nouvelle action explicite après un échec relance réellement le solveur ;
- un plan certifié identique reste réutilisable sans recalcul ;
- les budgets, lanes, classements, deadlines et certificats du solveur sont inchangés ;
- aucune finalisation, CAD IR ou scène Fusion automatique n'est déclenchée ;
- aucun pourcentage, ETA ou bouton Annuler n'est ajouté ;
- le schéma projet et le manifest Fusion restent inchangés ;
- fusion-validated: false, print-validated: false.

## Acceptation automatisée

- deux échecs identiques invoquent deux fois le solveur et laissent le cache vide ;
- un succès certifié est calculé une fois puis restitué par cache hit ;
- les temps du calcul initial et de la restitution restent distincts ;
- le bridge et le DOM exposent les libellés honnêtes ;
- suite complète : 651/651 tests OK en 143,528 s.
