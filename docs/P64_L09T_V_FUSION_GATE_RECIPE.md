# P64-L09T-V — recette Fusion humaine 0.1.70

Date : 2026-07-27.

## Statut avant observation

- Package candidat : `0.1.70`.
- Gate : `prepared-not-human-observed`.
- `fusion-validated=false`.
- `print-validated=false`.
- `0.1.69` reste `human-KO`, `do-not-run`.

Codex prépare et installe l'environnement. Thomas ne lance aucun script et ne
réinstalle jamais 0.1.69.

## Prérequis visibles

Avant la recette, vérifie :

- le manifeste installé annonce `0.1.70` ;
- le commit installé correspond au commit intégré annoncé par Codex ;
- la fixture courante est
  `p64-l09tv-01-explicit-composite.bgig.json` ;
- la palette propose `Calculer`, `Finaliser` et `Matérialiser` avec des états
  distincts ;
- le profil de calcul et le profil de finition sont `Normal`.

Si un prérequis manque, arrête la gate et rapporte KO sans poursuivre.

## Parcours 1 — cycle explicite et smoke public

1. Recharge complètement BGIG 0.1.70 et ouvre Atelier de rangement.
2. Ouvre la fixture publique préparée.
3. Modifie une valeur géométrique.
4. Vérifie que le plan minimal, le plan final et la scène deviennent obsolètes.
5. Vérifie qu'aucun placement n'est republié automatiquement.
6. Clique `Calculer`.
7. Vérifie que le minimal courant est publié seulement après ce clic.
8. Clique `Finaliser`, puis `Matérialiser`.
9. Exige un résiduel imprimable nul et aucun faux succès.

## Parcours 2 — réservations et parois

1. Vérifie que le plateau n'expose aucune origine X/Y manuelle.
2. Vérifie que sa pose X/Y est calculée automatiquement et peut être décentrée.
3. Vérifie que sa pose Z est la plus haute admissible.
4. Vérifie qu'un plateau proche d'une cavité ne rabote ni ne translate celle-ci.
5. Inspecte la paroi entre chaque cavité et la découpe supérieure.
6. Tout conflit, trou central non fermé ou paroi manifestement insuffisante
   vaut KO.

## Parcours 3 — priorité plancher d'abord

1. Sur un cas qui tient entièrement au sol, vérifie que tous les corps restent
   dans la couche basse.
2. Sur un cas où une pile est nécessaire, vérifie qu'une pile reste admise.
3. Vérifie qu'aucun empilement prématuré n'est préféré à un plan complet plus
   bas.

## Parcours 4 — CasLimite01+

1. Ouvre le projet local `CasLimite01+`.
2. Calcule en `Normal`.
3. Finalise en `Normal`.
4. Matérialise tous les conteneurs utilisateur.
5. Exige :
   - cavités aux poses du plan minimal ;
   - réservation automatique ;
   - unions avant coupes ;
   - aucun jeu interne propriétaire–annexe ;
   - jeux externes conservés ;
   - résiduel nul.

## Parcours 5 — CasLimite02+

1. Ouvre le projet local `CasLimite02+`.
2. Calcule en `Normal`.
3. Finalise en `Normal`.
4. Matérialise tous les conteneurs utilisateur.
5. Vérifie que le trou central est fermé, que le plateau et le livret restent
   des réservations virtuelles et qu'aucune cavité ne se déplace.

## Parcours 6 — arrêt anticipé explicable

Déclenche ou inspecte une tentative bornée qui ne finalise pas. Le résultat
doit afficher :

- la phase ;
- la raison d'arrêt ;
- le temps écoulé ;
- le plafond ;
- le nombre de candidats et rejets utile ;
- `proof_of_impossibility`.

Si la preuve d'impossibilité est fausse, l'UI doit dire que le résultat reste
inconnu, jamais qu'il est impossible.

## Verdict à transmettre

Pour chaque parcours, rapporte `OK` ou `KO` avec :

- capture de la palette ;
- capture de la scène ;
- identité du projet et du plan courant ;
- compte des composants, unions et coupes ;
- résiduel annoncé ;
- diagnostic complet en cas d'arrêt.

La gate peut promouvoir `fusion-validated` seulement après un verdict humain
OK complet. Elle ne promeut jamais `print-validated`.
