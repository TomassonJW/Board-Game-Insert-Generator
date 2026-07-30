# 2026-07-30 — P64-L09W panels permanents de performance

- Panel sentinelle fixé à 16 cas : 8 `common`, 8 `stress`.
- Panel candidat fixé à 48 cas : 24 `common`, 24 `stress`.
- Les 16 sentinelles couvrent toutes les valeurs des sept axes publics.
- Les deux cas causaux et `tuning-360` sont obligatoires.
- Les 48 cas contiennent 16 résultats prêts, 13 bornés et 16 pertes cibles.
- Les panels sont emboîtés et ne sont pas des estimateurs de taux.
- Les 400 cas restent réservés aux changements globaux ou au candidat gelé.
- Holdout : aucune surface d'entrée, ouverture ou invocation.
- Plan reproduit bit à bit ; 5 tests ciblés passent.
