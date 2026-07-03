# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Gate humaine active

### Gate - P4-M002 squelette d'adaptateur Fusion 360

Statut : `blocked`.

Decision demandee :

- autoriser ou refuser le demarrage de `P4-M002` ;
- definir si le prochain lot peut creer un squelette d'adaptateur Fusion ;
- confirmer que le coeur Python pur reste sans import `adsk` ;
- confirmer qu'aucun STL/3MF, aucune generation exploitable et aucune validation
  physique ne sont inclus dans ce prochain lot.

Contexte :

- `P4-M001` a livre la CAD IR V0 dans `src/board_game_insert_generator/cad_ir.py` ;
- le contrat est documente dans `docs/CAD_IR_CONTRACT.md` ;
- la decision structurante est consignee dans`n  `docs/DECISIONS/ADR-0007-cad-agnostic-ir.md` ;
- la CAD IR represente les blanks rectangulaires sans appeler Fusion 360.

Options :

- Option 1 recommandee : autoriser uniquement un squelette d'adaptateur Fusion
  non productif, isole du coeur, sans generation CAD exploitable.
- Option 2 : demander une consolidation supplementaire de la CAD IR avant tout
  fichier lie a Fusion.
- Option 3 : autoriser une premiere generation Fusion de blanks rectangulaires,
  ce qui devrait probablement declencher une gate plus stricte.

Recommandation :

- choisir l'option 1 seulement si le perimetre reste limite a la structure
  d'adaptateur, la documentation d'installation et les tests d'import hors
  Fusion ;
- garder la premiere generation Fusion exploitable pour une gate separee.

Risques :

- confusion entre squelette et fonctionnalite CAD utilisable ;
- import accidentel `adsk` dans le coeur Python ;
- duplication de logique layout/tolerance dans l'adaptateur ;
- elargissement implicite vers export STL/3MF.

Fichiers concernes probables si la gate est validee :

- `docs/FUSION_360_STRATEGY.md` ;
- futur repertoire d'adaptateur Fusion ;
- tests d'import ou de garde-frontiere ;
- `docs/BACKLOG.md` et `docs/STATUS.md`.

Validation attendue de l'humain :

- repondre explicitement que `P4-M002` est autorisee ;
- indiquer si le squelette peut contenir des references `adsk` hors du coeur
  Python ou s'il doit rester entierement mockable ;
- confirmer que la generation de blanks rectangulaires reste hors scope.

## Missions bloquees tant que la gate n'est pas validee

- `P4-M002 - Creer un squelette d'adaptateur Fusion 360`.
- Premiere generation Fusion exploitable.
- Premier export STL/3MF.
- Modification des valeurs de tolerance par defaut.
- Modules composites complets.

## Fin de chaque mission

Avant de terminer :

- mettre a jour `docs/STATUS.md` ;
- mettre a jour `docs/BACKLOG.md` ;
- remplacer cette liste par les prochaines actions reelles ;
- ajouter une ADR si une decision structurante a ete prise ;
- ajouter une entree de log si l'orientation ou le statut a change ;
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances ;
- committer proprement si le depot a ete modifie.
