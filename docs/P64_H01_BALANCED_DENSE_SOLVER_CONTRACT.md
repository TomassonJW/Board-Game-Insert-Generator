# P64-H01 - Recherche dense et répartition 3D équilibrée

## Statut

Implemented et automated-validated dans le package 0.1.42.
Gate Fusion P64-H01V requise.
`fusion-validated: false`, `print-validated: false`.

## Déclencheur

Le projet réel d'environ 30 conteneurs et 77 éléments redevient calculable après
P44-VH01, mais l'ajout d'un petit asset peut encore produire
`NO_STAGE_COMPOSITION_FITS` alors que les enveloppes minimales n'occupent
qu'environ 40 % du volume disponible. Le mode `balanced` attend par ailleurs
la saturation XY avant d'utiliser Z.

## Objectif

- trouver des compositions d'étages de tailles variables dans les projets
  denses ;
- faire de l'équilibre X/Y/Z un critère de référence du mode `balanced` ;
- construire les étages progressivement avec la densité quand ils améliorent
  réellement la répartition ;
- préserver le comportement simple du mode `compact`.

## Contrat

La recherche ajoute au plus huit nombres d'étages adaptatifs par ordre
déterministe. Une partition LPT distribue les enveloppes selon leur empreinte
minimale cumulée. Une borne optimiste de hauteur rejette les nombres d'étages
impossibles avant tout calcul XY. Les partitions adaptatives sont évaluées
avant les groupes contigus historiques, dans le budget global existant.

Pour le mode `balanced` :

- chaque arrangement XY équilibré est comparé à la hauteur de son étage ;
- le score spatial rapproche les facteurs d'expansion moyens X, Y et Z ;
- les sommes d'empreintes minimales des étages sont aussi équilibrées ;
- la famille de recherche ne prime plus sur la qualité d'un candidat complet ;
- une composition hybride par intervalles reçoit un léger coût de simplicité.

Le mode `compact` conserve son classement historique orienté vers les
compositions simples.

## Invariants

- aucune dimension fixe, cible ou minimale n'est recalibrée ;
- aucun défaut, tolérance, jeu, règle de cavité ou réservation ne change ;
- aucun schéma projet ne change ;
- le cœur reste pur Python et sans import `adsk` ;
- la recherche reste bornée, déterministe et non globalement optimale ;
- aucune scène ou matérialisation automatique n'est ajoutée ;
- aucun résultat partiel n'est présenté comme solution complète.

## Acceptation automatisée

- 2, 8 puis 32 conteneurs homogènes dans une boîte de référence donnent
  respectivement 1, 2 puis 3 étages en mode `balanced` ;
- 8 conteneurs dans le même cas restent sur un étage en mode `compact` ;
- une fixture anonymisée de 30 empreintes variables trouve deux étages complets
  dans 400 × 300 × 183 mm ;
- le projet réel augmenté du petit asset problématique trouve une solution
  complète en environ 1,8 seconde sur la machine de validation ;
- support, retraits, conservation, budgets et déterminisme restent testés.

## Gate Fusion P64-H01V

Préparation :

`scripts/fusion/prepare_p64_h01_balanced_dense_solver_test.ps1`

Vérifier le projet dense réel, l'ajout du petit asset, la présence de plusieurs
niveaux Z équilibrés, la fraîcheur du recalcul et l'absence de modification de
scène avant `Matérialiser dans Fusion`.

Retour attendu :

`P64-H01 Fusion OK 0.1.42 - commit <sha>`

Cette preuve ne valide ni les valeurs physiques, ni la géométrie imprimée, ni
l'impression réelle.

## Suite verrouillée

Après P64-H01V, P44-VH02 reste la seule mission de code suivante : suppression
directe des éléments, confirmation transactionnelle de suppression d'un
conteneur non vide, puis nommage incrémental des nouveaux conteneurs. P45 et les
missions géométriques restent bloquées.
