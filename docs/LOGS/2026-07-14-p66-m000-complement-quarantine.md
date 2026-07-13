# 2026-07-14 - P66-M000 quarantaine des complements experimentaux

## Contexte

P66 prepare l acceptance humaine du MVP V0.1 Fusion-only. ADR-0061 impose de
retirer les complements experimentaux du parcours normal sans casser les projets
historiques explicites.

## Changements

- palette : aucune creation normale de Bac vide, Bloc plein / cale ou Separateur ;
- presets : la reponse versionnee conserve son schema et expose une liste de
  complements vide ;
- compatibilite : les complements historiques restent visibles, modifiables,
  sauvegardables et regenerables lorsqu ils sont deja presents dans un projet ;
- package : manifest Fusion 0.1.20 et marqueurs d installation adaptes.

## Verifications

- 446 tests automatisees verts, dont DOM, bridge, import/round-trip et
  materialisation d une cale historique explicite ;
- syntaxe JavaScript de la palette et compilation Python vertes ;
- git diff --check vert ; aucun import adsk dans le coeur Python.

## Impact

Aucun solveur, tolerance, geometrie, migration destructive, corps automatique ou
semantique future des complements ne change. P66-M001 peut maintenant preparer
les fixtures et la gate Fusion, sans validation Fusion ou impression revendiquee.

## Suivi

- Executer P66-M001 puis s arreter a la gate humaine P66-V.
