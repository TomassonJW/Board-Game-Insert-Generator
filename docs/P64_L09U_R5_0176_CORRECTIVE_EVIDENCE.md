# P64-L09U-R5 — preuve corrective 0.1.76

Date : 2026-07-28.

Statut : `automated-validated`, `installed-local`, `ready-human-gate`,
`fusion-validated=false`, `print-validated=false`.

## Correction

- Une cavité partiellement recouverte conserve son ancrage Z calibré.
- Chaque région sous plateau rejoint le dessous exact de sa découpe.
- Chaque région hors plateau reçoit une coupe verticale jusqu'à son sommet
  fonctionnel local.
- Les coupes sont limitées à l'intersection XY entre cavité et prisme
  composite : aucune paroi voisine n'est retirée.
- Les accès verticaux sont soustraits après la cavité et avant les
  encastrements.
- La CAD IR et le plan Fusion transportent
  `frozen_cavity_vertical_access`.

## Preuves ciblées acquises

```text
tests.test_p64_l09u_r3_depth_local_insets
Ran 13 tests
OK
```

La matrice CAD/aperçu/Fusion voisine passe :

```text
Ran 35 tests
OK
```

Le cas automatisé partiel produit plusieurs accès locaux, tous contenus dans
l'empreinte de la cavité, avec le même nombre dans le certificat, la CAD IR et
le plan Fusion.

## Matrice ciblée et preflight

```text
133 tests ciblés
OK
P64_L09T_LOCAL_REPLAY status=passed cases=3 read_only=true
P64_L09UW_PREFLIGHT_OK
version=0.1.76
digest=1474bb27404252564212a4c11086fdb2e1c9e8c573285f74cef2082105206417
join_batches=1/19
cut_batches=1/5
```

Le préparateur a été exécuté en mode sec : aucune écriture AppData.

## Suite moteur autorisée

```text
BGIG_AUTHORIZED_SUITE modules=114 excluded=12
Ran 902 tests in 409.640s
OK (skipped=1)
```

Les douze modules benchmark/holdout/corpus/tournoi ont été exclus. Le test
ignoré est l'intégration SCIP native indisponible dans cet environnement.

## Replays personnels

Les trois projets personnels passent en lecture seule. Le script exige les
SHA-256 avant/après identiques et n'écrit aucun témoin.

## Intégration et installation

- Commit correctif initial : `07dcabf`.
- Intégration : fast-forward direct dans `origin/main`.
- Add-in 0.1.76 installé localement.
- Manifeste, runtime, réglages et marqueur de commit vérifiés.
- Reçus de preflight et replays écrits dans le dossier local de projets.

## Validation restante

- observation humaine Fusion R5-V.

Aucune validation Fusion ou impression n'est revendiquée.
