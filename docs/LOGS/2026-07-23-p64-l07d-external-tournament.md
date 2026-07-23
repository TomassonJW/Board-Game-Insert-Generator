# 2026-07-23 — P64-L07D tournoi externe

## Mission

Comparer réellement quatre moteurs externes, sceller un choix avant holdout,
puis ouvrir le nouveau holdout une seule fois.

## Faits

- OR-Tools, HiGHS, SCIP et LAFF ont reçu le même modèle sol, les mêmes limites
  et le même certificat BGIG.
- Deux sources publiques et huit contrôles de méthode ont été vérifiés.
- Discovery : SCIP 8/8, HiGHS 8/8, LAFF 7/8, OR-Tools 3/8.
- Tuning retenu : LAFF 7/7, SCIP 6/7, HiGHS 5/7, OR-Tools 2/7.
- SCIP et LAFF restent benchmark-only pour leurs gates de redistribution.
- HiGHS a été scellé seul avant holdout dans le commit `acdee83`.
- Holdout : 5/7 cas représentables certifiés, 2/7 `bounded_unknown`, aucune
  sortie invalide.
- Aucun portefeuille ne bat HiGHS parmi les candidats produit.
- La baseline BGIG refuse honnêtement la contrainte d'interdiction de rotation ;
  le tournoi ne revendique donc pas encore un gain produit.

## Incident de rapport

Le calcul du holdout était terminé quand l'agrégateur a rencontré un temps
`null` sur une ligne `unsupported`. La reprise n'a relancé aucun moteur :
sept checkpoints externes et sept checkpoints BGIG ont été réutilisés. Aucun
candidat, réglage, routeur ou résultat n'a été changé.

## Validation

Tests externes 40/40, garde documentaire 2/2, alignement Fusion-only 6/6 et
suite complète 756/756 en 230,824 s.

## Décision

P64-L07D est terminée. HiGHS passe en L07E comme
`laboratory-winner-product-candidate`. L'intégration reste conditionnée aux
gates produit, licence, packaging, fallback et gain réel.

`fusion-validated: false`. `print-validated: false`.
