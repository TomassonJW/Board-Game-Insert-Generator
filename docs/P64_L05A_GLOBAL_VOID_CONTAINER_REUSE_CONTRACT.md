# P64-L05A — Contrat de réutilisation du vide global

## Statut

Contrat implémenté et validé automatiquement le 2026-07-22.
ADR normative : ADR-0076.

fusion-validated: false. print-validated: false.

## But

Après l’ajout d’exactement un nouveau conteneur, tenter de l’insérer dans le
volume global encore disponible sans déplacer aucun corps existant. Une
réussite republie un plan minimal complet et recertifié. Un échec laisse le solve
global comme action explicite.

## Entrées autorisées

- plan minimal source courant, intègre et certifié ;
- mêmes boîte, hauteur utile, réservations, politique de dégagement et réglages ;
- mêmes compléments ;
- mêmes groupes et contenus existants ;
- exactement un nouveau groupe ;
- au moins un nouveau contenu, tous exclusivement affectés au nouveau groupe ;
- frontières locales courantes, complètes et certifiées pour l’effort actif.

Toute autre mutation est hors contrat et produit not_attempted ou
global_solve_required.

## Producteur pur

Identité :

- schéma : bgig.incremental_global_void_container_reuse.v1 ;
- famille : incremental_global_void_container_reuse ;
- version : p64-l05a-v1 ;
- producteur : fixed_world_contact_insertion_v1, version 1.

Pipeline :

1. vérifier l’intégrité du plan source et l’éligibilité du delta ;
2. reconstruire les placements existants depuis le plan certifié ;
3. sélectionner au plus 12 variantes P45 certifiées du nouveau conteneur,
   classées par volume minimal puis hauteur, emprise et digest ;
4. énumérer les rotations 0/90 utiles ;
5. dériver des coordonnées de contact depuis la boîte et les faces des
   placements réels, avec leurs dégagements effectifs ;
6. préfiltrer chaque candidat avec le validateur géométrique commun ;
7. reconstruire les espaces vides du plan complet ;
8. rejouer le certificat minimal P64 ;
9. vérifier que la signature géométrique de chaque ancien placement est
   strictement identique.

Les zones résiduelles d’affichage ne sont jamais utilisées comme preuve.

## Budgets

- max_new_container_groups : 1 ;
- max_variant_options : 12 ;
- max_position_trials : 16 384 ;
- max_global_recertifications : 64.

Les compteurs correspondants sont présents dans chaque rapport. Une limite
atteinte produit un fallback explicite, jamais une preuve d’impossibilité.

## Succès

Statut : container_placed_in_global_void.

Invariants :

- existing_placements_reused est vrai ;
- existing_world_placements_changed est faux ;
- new_world_placement_added est vrai ;
- global_solver_invocation_count vaut 0 ;
- finalization_invocation_count vaut 0 ;
- fusion_materialization_invocation_count vaut 0 ;
- le plan et le projet résultat possèdent de nouveaux digests ;
- la provenance expose groupe, placement, variante, origine, rotation, budgets,
  compteurs et raison d’arrêt.

Le lifecycle staged rend le nouveau plan minimal courant. Une finalisation
antérieure devient stale. Une CAD IR ou scène antérieure devient
desynchronized. Aucune scène n’est modifiée automatiquement.

## Échec

Statut : global_solve_required pour un delta admissible qui ne trouve aucun
candidat certifié, ou not_attempted si une dépendance globale change avant la
tentative.

Le plan source n’est jamais conservé comme courant sous le nouveau projet. La
palette demande explicitement le calcul de l’agencement minimal.

## UX et bridge

Sur succès, la palette annonce :

« Nouveau conteneur intégré dans le volume global disponible. Tous les
placements existants sont conservés. »

Les détails restent repliés par défaut et exposent identité, producteur,
variantes, positions, recertifications, caps, raison d’arrêt et digests. Aucun
pourcentage, ETA ou bouton Annuler décoratif n’est ajouté.

## Interdits

- aucun appel automatique du portefeuille global ;
- aucun déplacement d’un voisin ;
- aucun solve depuis zéro revendiqué ;
- aucune confiance aveugle dans le volume ou les zones résiduelles ;
- aucune modification du solveur, de ses lanes ou budgets ;
- aucune finalisation, CAD, scène ou sauvegarde de projet déclenchée par le
  producteur ;
- aucune auto-modification de l’algorithme ;
- aucune revendication sur le cas dense 11 × 34.

## Validation minimale

- tests purs : succès, déterminisme, dépassement et mutation concurrente ;
- test staged sans invocation du solveur global ;
- test bridge avec raison d’arrêt et géométrie des voisins conservée ;
- test DOM du message et des détails observables ;
- non-régression L04A ;
- suite complète, Ruff ciblé, py_compile, syntaxe JavaScript, frontière adsk et
  git diff --check.
