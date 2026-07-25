# P64-L09R-C — Preuve de la finition séparée et non destructive

Date : 2026-07-25

Statut : `implemented-product`, `automated-validated`.

## Portée livrée

- La finition reste une action explicite distincte du calcul minimal. Le calcul ne lance jamais F01B/F02B.
- Son profil est indépendant du calcul et accepte les cinq niveaux Rapide, Court, Normal, Long et Approfondi, soit 3, 10, 20, 60 et 180 secondes.
- Une seule deadline totale commence à l'entrée du finaliseur. Préparation, reconstruction de l'incumbent, fermeture de base, réparation locale, certificat global et objectif secondaire partagent cette limite.
- Le plan minimal certifié est copié comme incumbent. Son digest d'artefact et son digest de valeur sont capturés avant toute finition.
- Un timeout ou un rejet ne publie aucun plan partiel. Le plan minimal reste courant, inchangé et sélectionnable pour la matérialisation.
- Un résultat devenu obsolète est `stale_or_cancelled`, n'entre pas dans le cache et ne remplace aucun artefact courant.
- Si la fermeture de base est certifiée avant la deadline mais que l'objectif secondaire l'épuise, la base certifiée est conservée comme résultat final sûr.
- Le cache de finition inclut le budget indépendant. Le pont palette accepte déjà `finishing_effort` ; son sélecteur visuel appartient à P64-L09R-D.

## Preuves fonctionnelles

- Calcul `quick` puis finition par défaut `normal` : les profils et budgets restent distincts.
- Finition `long` demandée par la palette : le plan final expose une deadline totale de 60 000 ms.
- Timeout Rapide avant le premier certificat : `no_solution_within_budget`, aucun plan final, digest minimal identique et matérialisation minimale toujours disponible.
- Modification de source pendant la finition : résultat rejeté comme stale, aucun plan partiel publié.
- Rejet du certificat final : le plan minimal reste bit à bit identique et sélectionnable.
- Plateau/réservation active : fermeture, réparation locale et certificat global restent actifs sans rappel global.

## Validation

- Tests ciblés session : 17/17 OK.
- Tests ciblés pont palette : 29/29 OK.
- Tests ciblés fermeture continue : 5/5 OK.
- Suite complète : 859/859 en 240,829 s ; un test natif ignoré sous Python 3.10.
- Compilation Python : `python -m compileall -q src fusion_addin tests` OK.
- `git diff --check` : OK.

## Limites et non-objectifs

- Les deux sélecteurs visibles et leurs durées adjacentes appartiennent à P64-L09R-D.
- L'exécution hors thread UI et la jauge temporaire appartiennent à P64-L09R-E.
- Aucun benchmark, package Fusion, réglage local, appel `adsk`, observation Fusion ou fait d'impression n'est produit.
- La gate humaine P64-L09R-V reste inactive jusqu'à l'intégration de D à F.