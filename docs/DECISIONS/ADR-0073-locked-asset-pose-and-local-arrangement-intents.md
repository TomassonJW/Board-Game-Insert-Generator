# ADR-0073 — Pose verrouillée et intentions locales de disposition

## Statut

Proposée dans P45-M001 ; décision humaine requise avant tout runtime.

## Date

2026-07-21

## Cartes liées

- `P45-M001 — Contrat de disposition des assets non-cartes`
- `P64-L01 — États, digests et invalidation incrémentale`
- `P64-L02 — Frontières locales et score explicable`
- `P46 — Acceptation V0.2`

## Contexte

Le runtime actuel dimensionne les assets non-cartes par piles et grilles
rectangulaires. P64-V2H03 sait maintenant choisir plusieurs enveloppes locales,
mais son producteur correctif ne porte aucune intention fonctionnelle P45.

Le besoin produit distingue trois choses souvent confondues : orienter
physiquement une pièce, répartir plusieurs occurrences dans un conteneur, puis
placer ce conteneur dans la boîte. Une recherche 3D libre ne doit pas renverser
une pièce en transformant X ou Y en Z. Inversement, figer une seule enveloppe
locale avant P64 reproduirait les culs-de-sac déjà observés.

Contraintes : cœur sans `adsk`, Fusion-only, compatibilité historique, aucune
valeur physique nouvelle, jeux externes globaux, P64 propriétaire du solveur
global et aucune scène automatique.

## Options

### Option A — Rotation automatique sur les trois axes

- Simplicité algorithmique apparente et davantage de combinaisons.
- Rejette l'intention utilisateur, peut renverser des pièces et mélange pose,
  géométrie locale et recherche globale.
- Maintenance et validation physique coûteuses.

### Option B — Un mode produit une enveloppe locale unique

- Contrôle utilisateur lisible et petit espace de recherche.
- Le meilleur choix local est figé avant la boîte ; les culs-de-sac de
  combinaison réapparaissent et P64-V2H03 perd sa raison d'être.

### Option C — Pose verrouillée, frontière locale sémantique, choix global P64

- La personne choisit la pose et une intention de disposition.
- P45 génère plusieurs candidats locaux certifiés dans cette intention.
- P64 sélectionne paresseusement variante, rotation XY globale et placement.
- Davantage de types et de tests, mais responsabilités isolables et évolutives.

## Décision

Proposer l'option C.

Les identifiants internes sont `auto_balanced_v1`, `linear_xy_v1` et
`vertical_stack_z_v1`. La pose résolue verrouille Z. Une permutation X/Y reste
possible autour de Z ; une permutation avec Z exige une action utilisateur de
pose. L'empilement vertical translate des occurrences et ne les réoriente pas.

Les candidats locaux adaptent le contrat d'ADR-0070 et sont tous certifiés
avant consommation. P64 ignore la sémantique métier, conserve ses budgets et
applique le certificat global. Aucun candidat n'est choisi définitivement sur
son seul score local.

Le schéma public ne change pas dans P45-M001. Une extension future sera additive
et préservera bit-à-bit l'absence d'intention explicite.

## Conséquences

### Positives

- aucune pièce n'est renversée silencieusement ;
- les modes utilisateur ont un effet moteur testable ;
- P45 et P64 restent séparés ;
- les variantes locales continuent à résoudre des culs-de-sac globaux ;
- l'analyse locale incrémentale d'ADR-0071 dispose d'une frontière stable.

### Négatives

- pose, intention et placement demandent trois identités/digests distincts ;
- les messages d'échec doivent expliquer pose, intention ou budget global ;
- la future migration de schéma et l'UX exigeront un lot séparé.

### Risques

- confusion « ligne/colonne » : mitigée par les libellés `En ligne` et `Empilé
  verticalement` ;
- score ergonomique fictif : interdit sans métrique et preuve ;
- explosion combinatoire : Pareto, caps P64 et progressive widening ;
- régression historique : candidat canonique et absence de champ inchangés.

## Alternatives refusées

- Option A : refuse le verrou Z et mélange les responsabilités.
- Option B : pré-sélection locale incompatible avec ADR-0070.
- Un top 3 moteur fixe : refusé ; trois éléments est seulement une limite UI.
- Un ratio géométrique universel : refusé ; il reste une métrique souple et
  explicable, jamais une contrainte physique.

## Suivi

- contrat normatif : `docs/P45_M001_NON_CARD_ASSET_ARRANGEMENT_CONTRACT.md` ;
- décision attendue : `P45-M001V` ;
- après acceptation, P64-L01 peut démarrer sans attendre les formes P45 ;
- tout runtime P45 exige migration additive, tests et gate Fusion distincte ;
- `fusion-validated: false`, `print-validated: false`.
