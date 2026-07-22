# P64-L05A — Preuve d’insertion d’un nouveau conteneur

## Résultat

Statut : implemented-core, implemented-fusion-bridge,
implemented-fusion-ui, automated-validated.

fusion-validated: false. print-validated: false.

P64-L05A ajoute un producteur déterministe qui conserve tous les placements
existants, cherche une pose de contact pour exactement un nouveau conteneur et
recertifie le plan complet sans appeler le portefeuille global.

## Fichiers runtime

- src/board_game_insert_generator/incremental_global_container_reuse.py ;
- src/board_game_insert_generator/staged_calculation.py ;
- fusion_addin/BoardGameInsertGenerator/palette_project.py ;
- fusion_addin/BoardGameInsertGenerator/palette.html.

## Preuves fonctionnelles

### Producteur pur

Les tests démontrent :

- insertion réussie d’un petit conteneur dans un plan certifié ;
- signature monde de tous les voisins strictement conservée ;
- déterminisme du rapport et du digest résultat ;
- caps de variantes, positions et recertifications observables ;
- conteneur surdimensionné refusé sans solve global ;
- modification simultanée d’un ancien contenu refusée fail-closed.

### Orchestration staged

Une synchronisation tente d’abord L04A, puis L05A. Sur succès L05A :

- le plan minimal devient current et certifié ;
- result_source vaut global_void_container_reuse ;
- cache_status vaut global_void_reuse_not_cached ;
- le solveur global simulé comme interdit n’est jamais appelé ;
- finalisation et matérialisation restent explicites.

### Bridge et DOM

Le bridge retourne le plan recertifié pendant validate_project et transporte
new_container_inserted_and_plan_recertified comme raison d’arrêt.

La palette distingue le succès L05A de l’insertion de cavité L04A. Elle annonce
le nouveau conteneur, garde les détails repliés et expose groupe, placement,
producteur, caps, compteurs, raison d’arrêt et digests, sans faux pourcentage.

## Validations ciblées

- producteur et staged L05A : 7/7 ;
- non-régression L04A : 9/9 ;
- bridge palette : 25/25 ;
- DOM palette : 36/36 ;
- py_compile ciblé : OK.

## Validations finales

- suite complète : 660/660 en 137,923 s ;
- Ruff ciblé : OK ;
- py_compile ciblé : OK ;
- compileall cœur et add-in : OK ;
- syntaxe JavaScript extraite de la palette : OK ;
- frontière adsk du cœur pur : OK ;
- git diff --check : OK.

Un premier run complet avait exposé 1 échec sur le scénario chaîné L04A→L05A :
un nettoyage mécanique avait supprimé l’index des frontières enrichies. Le bloc
utile a été rétabli, le test ciblé a repassé 7/7, puis la suite complète finale
a passé 660/660. Aucun échec n’est masqué.

## Limites honnêtes

- fixture synthétique automatisée uniquement ; le projet personnel
  Mon insert.bgig.json n’est ni modifié ni utilisé comme preuve versionnée ;
- aucune observation Fusion du nouveau chemin ;
- un seul nouveau conteneur par édition ;
- faux négatifs encore possibles sous les caps ;
- aucune amélioration de reconstruction depuis zéro dans L05A ;
- aucune modification du solveur, de ses lanes ou de ses budgets ;
- aucune nouvelle revendication sur le cas dense 11 × 34.

La capture versionnée des cas réels et du parcours utilisateur appartient à
P64-L05B. Le plan témoin persistant et le warm start appartiennent à L05C.
