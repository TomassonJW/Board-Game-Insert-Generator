# P64-L09U-R3 — preuve corrective 0.1.74

Date : 2026-07-28.

Statut : `automated-validated`, `ready-human-gate`,
`fusion-validated=false`, `print-validated=false`.

## Résultat

- La profondeur calibrée reste identique du minimum au plan final, à
  l'aperçu, au CAD IR et au plan Fusion.
- Le cas générique `10 mm + 0,6 mm` reste à `10,6 mm` après finalisation.
- X/Y, orientation, identité et dimensions restent figés ; seule l'origine Z
  finale est résolue.
- Sans réservation recouvrante, la cavité est ouverte sur sa face fonctionnelle
  finale et le surplus reste sous la cavité.
- Sous une réservation locale, la cavité garde sa profondeur et se place sous
  la coupe avec la paroi et le fond canoniques.
- Les réservations sont découpées en régions XY exactes. Les zones disjointes
  ne cumulent pas leur épaisseur ; les recouvrements produisent uniquement les
  paliers locaux nécessaires.
- Le temps affiché sépare désormais recherche, plafond mural, terminaison et
  temps mural total. Une terminaison après 20 s n'est plus présentée comme une
  recherche « 24 s sur 20 s max ».
- Le corps BRep transitoire, le rendu entre modules, le rollback global et
  l'absence de Combine rectangulaire sont préservés.

La fermeture interne conserve une enveloppe conservatrice bornée déjà éprouvée.
Cette enveloppe ne définit aucune coupe de sortie : les prismes finaux, les
ancrages, l'aperçu, le CAD IR et Fusion sont reconstruits et certifiés depuis
les régions locales exactes.

## Preuves automatisées

Tests ciblés du préparateur : `126/126`.

Suite globale autorisée :

```text
BGIG_AUTHORIZED_SUITE modules=114 excluded=12
Ran 895 tests in 380.146s
OK (skipped=1)
```

Les douze modules benchmark/holdout/corpus/tournoi ont été exclus. Le test
ignoré est l'intégration SCIP native indisponible dans cet environnement.

Preflight :

```text
P64_L09UW_PREFLIGHT_OK
version=0.1.74
digest=d82666f86d494dec81118d922a118faec18064d93f0511f27c8d04567d284f30
join_batches=1/19
cut_batches=1/5
```

Le préparateur complet passe en mode sec.

## Replays personnels en lecture seule

```text
P64_L09T_LOCAL_REPLAY status=passed cases=3 read_only=true
```

- `CasLimite01+` : calcul `4448,213 ms`, finalisation `19132,902 ms` ;
- `CasLimite01++` : calcul `5421,914 ms`, finalisation `19120,087 ms` ;
- `CasLimite02+` : calcul `8926,211 ms`, finalisation `853,816 ms`.

Pour les trois cas, les profondeurs calibrées restent inchangées et le plan
Fusion est construit. Les temps sont des observations locales, pas des
benchmarks.

SHA-256 avant et après :

- `CasLimite01+` :
  `998ce73153cf5657f2653222e6cc57f6598b5ddefd0b11b2f57b0db8ff831090` ;
- `CasLimite01++` :
  `7ccac58e6304ae38bfbee38b9aee9f78fa05919e1ce72bed2efacdbaa95181bb` ;
- `CasLimite02+` :
  `53c1f607b033378b3a6228a49b9815fa1e663ccc9effa31021cbe55981175fe2`.

Les valeurs avant et après sont identiques. Aucun projet personnel n'est
modifié ni versionné.

## Limites

- La géométrie n'est pas encore observée dans Fusion 360 :
  `fusion-validated=false`.
- Aucune impression réelle n'est effectuée :
  `print-validated=false`.
- Les jobs annulables, miniatures de variantes et l'épaisseur distincte de
  séparateur restent hors R3.

Prochaine action unique :
`docs/P64_L09U_R3_V_0174_FUSION_GATE_RECIPE.md`.
