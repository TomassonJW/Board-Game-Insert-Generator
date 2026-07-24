# Journal P64-L08H — remédiation du paquet SCIP

Date : 2026-07-24

## Mission

Évaluer sans benchmark ni holdout le paquet produit SCIP 10.0.2 compatible
avec le Python 3.14 de Fusion, puis fermer la gate si une obligation de
redistribution reste inconnue.

## Résultat

Le wheel officiel PySCIPOpt 6.2.1 `cp314` est retenu face au CLI autonome afin
de conserver la route du worker L08F. Avec NumPy 2.5.1, il charge SCIP 10.0.2
et résout un contrôle binaire exact à l'optimal dans un Python 3.14 isolé,
hors ligne et sans installation globale.

La remédiation ABI passe, mais la gate produit reste négative. Le wheel ne
livre pas les avis des bibliothèques natives SCIP, Ipopt, MUMPS/METIS, Intel et
Microsoft ; les chaînes d'autorité Intel et Microsoft ne sont pas démontrées.
Aucun runtime n'est intégré et aucune gate Fusion n'est ouverte.

## Preuves

- `docs/P64_L08H_SCIP_PACKAGE_REMEDIATION_EVIDENCE.md` ;
- `tests/fixtures/p64_l08h_scip_package_remediation.v1.json` ;
- `scripts/solver/audit_scip_package_remediation.py` ;
- digest : `d2de2bea96200c614270ae60e5fdbe2736a398701eb424ec57c61706ba8c9440`.

## Suite

P64-L08I doit cadrer par ADR puis auditer un runtime SCIP 10.0.2 minimal
`cp314`, sans les composants non utilisés Ipopt/MUMPS/Intel, avant toute
intégration et toute gate Fusion.
