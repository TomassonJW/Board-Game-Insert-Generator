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

Statut : `manual_validation_required`.

`P6-M002 - Generer les encoches de doigts simples dans Fusion` est code et doit
maintenant etre valide manuellement dans Fusion avant tout elargissement.

Action humaine attendue : `P6-M002V - Valider manuellement les encoches de doigts
Fusion`.

Perimetre du smoke test :

- exporter `examples/simple_finger_notch_tray.json` en CAD IR ;
- pointer l'add-in Fusion vers cette CAD IR ;
- verifier le message `Simple finger notch cuts: 1` ;
- verifier que la coupe d'encoche frontale est visible sur le body cible ;
- mesurer blank, cavite et encoche ;
- conserver `print-validated: false` tant qu'aucune impression 3D n'a ete faite.

## Mission ready non gated si Fusion est reportee

Statut : `ready_if_gate_deferred`.

`P8-M001 - Specifier la grille volumetrique 3D et les layers`.

- Capability : `C-GRID-3D`, `C-LAYERS`.
- Milestone : `M7 Volumetric planner`.
- Objectif : definir le contrat pur Python de cellules X/Y/Z, layers,
  reservations, volumes libres et collisions, sans solveur complet.
- Gate : aucune si la mission reste documentaire/specification et ne modifie pas
  le schema public executable.
- Validation : tests documentaires, backlog/status/capability map mis a jour.

Cette mission ne doit etre prise que si l'humain reporte explicitement la gate
Fusion ou demande une mission non gated.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.