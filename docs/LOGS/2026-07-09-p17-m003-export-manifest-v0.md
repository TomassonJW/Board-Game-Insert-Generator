# 2026-07-09 - P17-M003 export manifest V0

Mission : `P17-M003 - Export manifest V0`.

Implementation : `export_printables` ecrit maintenant `bgig_export_manifest.json` et `bgig_export_manifest.md` dans le dossier export.

Le manifeste JSON contient : schema `bgig.export_manifest.v0`, politique export, format, timestamp, statut, settings UI, source CAD IR si disponible, assets, modules, fichiers exportes, refus, warnings, `print_validated: false` et `printability_validated_by_print: no`.

Limites : manifeste preprint uniquement, aucune validation Fusion humaine encore effectuee pour P17, aucune impression physique validee.

Suite : `P17-M004 - Printability blockers V0`.
