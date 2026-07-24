# P64-L08K — preuve d'intégration produit SCIP

Date : 2026-07-24
Statut automatisé : intégration fonctionnelle et régressions complètes validées
Fusion : `false`
Impression : `false`

## Objet

Intégrer dans le vrai parcours BGIG le gagnant du tournoi P64-L08F, sans faire
passer un contrôle simple pour une preuve de capacité sur les cas limites.

L'intégration utilise SCIP 10.0.2, SoPlex 8.0.2, PySCIPOpt 6.2.1 et NumPy 2.5.1
pour CPython `cp314`. Le modèle reste le worker MIP 3D scellé et qualifié par
L08J. BGIG reste l'autorité de certificat.

## Décision produit

ADR-0085 décide :

- SCIP est prioritaire pour un problème fidèlement représentable ;
- une solution SCIP recertifiée arrête la recherche ;
- un timeout SCIP ne déclenche pas silencieusement une seconde recherche
  interne ;
- un runtime absent ou invalide, une contrainte non représentable, une erreur
  native ou un certificat rejeté utilisent un fallback interne explicite ;
- une réservation supérieure localisée n'est jamais approximée ;
- l'affectation des éléments aux conteneurs reste résolue en amont par BGIG ;
  SCIP place les enveloppes et variantes locales certifiées ;
- aucune finalisation, génération CAD, scène Fusion ou valeur physique n'est
  modifiée par cette lane.

Budgets : Rapide 1 s, Normal 5 s, Approfondi 30 s ; 1 024 Mio, un thread, seed
6408.

## Paquet exact

- version add-in : `0.1.61` ;
- archive : `scip-runtime-cp314.zip` ;
- taille : 18 319 793 octets ;
- SHA-256 :
  `0a718ea5884d6326d66777db0ab853a31fa981e6392b89f184342fde27d465c6` ;
- digest artefact :
  `540e2fe6b9324f2d58afbdaab827760f98b6b0e4ab9f626efdaee69d2c6d2786` ;
- arbre extrait : 1 016 fichiers, 56 491 565 octets ;
- binaires : 26, tous résolus en L08J ;
- workers scellés : deux fichiers, empreintes vérifiées ;
- avis : PySCIPOpt, SCIP, SoPlex, NumPy et Microsoft inclus ;
- aucun réseau, service, compte, secret, télémétrie ou installation globale.

L'installateur vérifie le SHA-256 et la taille de l'archive, puis le nombre et la
taille totale des fichiers extraits. Avant le premier chargement natif,
l'adaptateur recalcule l'inventaire complet et son digest canonique.

## Traduction géométrique

- unité entière : 0,001 mm ;
- retrait du jeu de boîte de la zone utile ;
- jeux entre corps X/Y/Z transportés par gonflement positif des enveloppes ;
- tailles physiques d'origine restaurées dans le plan publié ;
- rotations X/Y et variantes locales transportées explicitement ;
- variantes incompatibles avec une dimension fixe filtrées, sans rejeter les
  variantes valides ;
- appuis recalculés par BGIG ;
- espaces vides reconstruits par BGIG ;
- certificat global BGIG obligatoire avant publication.

## Contrôle positif réellement 3D

La preuve
`tests/fixtures/p64_l08k_scip_product_integration.v1.json` exécute deux fois le
point d'entrée public `solve_minimal_layout` sur un cas dont les trois conteneurs
ne peuvent pas tenir côte à côte.

Résultat :

- `solution_found` ;
- source `external_scip_real_3d` ;
- trois niveaux Z : 0,0 / 16,4 / 32,8 mm ;
- deux placements appuyés ;
- une invocation SCIP par calcul ;
- zéro lane interne ;
- recertification BGIG : oui ;
- résultats déterministes sur deux runs ;
- digest de preuve :
  `4ef82b167dab28892bee663eb0c9a2264a9d174504a9ca9908713574b808829e`.

Ce contrôle prouve l'intégration, l'empilement en Z et la recertification. Il ne
prouve pas la capacité limite.

## Régression publique réelle 18 conteneurs / 20 éléments

La preuve
`tests/fixtures/p64_l08k_scip_product_limit_regression.v1.json` passe le cas
public revu `real-18-containers-20-contents-normal` par le même point d'entrée
produit.

Résultat observé :

| Effort | SCIP | Moteur | Invocation | Lanes internes | Résultat BGIG |
| --- | --- | --- | ---: | ---: | --- |
| Normal, 5 s | `bounded_unknown` | `timelimit` | 1 | 0 | `no_solution_within_budget` |
| Approfondi, 30 s | `bounded_unknown` | `timelimit` | 1 | 0 | `no_solution_within_budget` |

Digest :
`5a3f3550d8131dcdb088362fa06d2e7a70ee535e2d6d3ba235409ed78409a0de`.

Conclusion honnête : ce cas n'est plus rejeté par l'adaptateur, mais L08K ne
démontre aucun gain de solution sur lui. `bounded_unknown` ne veut pas dire
impossible. La gate réelle sur le projet limite de Thomas reste obligatoire.

## Package Fusion

Le staging local de l'installateur `0.1.61` a vérifié :

- copie du moteur Python pur ;
- archive SCIP exacte ;
- extraction locale du runtime ;
- fichiers PySCIPOpt, SCIP, NumPy et avis présents ;
- marqueurs produit présents ;
- aucune compilation pendant l'installation.

La checklist humaine est
`docs/P64_L08K_FUSION_GATE_CHECKLIST.md`. Le préparateur
`scripts/fusion/prepare_p64_l08k_scip_product_gate.ps1` préserve l'état local,
installe le cas public 18x20, sélectionne `Auto intelligent + Approfondi`,
installe l'add-in et écrit le marqueur du commit.

## Validations automatisées

- tests SCIP ciblés : 10/10 OK ;
- tests minimal-layout : 14/14 OK ;
- tests palette Qt : 9/9 OK ;
- compatibilité du runtime HiGHS historique : 5/5 OK ;
- préflight Fusion : 2/2 OK ;
- vraie intégration CPython 3.14 : OK ;
- staging installateur 0.1.61 : OK ;
- garde documentaire : 2/2 OK ;
- alignement Fusion-only : 6/6 OK ;
- suite complète finale : 828/828 OK en 252,471 s ;
- Ruff ciblé et format des nouveaux fichiers : OK ;
- `py_compile`, parse PowerShell et diff-check : OK.

Le premier passage complet a détecté un nom historique attendu par le paquet
HiGHS. Cette compatibilité a été restaurée avant le passage final vert.
## Limites maintenues

- pas de replay du holdout ;
- pas de tuning post-holdout ;
- top inset localisé : fallback interne ;
- appui SCIP complet plus strict que le minimum BGIG ;
- aucun statut `infeasible` SCIP n'est promu en impossibilité BGIG ;
- `fusion-validated=false` jusqu'au retour humain ;
- `print-validated=false` sans impression et mesure dédiées.