# 2026-07-10 - P17 printable export and preprint validation

Mission : enregistrement de la validation humaine Fusion `P17-PRINTABLE-EXPORT-AND-PREPRINT-SPRINT-V`.

Commit observe pendant le smoke test : `5d99d36`.

Validation Fusion confirmee : preset `p17_printable_export`, generation asset-first, compartiments et encoches V0, action `export_printables`, STL par module BGIG imprimable, manifestes JSON/Markdown et preservation des objets non-BGIG apres `clear_bgig_scene`.

Le filtre export est confirme : non-BGIG, racines, references/outlines, sketches debug, helpers, sources et vues eclatees ne sont pas exportes comme STL imprimables.

Statut : `fusion-validated-v0`. `print-validated: false` est maintenu : aucune impression physique, validation slicer, materiau ou mesure dimensionnelle reelle n'a ete realisee.

Suite autorisee : `P18-VISION-UX-VOLUMETRIC-REBASE-SPRINT`, uniquement documentaire jusqu'a une nouvelle gate humaine d'architecture ou produit.
