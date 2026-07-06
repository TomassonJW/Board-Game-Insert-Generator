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

Statut : `required_before_next_fusion_geometry`.

`P6-M003 - Formaliser la taxonomie des encoches et aides de prise` est termine.
La taxonomie distingue les encoches top-open, demi-lunes futures, fenetres de
paroi, scoops internes, degagements lateraux et acces bilateraux sans generer de
nouvelle geometrie Fusion.

Action humaine requise avant toute mission qui genere reellement : demi-lune
courbe, scoop interne non traversant, fillet/conge, fond arrondi, geometrie
courbe, grille 3D ou module composite dans Fusion.

## Mission bloquee par gate

`P6-M004 - Gate generation Fusion des aides de prise avancees`.

- Capability : `C-FILLETS`, `C-FEATURE`, `C-ACCESS`.
- Objectif : choisir explicitement la prochaine operation Fusion reelle a tenter,
  ses limites et son smoke test manuel.
- Statut : `blocked` jusqu'a validation humaine.

## Mission ready non gated si la gate Fusion est reportee

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