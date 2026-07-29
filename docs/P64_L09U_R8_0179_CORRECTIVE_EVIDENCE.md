# P64-L09U-R8 — preuve corrective 0.1.79

Date : 2026-07-29.

Statut courant : `automated-validated`, `installed-local`,
`ready-human-gate`,
`fusion-validated=false`, `print-validated=false`.

La candidate 0.1.78 reste `human-KO`, `do-not-run`. La candidate corrective
R8 est 0.1.79. Elle remplace le contrat de compensation positive R7 par le
pipeline décidé dans ADR-0105.

## Contrat livré

Le résultat matériel est :

```text
conteneurs finalisés sans éléments plats
moins
union des encastrements locaux des plateaux et livrets
```

La chaîne automatisée impose :

- `flat_positive_volume_mm3 = 0.0` ;
- `flat_positive_body_count = 0` ;
- `flat_positive_union_count = 0` ;
- `flat_positive_operation_count = 0` ;
- `new_printable_body_count_attributed_to_flat_items = 0` ;
- opérations plates uniquement `difference` ;
- digest positif inchangé avant et après les encastrements ;
- même identifiant et même intervalle `[bottom, top]` dans l’aperçu, la CAD IR,
  le plan Fusion et l’outil BRep ;
- profondeurs locales exactes `2 mm`, `4 mm` et `6 mm` dans le cas forcé ;
- grille produit `0,1 mm` distincte de l’epsilon numérique.

## Suite autorisée

Les douze modules suivants sont exclus avant import :

1. `test_anonymized_solver_case_corpus_builder`
2. `test_external_solver_benchmark_corpus`
3. `test_external_solver_tournament`
4. `test_external_solver_tournament_evidence`
5. `test_external_solver_tournament_runner`
6. `test_external_solver_tournament_selection`
7. `test_real_3d_solver_corpus`
8. `test_real_3d_solver_tournament`
9. `test_solver_benchmark_adapters`
10. `test_solver_benchmark_campaign`
11. `test_solver_benchmark_corpus`
12. `test_solver_case_corpus`

Aucun benchmark, holdout, corpus ou tournoi n’est exécuté.

Résultat global final :

```text
BGIG_AUTHORIZED_SUITE modules=118 excluded=12
Ran 945 tests in 650.355s
OK (skipped=1)
```

Le test ignoré est l’intégration SCIP native indisponible dans cet
environnement.

La première passe globale a correctement signalé trois sous-tests R7 qui
filtraient encore l’ancienne politique `localized_top_inset_v1`. Le produit
publiait bien la nouvelle politique soustractive. Le témoin a été aligné sur
`strictly_subtractive_flat_inset_v1` et renforcé par les compteurs positifs
nuls. La reproduction causale passe, puis les suites globales finales passent.

## Validation ciblée et préflight

Le préparateur à blanc passe :

- matrice ciblée : `153/153` ;
- `CasLimite02+` : replay lecture seule réussi ;
- `CasLimite02++` : replay lecture seule réussi ;
- installation AppData : simulée, aucune écriture ;
- préflight : `passed`.

Préflight :

```text
version=0.1.79
digest=ebd2d0b055397c280d6d6eaf1112f251700dec8ee16061a8c0feb218a2ff3f71
operations=2
flat_positive_volume_mm3=0.0
flat_positive_bodies=0
flat_positive_unions=0
new_printable_bodies=0
fusion-validated=false
print-validated=false
```

Douze constructions successives du préflight donnent le même digest
`ebd2d0b0...3f71`. Les observations temporelles et les artefacts de run
historiques R6 ne participent pas au hash R8 ; leurs contrats hérités restent
couverts.

Le digest CAD historique P66 est mis à jour de
`4213ef61...aad6` à `9614f170...844` parce que la CAD IR porte désormais le
plan soustractif et son certificat. Le plan produit, les valeurs physiques et
le digest source P66 ne changent pas.

## Projets personnels

Le préparateur contrôle les deux SHA avant et après chaque replay :

- `CasLimite02+` :
  `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` ;
- `CasLimite02++` :
  `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743`.

Les fichiers sont uniquement lus. Ils ne sont ni sauvegardés, ni normalisés en
place, ni copiés dans le dépôt.

## Installation

Le package du commit `8baaaa9` est installé et vérifié dans le dossier add-in
Fusion :

- manifeste installé : `0.1.79` ;
- marqueur installé : `8baaaa9` ;
- runtime embarqué et marqueurs strictement soustractifs : conformes ;
- réglages UI locaux : écrits ;
- préparateur réel : `153/153` tests ciblés ;
- deux replays personnels : réussis, SHA inchangés ;
- préflight installé : `ebd2d0b0...3f71`.

La candidate est `ready-human-gate`. Aucune observation Fusion réelle n’est
encore revendiquée.

Recette :
`docs/P64_L09U_R8_V_0179_FUSION_GATE_RECIPE.md`.
