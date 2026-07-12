# ADR-0048 - Contrat projet utilisateur V0.1 et migration additive

## Statut

Accepte dans le cadre de l'objectif autonome V0.1 du 2026-07-12.

## Carte liee

- `P37 - Contrat projet V0.1 et migration`.

## Contexte

Le contrat `bgig.local_composer.v0` expose au Studio des candidats dimensionnes,
des layers et des reservations placees manuellement. Il ne permet pas de
representer directement le parcours canonique : pieces -> bac cible ->
plateaux/livrets -> remplissage. Le remplacer sans migration ferait perdre les
anciens projets et casserait le bridge P23/P31.

## Options

1. Etendre le draft P23 avec des champs V0.1 et conserver les candidats visibles.
2. Creer un contrat utilisateur V1 et jeter les projets P23.
3. Creer un contrat utilisateur V1, conserver P23 et fournir une migration pure.

## Decision

Retenir l'option 3.

`bgig.project.v1` devient le contrat utilisateur de reference. Il contient :

- boite et jeux explicites ;
- lignes de pieces normalisees avec forme, quantite et `container_group_id` ;
- groupes de bacs avec surcharges de paroi/fond ;
- plateaux/livrets quantifies ;
- remplissages creux, pleins ou separateurs ;
- options apparence/mecanisme conservees mais differees.

Le normaliseur accepte `bgig.local_composer.v0`, produit V1 sans muter l'entree
et conserve les donnees non encore reinterpretees dans `migration.legacy_snapshot`.
P37 n'essaie pas de generer une solution V1 : P39 devra d'abord calculer les
bacs, puis P41 le volume entier.

## Consequences

- L'UI P38 peut enfin parler en termes de boite, pieces, bacs et plateaux.
- Les anciens projets restent importables et auditables.
- Le moteur P20/P21 demeure temporairement branche sur P23 ; aucune promesse de
  solution automatique n'est faite avant P39.
- Les migrations sont purement locales, testables et sans dependance externe.

## Alternatives refusees

- Ajouter les champs V0.1 au draft P23 : conserverait les candidats comme centre
  mental du produit et prolongerait le jargon technique.
- Casser les projets existants : perte de travail inutile et absence de rollback.
- Exposer directement BoxFillPlan : ce contrat est un resultat moteur, pas une
  saisie utilisateur.

## Suivi

- P38 utilisera le projet V1 dans le Studio.
- P39 construira les bacs et logements depuis `contents` et `container_groups`.
- P40/P41 consommeront `flat_items` et `fill_elements`.
- Fusion reste une cible de sortie et ne consomme pas le projet V1 brut.
