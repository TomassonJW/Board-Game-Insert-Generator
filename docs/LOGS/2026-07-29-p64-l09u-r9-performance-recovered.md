# 2026-07-29 — P64-L09U-R9 performance récupérée

P64-L09U-R9-A à R9-C sont terminées et intégrées.

Le coût dominant venait de deux passages SCIP identiques avant le repli interne
qui produisait réellement le placement humainement accepté. ADR-0106 retient
la première voie interne Approfondie exacte avant SCIP, puis le premier groupe
géométrique entièrement certifié comme autorité. SCIP reste disponible en
repli si aucune solution interne certifiée n’est trouvée.

Résultat :

- placement autoritaire `a3ef2f44...8817bc46` conservé ;
- calculs de bout en bout à `3,727 s` et `3,911 s` ;
- finalisations à `2,654 s` et `2,500 s` ;
- replays du préparateur à `4,403 s` et `4,400 s` ;
- SHA des deux projets personnels inchangés ;
- pipeline soustractif, profondeur, cavités, parois, grille, epsilon et budgets
  inchangés ;
- suite autorisée : `953` tests passés, `1` skip prévu ;
- préparateur 0.1.80 en mode sec : `174` tests ciblés, `1` skip prévu.

La candidate 0.1.80, son préflight et sa recette humaine sont prêts à installer.
`fusion-validated=false`, `print-validated=false`.
