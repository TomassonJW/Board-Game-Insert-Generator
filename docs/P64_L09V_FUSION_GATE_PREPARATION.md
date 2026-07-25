# P64-L09V — préparation de la gate Fusion combinée

Date : 2026-07-24
Paquet : BGIG 0.1.63
Statut : supersédée sans observation par ADR-0088 et P64-L09R-A ;
ne pas exécuter cette gate ; print-validated=false.

> Cette préparation reste une preuve historique de 0.1.63. Ses critères
> anti-chute et finalisation obligatoire ne correspondent plus au produit décidé.
> La prochaine gate sera P64-L09R-V après les lots L09R-B à F.

## Paquet préparé

Le script `scripts/fusion/prepare_p64_l09v_combined_gate.ps1` prépare et
vérifie un handoff local unique :

- installe l'add-in 0.1.63 et le runtime SCIP déjà scellé ;
- vérifie les marqueurs support matériel, réservations SCIP et finalisation
  couplée ;
- écrit un marqueur du commit réellement installé ;
- préserve l'état documentaire précédent avant de sélectionner le cas plateau ;
- règle la palette sur Auto intelligent + Approfondi ;
- installe trois projets publics et un résumé à digest dans
  `Documents\BGIG\projects`.

## Trois observations séparées

1. `p64-l09v-01-anti-fall-negative.bgig.json` force le solveur à traiter un
   petit conteneur dans une empreinte dense. Il ne doit jamais publier un
   empilement où ce conteneur tombe dans l'ouverture inférieure.
2. `p64-l09v-02-stable-bridge.bgig.json` conserve des corps larges : un
   pontage réellement appuyé sur les rebords doit rester admissible.
3. `p64-l09v-03-tray-finalization.bgig.json` ajoute une réservation supérieure
   exacte : le cas doit atteindre SCIP, produire un plan final certifié, puis
   matérialiser le plateau sans réduire ni percer les cavités.

Ces trois cas distinguent volontairement le refus anti-chute, le pontage valide
et le parcours plateau/finalisation. Ils ne tentent pas de faire passer une seule
scène pour trois preuves différentes.

## Contrôles automatisés du préparateur

- preuve anti-chute : `falls_through_opening` même avec `has_lid=true` sans
  certificat de fermeture ;
- preuve pontage : `bridged_on_material`, polygone stable ;
- trois projets normalisés et préparables hors Fusion ;
- contrôle rapide du pontage public : 3/3 placements certifiés ;
- une réservation supérieure exacte sur le troisième cas ;
- marqueurs installés : `material_surface_v1`, `top_inset_support`,
  `bounded_growth_local_repair_balanced_proportional` et
  `bgig.finalization_secondary_objectives.v1` ;
- artefact et archive SCIP vérifiés par digest ;
- simulation complète du préparateur : 74 contrôles ciblés, un contrôle natif
  ignoré sous Python 3.10 ;
- suite complète : 855/855 en 225 s, avec un test SCIP natif ignoré sous
  Python 3.10.

## Limites et interdits

- aucun benchmark, tuning ou holdout n'est exécuté ;
- aucune nouvelle valeur physique, pose ou sémantique de couvercle ;
- `has_lid` seul ne ferme toujours pas une ouverture ;
- aucune scène ne doit être créée depuis un plan partiel ou minimal quand une
  réservation impose la finalisation ;
- cette gate peut promouvoir `fusion-validated`, jamais `print-validated`.
