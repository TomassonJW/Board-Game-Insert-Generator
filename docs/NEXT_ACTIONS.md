# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Gate humaine active

### Gate - P4-M003 generation de blanks rectangulaires Fusion

Statut : `blocked`.

Decision demandee :

- autoriser ou refuser le demarrage de `P4-M003` ;
- confirmer que la premiere generation Fusion peut creer des composants, corps
  rectangulaires ou esquisses reels ;
- confirmer que Fusion ne doit toujours pas recalculer layout, tolerances ou CAD
  IR ;
- definir le niveau de validation manuelle attendu dans Fusion ;
- confirmer qu'aucun export STL/3MF ni validation physique ne sont inclus dans ce
  lot.

Contexte :

- `P4-M001` a livre la CAD IR V0 dans `src/board_game_insert_generator/cad_ir.py` ;
- `P4-M002` a cree le squelette isole `fusion_addin/BoardGameInsertGenerator` ;
- le squelette detecte le cas Zero Doc et planifie les operations en
  `planned_only` ;
- `adsk` reste interdit dans `src/board_game_insert_generator` ;
- aucune geometrie Fusion reelle n'est encore generee.

Options :

- Option 1 recommandee : autoriser une generation minimale de blanks
  rectangulaires depuis la CAD IR, sans export et sans logique metier nouvelle.
- Option 2 : demander une verification manuelle du chargement du squelette dans
  Fusion avant toute creation de geometrie.
- Option 3 : differer Fusion et renforcer d'abord les cavites ou modules
  composites dans le coeur Python.

Recommandation :

- choisir l'option 1 seulement si la mission reste limitee a la creation de
  blanks rectangulaires inspectables dans Fusion ;
- garder les exports STL/3MF et la validation physique pour des gates separees ;
- documenter explicitement la procedure Zero Doc et les resultats de verification
  manuelle Fusion.

Risques :

- transfert accidentel de logique metier dans Fusion ;
- confusion entre verification visuelle Fusion et validation d'impression ;
- dependance implicite a une version locale de Fusion ;
- creation de geometrie difficile a tester automatiquement.

Fichiers concernes probables si la gate est validee :

- `fusion_addin/BoardGameInsertGenerator/` ;
- `docs/FUSION_360_STRATEGY.md` ;
- `docs/CAD_IR_CONTRACT.md` ;
- tests hors Fusion pour la conversion non-API ;
- log de mission et pilotage projet.

Validation attendue de l'humain :

- repondre explicitement que `P4-M003` est autorisee ;
- confirmer le perimetre exact de generation Fusion ;
- confirmer si une verification manuelle dans Fusion est obligatoire pendant la
  mission.

## Missions bloquees tant que la gate n'est pas validee

- `P4-M003 - Generer des blanks rectangulaires Fusion`.
- Premier export STL/3MF.
- Validation physique par impression reelle.
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
