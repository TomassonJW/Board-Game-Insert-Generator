# 2026-07-10 - P19-M001 BoxFillPlan contract

ADR-0037 accepte `box_fill_plan.v0` comme contrat P19. Le bloc sera optionnel, versionne, CAD-agnostic et retrocompatible; il ne remplace ni les configurations existantes ni `volumetric_grid`.

Le contrat distingue explicitement volume de boite, module manuel, reservation, layer, allocation asset, compartiment/feature reference et FreeVolume aggregate. Il interdit toute couverture implicite et toute source de verite Fusion.

Suite : P19-M002, dataclasses et loader du bloc optionnel dans le moteur Python pur.