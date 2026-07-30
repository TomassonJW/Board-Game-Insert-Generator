# 2026-07-30 — P64-L09W-D-N identité du produit sélectionné

- Diagnostic public `tuning-360` exécuté sans holdout.
- Quatre observations historiques : même placement et même route sélectionnée,
  compteurs de travail non retenu variables sous limite de temps.
- Cinq relectures exactes : cinq plans complets identiques.
- ADR-0109 acceptée.
- Ajout d'une identité stable du produit sélectionné, distincte du digest de
  trace complet.
- Aucun budget, algorithme, paramètre physique ou checkpoint historique modifié.
- Tests ciblés : `17/17`, OK.
- Suite complète : timeout gardé à `600 s`, aucun échec observé avant la borne,
  non qualifiée verte.
- Prochaine mission : panels permanents 12–16 et 48 cas, puis mesure de variance.
