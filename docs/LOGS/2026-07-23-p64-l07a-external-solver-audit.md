# 2026-07-23 — P64-L07A audit externe

## Mission

Auditer l'état de l'art externe avant tout téléchargement ou build coûteux,
vérifier les gates légales et techniques, puis retenir assez de familles pour
un vrai tournoi P64-L07.

## Résultat

- dix candidats audités depuis leurs sources officielles ;
- cinq candidats shortlistés : PackingSolver, LAFF, OR-Tools CP-SAT, SCIP et
  HiGHS ;
- cinq familles algorithmiques distinctes ;
- Choco, Chuffed et CBC conservés `benchmark-only` ;
- Timefold et py3dbp rejetés pour le tournoi L07 ;
- minimum de trois vrais concurrents externes satisfait avant L07B/C.

## Décisions et contraintes

- aucun candidat n'est préclassé ni adopté ;
- tout artefact doit être verrouillé par version et SHA-256 avant exécution ;
- PackingSolver sera construit sans CLP ni Knitro ;
- CBC ne peut pas entrer dans le produit sans gate humaine distincte sur
  l'EPL-2.0 ;
- toute contrainte non traduite sans perte produit `unsupported` ;
- toute sortie positive devra être recertifiée par BGIG ;
- aucun candidat ne prend en charge nativement les formes 3D arbitraires ;
  T2 à T4 restent hors scope.

## Preuves

- `docs/P64_L07A_EXTERNAL_SOLVER_AUDIT_EVIDENCE.md` ;
- `tests/fixtures/p64_l07a_external_solver_audit.v1.json` ;
- `tests/test_external_solver_audit.py` ;
- `tests/test_p64_l07a_evidence_document.py`.

## Validation

- audit ciblé : 5/5 tests, OK ;
- garde documentaire dédiée : 1/1, OK ;
- reconstruction portable du manifest : 9/9, OK ;
- suite complète canonique : 721/721 en 217,756 s, OK ;
- correction d'un défaut CRLF/LF du constructeur de manifest sous Windows ;
- aucun benchmark, build externe, runtime Fusion, CAD ou scène lancé ;
- fusion-validated: false ;
- print-validated: false.

## Suite

P64-L07B construit le manifest V2, ajoute au moins deux sources publiques
indépendantes, documente leur correspondance d'objectif et scelle un nouveau
holdout avant toute exécution externe.
