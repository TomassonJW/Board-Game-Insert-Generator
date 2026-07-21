# Next Actions

Dernière mise à jour : 2026-07-21

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` et
`print-validated: false`. P64-V2H03V et P44-V sont fermées dans Fusion 0.1.55.
La réserve de charge P44 à environ cinquante conteneurs reste explicitement non
observée et ne constitue aucune preuve de performance.

## Dernier état réel

- P64-V2H03B/C/V fournit la frontière locale, la sélection globale paresseuse,
  les certificats et la preuve Fusion des variantes internes ;
- le mécanisme dense 11 × 34 reste `no_solution_within_budget` et n'est déclaré
  ni soluble ni impossible ;
- P44-V est `done-human-gate` pour la fondation UX 0.1.55 ;
- ADR-0071/0072 décrivent la future boucle locale, le solve global explicite,
  la finalisation et la capacité réutilisable, sans runtime correspondant ;
- P45-M001 propose ADR-0073 et le contrat de disposition des assets non-cartes,
  sans code, schéma, UI ou géométrie nouvelle.

## Prochaine action recommandée

### P45-M001V — Décision sur la pose et les dispositions locales

Thomas doit accepter, corriger ou refuser ensemble :

1. la séparation entre pose physique, disposition locale et placement global ;
2. le verrou Z : aucune permutation X/Y vers Z sans action utilisateur ;
3. les intentions `Automatique`, `En ligne`, `Empilé verticalement` ;
4. l'absence de fallback silencieux entre intentions ;
5. la frontière locale certifiée P45 consommée sans interprétation par P64 ;
6. P64-L01 comme premier runtime suivant, sans UI ni formes P45.

Sources : `docs/P45_M001_NON_CARD_ASSET_ARRANGEMENT_CONTRACT.md` et ADR-0073.

Modèle conseillé pour cette décision : aucun agent n'est nécessaire si la
proposition est acceptée telle quelle. En cas de correction architecturale,
`gpt-5.6-sol` avec raisonnement `xhigh` reste optimal. `gpt-5.6-terra` en
raisonnement `high` convient à une correction éditoriale sans changement de
frontière.

## Lots suivants, non ouverts

1. P64-L01 après acceptation P45-M001V ;
2. P64-L02 puis P64-L03/L03V selon ADR-0071 ;
3. futur runtime P45 par contrat et migration additive distincts ;
4. P46 seulement après formes et ergonomie réellement matérialisées ;
5. P64-F01/F02, C01-C03 et F03 selon leurs dépendances ;
6. P47-P50 restent bloqués par P46, P69 par P50.

## Séquence verrouillée

Une seule décision est active : P45-M001V. Aucun code P45 ou P64-L01 ne commence
avant son retour. P45 ne possède pas le solveur global ; P64 ne définit pas les
poses, intentions ou formes. Les jeux externes restent globaux, les valeurs
physiques inchangées et aucune scène n'est créée automatiquement.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans main seulement lorsqu'aucune gate humaine n'est
ouverte. Une gate Fusion ne vaut jamais impression.
