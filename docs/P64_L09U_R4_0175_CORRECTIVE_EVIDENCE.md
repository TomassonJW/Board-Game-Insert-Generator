# P64-L09U-R4 — preuve corrective 0.1.75

Date : 2026-07-28.

Statut : `automated-validated`, `ready-human-gate`,
`fusion-validated=false`, `print-validated=false`.

## Résultat

- La paroi canonique n'est plus soustraite au Z de la cavité sous plateau.
- Le sommet d'une cavité sous coupe coïncide exactement avec le dessous de la
  coupe locale réelle portée par le même conteneur.
- `top_separation_mm` et `intermediate_material_thickness_mm` valent `0`.
- La profondeur calibrée, X/Y, l'orientation et les dimensions restent
  inchangés.
- Une empreinte globale de plateau ne déplace plus une cavité si son conteneur
  ne porte aucune coupe locale.
- Une telle cavité reste ouverte sur la face fonctionnelle locale de son corps
  composite, même si le sommet global du module est plus haut ailleurs.
- Le résultat, l'aperçu, la CAD IR et le plan Fusion portent les deux preuves :
  `direct_void_to_removable_top_inset` ou `open_functional_face`.
- La CAD IR et l'adaptateur Fusion refusent une matière intermédiaire
  réintroduite.
- Les paliers locaux, profondeurs, budgets, corps BRep transitoire, rollback,
  rendu progressif et absence de Combine rectangulaire restent inchangés.

## Tests automatisés

Préparateur sec :

```text
130 tests ciblés
OK
```

Suite globale autorisée :

```text
BGIG_AUTHORIZED_SUITE modules=114 excluded=12
Ran 899 tests in 458.177s
OK (skipped=1)
```

Les douze modules benchmark/holdout/corpus/tournoi ont été exclus. Le test
ignoré est l'intégration SCIP native indisponible dans cet environnement.

Preflight :

```text
P64_L09UW_PREFLIGHT_OK
version=0.1.75
digest=08e36a2bfb96e3a12b5091781bcac2e7cd28bd078010ba790daa52402321443f
join_batches=1/19
cut_batches=1/5
```

Le preflight extrait le certificat réel de la fixture et exige :

- au moins une cavité sous plateau ;
- une coupe locale réelle correspondante ;
- autant de vides directs que de cavités `below_top_inset` ;
- continuité certifiée ;
- séparation et matière intermédiaire nulles.

## Replays personnels en lecture seule

```text
P64_L09T_LOCAL_REPLAY status=passed cases=3 read_only=true
```

| Cas | Cavités sous coupe directe | Cavités ouvertes localement | Calcul observé | Finalisation observée |
| --- | ---: | ---: | ---: | ---: |
| `CasLimite01+` | 8 | 17 | 4 496,921 ms | 19 190,895 ms |
| `CasLimite01++` | 10 | 17 | 8 290,983 ms | 19 177,433 ms |
| `CasLimite02+` | 3 | 9 | 14 663,696 ms | 1 472,658 ms |

Ces temps sont des observations locales, pas des benchmarks.

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

- La géométrie 0.1.75 n'est pas encore observée dans Fusion 360 :
  `fusion-validated=false`.
- Aucune impression réelle n'est effectuée :
  `print-validated=false`.
- Les jobs annulables, miniatures et séparateurs distincts restent hors R4.

Prochaine action unique :
`docs/P64_L09U_R4_V_0175_FUSION_GATE_RECIPE.md`.
