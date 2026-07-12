# ADR-0051 - Plan de fermeture de volume global V0.1

## Statut

Acceptee, decision reversible de la mission P41 du MVP V0.1.

## Date

2026-07-12

## Carte liee

- `P41 - Solveur de fermeture du volume`.

## Contexte

P39 dimensionne les bacs et P40 reserve les plateaux/livrets, mais aucun des
deux ne prouve que tous les volumes tiennent ensemble, qu ils gardent leur jeu,
ou que le volume restant est traite.

## Decision

`bgig.volume_closure.v1` devient le resultat pur de P41. Il place les bacs en
X/Y/Z, reserve la pile superieure, place les remplissages exacts, classifie les
regions restantes et controle collisions/conservation. Les volumes creux sont
proposes avant les volumes pleins ; ces derniers exigent une demande utilisateur.

## Consequences

- Le bouton principal retourne un plan complet et explicable.
- P42 consommera ce plan comme unique source de geometrie fonctionnelle.
- Fusion reste un adaptateur de sortie, sans decision de placement.

## Alternatives refusees

- Reutiliser P20/P21 : vocabulaire P23 incompatible avec la pile V1.
- Generer directement Fusion : frontiere moteur/Fusion cassee.
- Ajouter des blocs pleins silencieux : contraire a la vision produit.
