# ADR-0007 - CAD-agnostic intermediate representation

## Statut

Accepte.

## Date

2026-07-03

## Carte liee

- `P4-M001 - Definir le contrat de representation intermediaire CAD`

## Contexte

Le moteur Python pur sait maintenant charger une configuration, produire un
layout simple, appliquer les tolerances par role de face et exposer des rapports.
La prochaine phase vise Fusion 360, mais l'adaptateur ne doit pas recalculer le
layout ni les tolerances.

Il faut donc stabiliser un contrat intermediaire avant tout code Fusion
executable.

## Options

1. Passer directement `PrintableBody` a l'adaptateur Fusion.
2. Creer une CAD IR dediee, serialisable et CAD-agnostic.
3. Creer directement un script Fusion qui reconstruit la scene.

## Decision

Choisir l'option 2.

Le projet ajoute une CAD IR dediee dans `board_game_insert_generator.cad_ir`.
Elle represente une scene CAD abstraite : boite de reference, composants, corps
rectangulaires, dimensions theoriques et imprimables, operations abstraites,
parametres, metadata, classifications de faces et tolerances appliquees.

La CAD IR V0 cible uniquement les blanks rectangulaires et ne contient aucune
dependance Fusion 360.

## Consequences

Positives :

- l'adaptateur Fusion futur recevra un contrat explicite ;
- le coeur reste testable hors Fusion ;
- les dimensions CAD futures restent reliees aux decisions deja testees ;
- les metadata de tolerance restent auditables.

Negatives et risques :

- le contrat ajoute une couche de donnees supplementaire a maintenir ;
- certaines contraintes concretes de Fusion ne seront connues qu'apres un
  adaptateur executable ;
- le contrat V0 couvre les blanks rectangulaires, pas les cavites, couvercles ou
  modules composites.

## Alternatives refusees

L'option 1 est refusee car `PrintableBody` ne suffit pas a exprimer scene,
repere, parametres et operations attendues par un adaptateur CAD.

L'option 3 est refusee car elle ferait commencer l'integration Fusion avant le
contrat stable et risquerait de dupliquer la logique metier dans l'adaptateur.

## Suivi

- `tests/test_cad_ir.py` couvre le contrat V0.
- `docs/CAD_IR_CONTRACT.md` documente la scene et ses frontieres.
- `P4-M002` reste bloque par validation humaine avant tout adaptateur Fusion
  executable ou squelette d'adaptateur.
