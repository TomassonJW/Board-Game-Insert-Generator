# 2026-07-10 - P19-M002 BoxFillPlan models and loader

`box_fill_plan.v0` est implemente dans le coeur Python comme bloc racine optionnel. Il derive BoxFillBox et les assets des objets config existants, puis charge layers, reservations, modules manuels, allocations, compartiments `Cavity` et features `Feature` sans dependance Fusion.

Preuve : fixture `examples/box_fill_manual_v0.json`; tests de chargement, schema inconnu/version refusee et retrocompatibilite sans bloc. Les invariants de collision, coverage et FreeVolume ne sont pas encore revendiques.

Suite : P19-M003, analyse et validation du plan manuel.