# 2026-07-29 — candidate P64-L09U-R8 0.1.79 préparée

La candidate 0.1.79 possède un préflight et un préparateur distincts de la
candidate 0.1.78 rejetée.

Le préparateur à blanc passe `151/151` tests ciblés et rejoue
`CasLimite02+` puis `CasLimite02++` en lecture seule. Les SHA attendus sont
contrôlés avant et après chaque replay.

Le préflight `5c251f13...ac55a` certifie de bout en bout :

- zéro volume, corps, union, opération positive ou nouveau corps imprimable
  lié aux éléments plats ;
- opérations `difference` seulement ;
- plan CAD, certificat Fusion et intervalles BRep identiques.

La suite globale autorisée et l’installation locale restent à exécuter avant
l’ouverture de la gate humaine.

`fusion-validated=false`, `print-validated=false`.
