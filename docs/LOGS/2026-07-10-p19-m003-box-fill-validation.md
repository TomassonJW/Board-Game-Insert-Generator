# 2026-07-10 - P19-M003 BoxFillPlan validation

Le moteur pur valide maintenant les volumes du BoxFillPlan dans la hauteur utile de la boite, les collisions, les IDs, layers et references. Les allocations sont comparees explicitement au count des assets : assets non couverts et sur-alloues sont refuses avec une issue actionnable.

`FreeVolume` V0 expose un agregat (volume boite utile moins modules/reservations) et declare `aggregate_only`. Il ne decrit pas encore de regions libres ni une garantie d'utilisabilite.

Suite : P19-M004, exposition Markdown/JSON/CAD IR sans changement Fusion.