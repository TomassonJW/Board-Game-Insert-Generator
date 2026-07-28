# 2026-07-28 — P64-L09U-R4 cavités ouvertes sous plateaux

- 0.1.74 classée `human-KO`, `do-not-run`.
- Cause : une paroi canonique était ajoutée entre le dessous de l'encastrement
  et le sommet de la cavité.
- Décision ADR-0100 : le plateau amovible ferme la cavité ; aucune matière
  imprimée ne sépare leurs vides.
- Correction complémentaire : seule une coupe locale réelle du propriétaire
  peut abaisser la cavité. L'empreinte globale seule ne suffit pas.
- Les cavités sans coupe restent ouvertes sur leur face fonctionnelle locale.
- Candidate : 0.1.75.
- Validation : préparateur 130/130, suite autorisée 899/899, trois replays
  personnels en lecture seule avec SHA-256 inchangés.
- Prochaine action : gate humaine P64-L09U-R4-V.
- `fusion-validated=false`, `print-validated=false`.
