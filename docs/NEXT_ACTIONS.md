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

Statut : `blocked`.

Decision demandee : autoriser, reporter ou recadrer `P6-M001 - Generer les
cavites rectangulaires simples dans Fusion`.

Contexte :

- North Star realignee vers un generateur volumetrique asset-first ;
- `C-CAVITY` et `C-FEATURE` sont `implemented-cad-ir`, pas `implemented-fusion` ;
- `C-FUSION-CAVITIES` et `C-FILLETS` restent `blocked` ;
- les rapports Markdown/JSON et la CAD IR exposent `subtract_rectangular_cavity`
  et `describe_cavity_feature` avec `fusion_generation: not_implemented` ;
- l'add-in Fusion actuel reste limite aux blanks rectangulaires et a la lecture
  CAD IR.

Options :

1. Autoriser `P6-M001` : generation Fusion limitee aux cavites rectangulaires
   simples, sans encoche, fond arrondi, fillet, export STL/3MF ni recalcul
   metier dans Fusion.
2. Autoriser une ADR technique avant code Fusion : strategie de cuts, booleans,
   robustesse et smoke test manuel.
3. Reporter Fusion et continuer hors gate avec `P8-M001 - Specifier la grille
   volumetrique 3D`.
4. Autoriser directement encoches/fonds arrondis reels dans Fusion : option
   deconseillee tant que les cuts rectangulaires ne sont pas stables.

Recommandation : option 1 si l'objectif est de prouver le prochain maillon
Fusion, option 3 si l'objectif est de renforcer la conception volumetrique avant
de toucher a la geometrie reelle.

Validation attendue de l'humain pour P6-M001 :

- type exact d'operation Fusion autorise ;
- limites explicites sur booleans, encoches, fonds arrondis et fillets ;
- fixture CAD IR a utiliser ;
- procedure de smoke test manuel attendue dans Fusion 360.

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