# P64-H03 — Recherche dirigée par contraintes

## Statut

Implémenté et automated-validated dans le package d’essai 0.1.45.
`fusion-validated: false`, `print-validated: false`. Gate suivante : P64-H03V.
Aucun commit n’est créé avant le retour de l’essai Fusion demandé par Thomas.

## Déclencheur

Le projet Fusion réel reste physiquement logeable mais un petit asset supplémentaire
peut faire rejeter tous les candidats : les cavités hautes sont placées sous le
plateau, le faisceau conserve des piles trop denses et les ordres XY valides sont
élagués. Des centaines de seeds hash ne garantissent pas de retrouver la solution.

## Objectif

- conserver le chemin canonique rapide lorsqu’il réussit ;
- chercher les étages et les positions XY à partir des contraintes qui ont causé
  le rejet, avant la reprise hash de P64-H02 ;
- répartir le surplus Z au bon membre d’une pile lorsque la position XY finale
  l’exige ;
- rester déterministe, borné et observable, sans modifier les données physiques.

## Contrat de recherche

Après un cul-de-sac canonique lié aux réservations supérieures, le solveur essaie
des ordres structurés. Le portefeuille `top_inset_safe_top_asc` active :

1. un faisceau borné de compositions verticales non contiguës, diversifié par
   nombre de piles et classé par dette de hauteur irrécupérable ;
2. jusqu’à 128 partitions de piles et 32 ordres XY géométriques par groupe ;
3. une estimation spatiale fondée sur les rectangles réels des cavités et des
   réservations supérieures ;
4. un transfert de surplus Z des membres inférieurs expansibles vers le membre
   supérieur, sans changer la hauteur totale de la pile, sans descendre sous un
   minimum et sans modifier une dimension fixe ;
5. la validation physique existante comme autorité finale.

Les sept stratégies structurées précèdent les six seeds hash de P64-H02. Le
premier candidat complet gagne. Les compteurs `directed_portfolios_evaluated` et
`hash_portfolios_evaluated` rendent le coût réel visible.

## Invariants

- aucun schéma projet, default, minimum, jeu, tolérance ou mode ne change ;
- aucune cavité, réservation, règle de support ou validation n’est ignorée ;
- aucune dimension fixe n’est redistribuée ;
- aucune dépendance d’optimisation externe n’est ajoutée ;
- le cœur reste pur Python, sans import `adsk` ;
- aucune scène ni matérialisation automatique n’est ajoutée ;
- la recherche canonique réussie ne paie aucun coût supplémentaire.

## Acceptation automatisée

- l’autosauvegarde Fusion exacte construit 8 conteneurs sans diagnostic de
  plateau ;
- le scénario ajoute successivement 6 petits assets dans un bac et reste
  constructible ;
- le stress déterministe construit jusqu’à 20 petits conteneurs supplémentaires,
  soit 28 conteneurs au total, en créant 14 intervalles Z ;
- une régression automatisée construit 14 conteneurs sans utiliser de seed hash ;
- le transfert Z conserve la hauteur totale et respecte les minima ;
- 495 tests passent, y compris le digest canonique P66.

## Gate P64-H03V

Préparation : `scripts/fusion/prepare_p64_h03_constraint_directed_search_test.ps1`.

Avant commit, Thomas répond seulement `P64-H03 Fusion trial OK 0.1.45
(uncommitted)` ou décrit le KO contextuel. Après un essai positif, Codex crée le
commit atomique, intègre et installe le package final ; la preuve canonique pourra
alors porter le SHA final.

Cette gate ne valide ni valeurs physiques ni impression réelle.