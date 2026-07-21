# P64-L03R-A — Correction du contrat minimal/final

## Déclencheur

La revue humaine du package Fusion 0.1.56 constate que `Calculer l'agencement`
affiche déjà des enveloppes étendues à la boîte, que `Finaliser` ne transforme
pas la géométrie et qu'une nouvelle proposition ne réactive pas toujours la mise
à jour de la scène.

## Décision

- enregistrer P64-L03V comme KO contextuel ;
- distinguer `minimal_layout` et `finalized_plan` ;
- rendre le plan minimal certifié matérialisable et exportable ;
- réserver toute absorption du résiduel aux politiques de finition ;
- adopter un portfolio borné de graines, ancres et propagations ordonné par
  rareté de placement ;
- suivre la scène Fusion par type et digest exact d'artefact.

## Livrables

- ADR-0074 ;
- contrat P64-L03R minimal et matérialisation duale ;
- amendement d'ADR-0071 et du programme P64 ;
- pilotage, backlog, capabilities, roadmap et tests documentaires synchronisés.

## Limites

Aucun runtime, solveur, budget, schéma, valeur physique, CAD IR ou scène n'est
modifié. Le cas dense 11 × 34 reste `no_solution_within_budget`.
`fusion-validated: false`, `print-validated: false` pour la correction.

## Suite

P64-L03R-B devient la seule prochaine mission : produire le plan global minimal
multi-graines sans allocation de surplus.
