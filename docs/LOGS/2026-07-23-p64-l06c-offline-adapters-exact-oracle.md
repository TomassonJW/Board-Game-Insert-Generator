# Log — P64-L06C comparateurs offline et petit oracle exact

Date : 2026-07-23

## Mission

Fournir une interface commune pour deux candidats maximum et un petit oracle
exact interne, sans installer de dépendance et sans modifier le solveur produit.

## Décisions réversibles

- Deux candidats actifs : solveur BGIG courant et oracle exact interne.
- Résultat compact, déterministe et indépendant du plan complet.
- Recertification BGIG fraîche obligatoire pour toute solution.
- Modèle exact limité à un niveau, aucune réservation, une variante locale et au
  plus quatre conteneurs.
- Refus explicite de l'interdiction de rotation par l'adapter courant.
- Aucun accès au holdout.

## Implémentation

- protocole `bgig.solver_benchmark_adapter_protocol.v1` ;
- résultat `bgig.solver_benchmark_adapter_result.v1` ;
- recherche exhaustive des placements stables gauche/bas ;
- bornes fixes de hauteur, empreinte, volume et aire ;
- caps 4 participants, 250 000 états, 1 000 000 essais ;
- relecture du digest projet avant tout calcul.

## Preuves intermédiaires

- 9/9 tests L06C et 18/18 corpus + adapters ;
- 6/6 cas discovery dans le périmètre exact ;
- 4 faisables et 2 impossibles correctement classés ;
- résultat déterministe répété ;
- cap forcé classé `bounded_unknown` ;
- garde documentaire 2/2 et alignement Fusion-only 6/6 ;
- suite complète 707/707 en 184,570 s ;
- Ruff et compilation ciblés OK.

## Frontières préservées

Aucune dépendance externe, aucun changement de solveur, budget public, deadline,
certificat public, schéma, tolérance, géométrie, finalisation, CAD, scène ou
manifest Fusion. `fusion-validated: false`. `print-validated: false`.
