# Journal — P64-L08J runtime SCIP minimal

Date : 2026-07-24

## Mission

Construire depuis les entrées L08I un runtime SCIP 10.0.2 minimal pour Python
3.14, inventorier ses dépendances et vérifier son équivalence publique sans lire
ni rejouer le holdout L08F.

## Réalisation

- build local SoPlex 8.0.2, SCIP 10.0.2 et PySCIPOpt 6.2.1 `cp314` ;
- runtime de 56 491 565 octets, soit 69,65 % de moins que le candidat L08H ;
- 26 binaires inventoriés, zéro dépendance non résolue et zéro famille interdite ;
- quatre fichiers Microsoft identiques aux sources officielles `VC/Redist` ;
- avis PySCIPOpt, SCIP, SoPlex, NumPy et Microsoft réunis ;
- probe exact et six contrôles publics 3D passés ;
- reconstruction indépendante depuis une racine vide et seconde qualification ;
- aucun tuning, aucune installation globale, aucune lecture du holdout et aucune
  modification du runtime produit.

## Verdict

`minimal_scip_runtime_build_and_public_equivalence_pass`.

P64-L08K est autorisée pour intégrer un build qualifié précis dans BGIG, lancer
les régressions complètes puis préparer une gate Fusion seulement si elles sont
vertes. Les différences binaires non fonctionnelles entre deux compilations MSVC
sont conservées explicitement ; le paquet produit devra verrouiller le build
réellement intégré.

`fusion-validated=false` et `print-validated=false`.
