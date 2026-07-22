# P64-L05V - Evidence d observation Fusion

Date : 2026-07-22
Package observe : add-in Fusion 0.1.58, commit installe `261f7cc`
Statut : observation positive partielle ; `fusion-validated: false` ; `print-validated: false`.

## Faits fournis par Thomas

- Le plan minimal affiche deux conteneurs, `Bac initial` et `Bac 888`, sur un etage.
- Le panneau witness affiche `Persistance : enregistre`, `Recherche poursuivie : Oui` et `Cache revendique : Non`.
- La trace affiche `exact_witness_file_not_found`, puis `certified_witness_stored_atomically`.
- L inspection de scene est read-only et ne trouve aucune occurrence ou entite BGIG ; aucune materialisation n est revendiquee.

## Interpretation limitee

Le premier calcul n avait pas d incumbent : `Warm start : non fourni` et `no_initial_incumbent` sont coherents avec l absence de witness preexistant. Ce retour prouve la premiere persistance, pas le rechargement compatible d un witness. Aucun chemin/digest de SolverCaseBundle DEV n est fourni.

La fixture est volontairement peu contrainte. Elle teste le contrat d insertion locale et les garde-fous, pas la capacite du solveur a retrouver un agencement humainement materialisable dans le projet complexe. Les volumes residuels affiches ne sont jamais une preuve de faisabilite.

## Suite de preuve

1. Recharger le meme projet apres un changement temporaire d effort et verifier un witness accepte et un warm start accepte.
2. Capturer avec le bouton DEV une manipulation reelle de `Mon insert`, puis fournir seulement le chemin local et le digest du bundle pour anonymisation.
3. Rejouer le bundle hors Fusion avant de cadrer toute evolution de solveur.
