# 2026-07-23 — P64-L07E intégration HiGHS

## Mission

Fermer le Goal P64-L07 par la gate produit, le packaging hors ligne, le
fallback et l'intégration conditionnelle du gagnant.

## Résultat

HiGHS 1.15.1 passe la gate produit sur cinq régressions communes :

- même vérité fonctionnelle et même nombre de solutions certifiées ;
- deux gains de qualité, aucune perte ;
- fragmentation résiduelle 0 contre 5 sur les deux cas comparables ;
- temps observé 1,308987 s contre 4,077502 s.

HiGHS est intégré seul. OR-Tools ne gagne aucune famille distincte ; SCIP et
LAFF restent benchmark-only.

## Intégration

- CLI officiel Windows x86_64 MIT ;
- exécutable, DLL, archive, licences et avis verrouillés ;
- 11 307 594 octets ajoutés au paquet versionné ;
- dépendances PE inventoriées : Universal CRT et Visual C++ Runtime 14 déjà
  présents, aucun installateur BGIG ;
- un appel maximum par calcul ;
- sous-limites 0,75 s Rapide et 3 s Normal/Approfondi ;
- certificat BGIG obligatoire ;
- fallback interne sur toute absence, altération, erreur ou limite ;
- add-in porté à 0.1.60.

## Preuves

- ADR-0082 ;
- `docs/P64_L07E_HIGHS_PRODUCT_INTEGRATION_EVIDENCE.md` ;
- `tests/fixtures/p64_l07e_highs_product_gate.v1.json` ;
- sonde CLI : 3 contrôles, 8 régressions, aucune différence de statut ou de
  qualité ;
- tests produit HiGHS 5/5, preuves 2/2 et reprise nullable 2/2 ;
- gate du runtime final : 5 statuts conservés, 2 gains, 0 perte ;
- package staging 0.1.60 et vrai binaire : OK ;
- garde documentaire 2/2 et alignement Fusion-only 6/6 ;
- Ruff et compilation Python ciblés : OK ;
- suite complète 765/765 en 228,071 s.

## Limites

Le holdout n'est pas rouvert. La lane reste T0/T1, rectangulaire et sur un seul
niveau. Aucun gain dense 11 × 34, aucune forme complexe, aucune observation
Fusion et aucune impression ne sont revendiqués.
