# 2026-07-28 — P64-L09U-R8-A diagnostic soustractif

- 0.1.78 reste `human-KO`, `do-not-run`.
- Les deux projets personnels ont été rejoués en lecture seule et leurs SHA
  sont inchangés.
- Le journal Fusion confirme `175,613 s` cumulées avant la solution de
  `CasLimite02+`, puis `87,192 s` pour `CasLimite02++`.
- La première matière positive liée aux éléments plats apparaît dans la
  finalisation composite, lors du passage de `final_size_mm` à `cad_size_mm`.
- La CAD IR exacte reconnaît `125 019,76 mm³` ajoutés au-dessus des corps dits
  finaux, puis les annule seulement par égalité de volumes planifiés.
- Le plan Fusion déplace trois coupes du livret de `[63,8 ; 65,8]` à
  `[67,8 ; 69,8]`.
- La BRep laisse ainsi `31 209,20 mm³` du vide demandé non retiré.
- Le modèle retenu pour décision est : conteneurs finalisés d'abord, puis une
  passe uniquement soustractive partagée jusqu'à la BRep.
- R8-A est `done-diagnostic`; R8-B devient `ready`.
- Aucun code produit, benchmark, holdout, corpus, tournoi, package ou valeur
  physique n'a été modifié.
- `fusion-validated=false`, `print-validated=false`.

Preuve :
`docs/P64_L09U_R8_A_SUBTRACTIVE_PIPELINE_DIAGNOSTIC_EVIDENCE.md`.
