# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P3-M004 - Ajouter un protocole de calibration physique

Statut : `ready`.

Pourquoi maintenant :

- `P3-M002` rend les tolerances appliquees explicites par face ;
- `P3-M003` ajoute des profils d'impression opt-in et surchargeables ;
- les profils restent experimentaux et non calibres physiquement ;
- le projet doit eviter de confondre preset logiciel et validation par impression.

Objectif :

- documenter un protocole de calibration physique par coupons de test et tableau
  de mesure, sans effectuer ni revendiquer d'impression reelle.

Contraintes :

- ne pas modifier les valeurs de tolerance par defaut ;
- ne pas declarer les profils valides physiquement ;
- ne pas lancer Fusion 360, STL ou 3MF ;
- rester sur documentation et exemples locaux reproductibles.

Validation attendue :

- relecture documentaire ;
- suite unitaire pour verifier la coherence des fichiers de pilotage ;
- `git diff --check`.

## Missions a ne pas lancer tout de suite

- Modification des valeurs de tolerance par defaut sans gate humaine dediee.
- Generation Fusion 360 de blanks tant que `P4-M000` n'a pas produit de rapport
  de gate.
- Cavites complexes tant que les parois minimales et clearances ne sont pas
  formalisees.
- Modules composites complets tant que `P6-M001` n'est pas cadree.
- Assistant de conception tant que plusieurs strategies et profils ne sont pas
  stabilises.
- Packaging produit tant que des exemples imprimes reels ne sont pas disponibles.

## Fin de chaque mission

Avant de terminer :

- mettre a jour `docs/STATUS.md` ;
- mettre a jour `docs/BACKLOG.md` ;
- remplacer cette liste par les prochaines actions reelles ;
- ajouter une ADR si une decision structurante a ete prise ;
- ajouter une entree de log si l'orientation ou le statut a change ;
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances ;
- committer proprement si le depot a ete modifie.