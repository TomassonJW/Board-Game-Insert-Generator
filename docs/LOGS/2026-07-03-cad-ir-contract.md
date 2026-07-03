# 2026-07-03 - Contrat CAD IR

Mission : `P4-M001 - Definir le contrat de representation intermediaire CAD`

## Contexte

La gate P4-M001 a ete validee humainement apres le rapport P4-M000. Le perimetre
autorise consiste a preparer une representation CAD abstraite sans integration
Fusion 360 executable.

## Travail realise

- Ajout du module `board_game_insert_generator.cad_ir`.
- Ajout d'une scene `CadScene` serialisable et CAD-agnostic.
- Representation de la boite de reference non imprimable, des composants, des
  corps rectangulaires, des dimensions theoriques/imprimables, des operations
  abstraites, des parametres, des classifications de faces et des tolerances
  appliquees.
- Ajout de tests unitaires dedies.
- Documentation du contrat et ADR-0007.

## Limites

- Aucun import `adsk`.
- Aucun adaptateur Fusion executable.
- Aucun export STL/3MF.
- Aucune modification des valeurs de tolerance par defaut.
- Aucune validation physique ou CAD concrete.

## Suite

`P4-M002` necessite une nouvelle validation humaine car il ouvrirait le perimetre
d'un squelette d'adaptateur Fusion.
