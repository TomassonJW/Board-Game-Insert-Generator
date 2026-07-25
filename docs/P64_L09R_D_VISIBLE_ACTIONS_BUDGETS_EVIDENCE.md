# P64-L09R-D — Preuve des actions et budgets visibles

Date : 2026-07-25

Statut : `implemented-product`, `automated-validated`.

## Portée livrée

- `Calculer`, `Finaliser` et `Matérialiser` sont trois boutons distincts, rendus en permanence dans la barre inférieure.
- Projet neuf ou source modifiée : seul `Calculer` peut être actif.
- Plan minimal courant : `Finaliser` et `Matérialiser` sont actifs ; `Matérialiser` cible `minimal_layout`.
- Plan final courant : `Finaliser` reste actif pour une relance explicite et `Matérialiser` cible `finalized_plan`.
- Calcul, finition ou matérialisation active : les trois actions sont grisées.
- Le budget du calcul et celui de la finition sont deux sélecteurs indépendants avec cinq niveaux : Rapide, Court, Normal, Long et Approfondi.
- Chaque sélecteur possède un champ adjacent non éditable : `3 s max`, `10 s max`, `20 s max`, `60 s max` ou `3 min max`.
- Les deux valeurs persistent dans état local du document, sans entrer dans les dimensions physiques du projet.
- Une modification du calcul conserve le contrat historique : plans minimal et final deviennent obsolètes.
- Une modification de la finition appelle une invalidation dédiée : le plan final devient obsolète, le plan minimal reste courant et matérialisable.

## Preuves automatisées

- Cycle staged : changement de finition après plan final, minimal inchangé, final stale et sélection CAD minimale encore valide.
- Pont palette : persistance locale de `long`, rechargement exact et aucune sauvegarde implicite du projet.
- DOM : trois boutons présents, ordre fixe, cinq options dans chaque sélecteur, champs read-only et limites exactes.
- Routage : artefact final préféré seulement si courant ; sinon artefact minimal.
- Verrou opérationnel : les trois boutons partagent le même état actif.

## Validation

- Tests cycle : 18/18 OK.
- Tests pont palette : 29/29 OK.
- Tests DOM : 40/40 OK.
- Tests résultat, transport et synchro CAD : 28/28 OK.
- Syntaxe JavaScript extraite : `node --check` OK.
- Suite complète : 861/861 en 252,858 s ; un test natif ignoré sous Python 3.10.
- Compilation Python et `git diff --check` : OK.

## Limites et non-objectifs

- La jauge temporaire, son emplacement exact et le hors-thread UI appartiennent à P64-L09R-E.
- Aucun benchmark, package Fusion, réglage Fusion, observation Fusion ou fait impression produit.
- La gate humaine P64-L09R-V reste inactive avant E et F.
