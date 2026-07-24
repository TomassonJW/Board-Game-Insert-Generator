# 2026-07-24 — P64-L08G, gate produit SCIP

## Mission

Auditer le runtime Windows SCIP/PySCIPOpt déjà acquis, intégrer SCIP seul et
préparer Fusion uniquement si toutes les dépendances, licences, compatibilités
et non-régressions sont prouvées.

## Exécution

- deux wheels verrouillés : PySCIPOpt 6.2.1 et NumPy 2.2.6 ;
- 61 194 406 octets compressés, 187 848 352 octets décompressés ;
- dix DLL et tous les avis présents inventoriés par chemin, taille et SHA-256 ;
- Fusion 2704.1.36 et `python314.dll` observés et verrouillés ;
- sources officielles SCIP, Ipopt, MUMPS, Intel et Microsoft vérifiées ;
- aucun solveur, corpus ou holdout exécuté.

## Verdict

La gate échoue avant intégration :

- PySCIPOpt acquis : `cp310` ; Fusion courant : `cp314` ;
- versions exactes natives incomplètes ;
- avis tiers incomplets ;
- autorité de redistribution des binaires précis incomplète.

Décision : `negative_no_product_integrable_winner`. SCIP reste le gagnant du
benchmark L08F ; aucun concurrent n'est substitué après lecture du holdout.
Aucun runtime, package ou réglage produit ne change. Aucune gate Fusion n'est
préparée ou installée.

## Preuves

- `scripts/solver/audit_scip_product_gate.py` ;
- `tests/fixtures/p64_l08g_scip_product_gate.v1.json` ;
- `tests/test_scip_product_gate_evidence.py` ;
- `docs/P64_L08G_SCIP_PRODUCT_GATE_EVIDENCE.md` ;
- digest L08G :
  `a8ddb80e48ba83f9e3869f0bd3fffc7447be997b2c5932daf781775a7cbcc09a`.

## Validation

- preuve L08G : 4/4 ;
- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- Ruff et compilation Python ciblés : OK ;
- suite complète : 797/797 en 270,144 s sous garde Windows, code 0.
## Suite

P64-L08H peut auditer un runtime SCIP `cp314` ou CLI autonome sans rouvrir le
benchmark. Toute intégration future exigera ensuite une ADR, des régressions
ouvertes sans perte et seulement alors une préparation Fusion humaine.

`fusion-validated=false`. `print-validated=false`.
