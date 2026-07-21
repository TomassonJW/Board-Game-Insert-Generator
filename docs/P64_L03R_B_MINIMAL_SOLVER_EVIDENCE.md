# P64-L03R-B — Preuve du solveur minimal multi-graines

Date : 2026-07-21
Statut : `implemented-core`, `automated-validated`
Fusion validated : false
Print validated : false

## Résultat

P64-L03R-B livre une API cœur autonome `solve_minimal_layout`. Elle sélectionne
une variante locale certifiée par conteneur, place uniquement ses dimensions
minimales, certifie le plan global et conserve le volume restant comme résiduel
non attribué.

Le chemin n'appelle ni fermeture continue, ni finalisation, ni CAD IR, ni
bridge, ni scène Fusion. Il ne modifie pas les solveurs publics historiques,
leurs budgets, le schéma projet, les tolérances, les valeurs physiques ou les
defaults.

## Contrat livré

L'artefact `bgig.minimal_layout.v1` expose :

- variantes locales et digests de frontière L01/L02 ;
- placements monde complets ;
- dimensions finales égales aux enveloppes minimales sélectionnées ;
- surplus nuls sur `left`, `right`, `front`, `back`, `below` et `above` ;
- résiduel conservé, classifié, non distribué et non imprimable automatiquement ;
- certificat global `bgig.minimal_layout_certificate.v1` ;
- budgets, compteurs, raisons d'arrêt et provenance de lane ;
- formulation `best_certified_proposal_found_within_budget`, sans optimalité
  globale implicite.

La matérialisabilité reste volontairement false dans B : P64-L03R-C possède la
CAD IR minimale, le bridge et l'identité de scène.

## Recherche bornée

Les profils sont des préfixes monotones :

| Profil | Lanes | États max par lane | Essais max par lane | Temps max par lane |
| --- | ---: | ---: | ---: | ---: |
| Rapide | 3 | 256 | 15 000 | 5 000 ms |
| Normal | 6 | 1 500 | 75 000 | 12 000 ms |
| Approfondi | 9 | 5 000 | 250 000 | 30 000 ms |

Les lanes comparent :

- rareté de placement et pressions d'axe normalisées ;
- côté long, empreinte, hauteur, volume et interleaving des extrêmes ;
- graines alternatives ;
- ancres `compact_corner`, `aligned_edge`, `compact_center` et
  `lowest_surface` ;
- propagations `inward_contact`, `long_axis_spine`, `radial_compact` et
  `lowest_supported_surface_first` ;
- variantes internes certifiées avec élargissement progressif ;
- lanes EMS historiques comme comparateurs minimaux isolés.

Le classement final reste une suite d'axes nommés : volume du groupe, vide
interne, hauteur, empreinte, fragmentation, contacts et support. Aucun total
opaque n'est produit. Les candidats non dominés restent dans une frontière
Pareto ; aucune limite moteur au top 3 n'est introduite.

## Validation automatisée

La fixture cœur `tests/test_minimal_layout_solver.py` couvre les scénarios
contractuels 1 à 10 et 16 à 18 :

1. conteneur extensible conservé exactement à son minimum ;
2. aucun surplus X/Y/Z distribué ;
3. deux modules longs et plusieurs graines observables ;
4. rareté normalisée distincte de la hauteur absolue ;
5. ancres symétriques dédupliquées ;
6. réservation localisée rouvrant les points de frontière ;
7. corps haut à côté d'une pile fine supportée ;
8. corps flottant refusé par le certificat commun ;
9. Rapide préfixe de Normal, Normal d'Approfondi ;
10. échec borné non promu en impossibilité ;
16. édition locale sans solve global, puis consommation explicite des
    frontières courantes ;
17. plateau et réservation supérieure toujours contraignants ;
18. mécanisme dense 11 × 34 toujours `no_solution_within_budget`.

Le statut `stale_or_cancelled` est aussi couvert par une annulation ponctuelle
déclenchée dans une lane : il ne peut pas être rétrogradé en absence de solution.

Résultats observés :

- 11/11 tests spécifiques L03R-B ;
- 18/18 tests free-3D historiques ;
- 5/5 tests du contrat solveur ;
- 10/10 tests de sélection globale de variantes ;
- 7/7 tests d'analyse locale contextuelle ;
- 5/5 tests du portefeuille historique ;
- 617/617 tests de la suite complète ;
- Ruff ciblé : OK ;
- compilation ciblée : OK.

Le recentrage XY est essayé avant certification et retombe de manière
déterministe sur les coordonnées de recherche si une contrainte asymétrique
l'interdit. Les relations de support et les réservations sont toujours
revalidées sur les coordonnées finales.

## Limites

- Aucun résultat nouveau n'est revendiqué pour le cas dense 11 × 34.
- Aucune optimalité globale n'est revendiquée.
- Les EMS résiduels affichés sont une classification de diagnostic ; ils ne
  deviennent ni corps, ni cale, ni réserve utile.
- L03R-B n'est ni `fusion-validated` ni `print-validated`.
- Les fixtures 11 à 15, la CAD IR minimale, le registre de scène et le
  remplacement Fusion appartiennent à L03R-C.
- Les vraies transformations de finition restent verrouillées après L03R-V.

## Suite

P64-L03R-C est la seule mission `ready`. Elle doit brancher l'artefact minimal
sur le cycle explicite, produire la CAD IR correspondante, sélectionner
minimal/finalisé et remplacer uniquement la scène BGIG dont les digests ne sont
plus courants. Aucune gate humaine n'est requise avant la clôture automatisée de
C ; P64-L03R-V reste inactive jusque-là.