# 2026-07-29 — P64-L09U-R9-A diagnostic de performance

## Décision

R9-A est terminé. ADR-0106 ouvre R9-B.

## Faits

- Normal local fidèle : `23,408 s`, sans solution.
- Approfondi local fidèle : `92,968 s`, solution certifiée.
- Les deux projets, avec ou sans éléments plats, produisent le même payload
  SCIP `77182c19...900bc183`.
- Deux appels SCIP consomment environ `68,1 s`.
- Le témoin SCIP est rejeté par `MINIMAL_ENVELOPE_EXPANDED`.
- Le résultat humain provient du repli interne, digest
  `a3ef2f44...8817bc46`.
- La première lane interne seule conserve ce digest en `13,363 s`.
- La voie Normal à environ `4 s` change la disposition et n'est pas retenue.
- Les SHA des deux projets personnels sont inchangés.

## Suite

R9-B applique ADR-0106 : préfixe interne certifié, lot de complétions borné,
arrêt sur la première lane certifiée, déduplication locale exacte et SCIP
uniquement en repli.
