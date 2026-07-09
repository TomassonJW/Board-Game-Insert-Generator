# 2026-07-09 - P17-M001 export/preprint ADR

Mission : `P17-M001 - ADR export/preprint V0`.

Decision prise : `ADR-0035-printable-export-preprint-v0.md` accepte un export V0 Fusion-only. Le coeur Python reste sans dependance `adsk` et ne produit pas de STL/3MF.

Contrat retenu :

- STL par module imprimable en V0 ;
- 3MF reporte sauf API Fusion simple et fiable ;
- filtrage via registry BGIG ;
- exclusion des objets non-BGIG, references/outlines, sketches debug, helpers/source occurrences et vues eclatees par defaut ;
- dossier d'export dedie ;
- noms deterministes et filesystem-safe ;
- manifeste JSON et Markdown ;
- `print_validated: false` obligatoire.

Suite : `P17-M002 - Action Fusion export_printables` est ready. Elle doit s'arreter sur gate technique si l'API Fusion ne permet pas un export fiable par module.
