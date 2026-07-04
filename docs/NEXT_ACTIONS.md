# Next Actions

Derniere mise a jour : 2026-07-04

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

Action demandee : executer le smoke test manuel `P6-M001V - Valider les cavites
rectangulaires Fusion`.

Contexte :

- la gate humaine P6-M001 a autorise les cavites rectangulaires simples dans
  Fusion ;
- l'add-in code maintenant `subtract_rectangular_cavity` sous forme de coupe
  rectangulaire verticale limitee au body cible ;
- les features ergonomiques `describe_cavity_feature`, encoches, fonds arrondis,
  fillets, couvercles et exports restent hors perimetre ;
- le coeur Python reste sans `adsk` et Fusion ne recalcule pas layout,
  tolerances ou clearances.

Validation attendue de l'humain :

- generer une CAD IR depuis `examples/simple_tray.json` ;
- la charger dans l'add-in via `cad_ir_path.txt` ou `cad_ir_input.json` ;
- lancer l'add-in dans un design Fusion de test ;
- verifier le message final, le blank, la cavite rectangulaire et le plancher
  conserve ;
- documenter les mesures avant toute mission Fusion suivante.

Tant que cette validation n'est pas enregistree, ne pas lancer P6-M002 ni de
nouvelle geometrie Fusion reelle.

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