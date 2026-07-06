# Next Actions

Derniere mise a jour : 2026-07-06

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici, sauf gate humaine.

## Politique active - Integration Git autonome

Statut : `active`.

Le chemin standard est `direct-to-main` : une mission doit etre testee, commitee,
integree directement dans `main`, puis poussee vers `origin/main` avant selection
d'une mission suivante. Les pull requests sont reservees aux cas de repli :
protection GitHub, review imposee, conflit, divergence non triviale, risque
structurant, authentification absente ou refus de push direct.

## Gate humaine active

Statut : `none`.

`P6-M002V - Valider manuellement les encoches de doigts Fusion` est valide apres
le correctif `b27c2e7`. La version validee est une `top-open rectangular wall
notch` : blank OK, cavite OK, message OK, encoche frontale ouverte vers le haut
OK, pas de fenetre fermee. `print-validated: false` reste explicite.

## Mission ready

Statut : `ready`.

`P6-M003 - Formaliser la taxonomie des encoches et aides de prise`.

- Capability : `C-FEATURE`, `C-FILLETS`, `C-ACCESS`.
- Milestone : `M5 CAD ergonomic features` / `M8 Ergonomic planner`.
- Objectif : definir une taxonomie claire et parametree des aides de prise sans
  nouvelle generation Fusion reelle.
- Gate : aucune tant que la mission reste abstraite et CAD-agnostic.
- Validation : tests unitaires, CLI Markdown/JSON/export CAD IR sur
  `simple_tray` et `simple_finger_notch_tray`, `git diff --check`, absence
  d'`adsk` dans `src/board_game_insert_generator`.
- Arret obligatoire : toute generation Fusion de demi-lune courbe, scoop interne,
  fillet/conge, fond arrondi, geometrie courbe, grille 3D ou module composite.

## Mission ready non gated si P6-M003 est terminee et gate Fusion atteinte

Statut : `ready_if_gate_deferred`.

`P8-M001 - Specifier la grille volumetrique 3D et les layers`.

- Capability : `C-GRID-3D`, `C-LAYERS`.
- Milestone : `M7 Volumetric planner`.
- Objectif : definir le contrat pur Python de cellules X/Y/Z, layers,
  reservations, volumes libres et collisions, sans solveur complet.
- Gate : aucune si la mission reste documentaire/specification et ne modifie pas
  le schema public executable.
- Validation : tests documentaires, backlog/status/capability map mis a jour.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.