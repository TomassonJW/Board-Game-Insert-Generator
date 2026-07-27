# ADR-0096 — Sélection explicite des agencements locaux certifiés

## Statut

Proposée après l'analyse contrôlée de `CasLimite01++` le 2026-07-27.

Cette ADR étend ADR-0073 sans modifier le runtime de 0.1.72.

## Contexte

La palette calcule déjà des variantes locales certifiées et affiche des cartes
Compact, Équilibré et autres représentants. Elle ne montre pas leur géométrie
et la liste visible ne limite volontairement pas la frontière moteur.

Sur `CasLimite01++`, `18` variantes locales sont générées et `7` retenues. La
recherche globale atteint ses plafonds. En mémoire seulement, l'autorisation du
seul agencement canonique du conteneur 001 trouve un plan complet en environ
`15,8 s`.

Le besoin n'est donc pas de prétendre deviner automatiquement le meilleur
agencement. Il est de permettre à l'utilisateur d'apporter une contrainte
géométrique locale explicite.

## Décision proposée

### 1. Aperçu instantané

Chaque variante certifiée expose son `cavity_layout` déjà calculé sous forme
d'une miniature SVG vue du dessus :

- contour extérieur ;
- cavités et leur orientation ;
- nom court ou couleur par élément ;
- dimensions principales ;
- badges Compact, Équilibré ou autre représentant non dominé.

Aucun solve global ni appel Fusion n'est déclenché pour dessiner la miniature.

### 2. Sélection

L'utilisateur peut cocher une ou plusieurs variantes pour un conteneur.

- aucune case cochée : comportement automatique actuel, toute la frontière
  moteur certifiée reste admissible ;
- une ou plusieurs cases cochées : la sélection devient une allowlist dure pour
  ce conteneur ;
- « Réinitialiser » retire la contrainte et restaure le mode automatique ;
- « Voir toutes les variantes » expose la frontière certifiée complète.

La shortlist visuelle par défaut ne limite jamais silencieusement le moteur.

### 3. Identité et invalidation

La contrainte persistée référence les digests géométriques stables, pas un
index d'affichage. L'identité de calcul inclut :

- digest du projet ;
- digest de la frontière locale ;
- digests autorisés triés par conteneur.

Toute modification qui invalide une variante retire la sélection orpheline,
rend le plan obsolète et exige un nouveau clic sur Calculer.

### 4. Certification

Le solveur global reçoit seulement les variantes autorisées pour les
conteneurs contraints. Il doit toujours certifier :

- dimensions et cavités ;
- appuis et stabilité ;
- réservation supérieure ;
- priorité plancher d'abord ;
- jeux et parois ;
- plan complet.

Une sélection sans plan dans le budget signifie
`no_solution_within_budget_under_user_layout_constraint`, jamais impossible.

## Migration

Les projets existants n'ont aucune sélection et conservent le comportement
automatique. La lecture ne réécrit pas le fichier.

## Alternatives refusées

- figer arbitrairement les trois cartes visibles ;
- transformer Compact ou Équilibré en score total opaque ;
- considérer la sélection locale comme preuve globale ;
- modifier ou déplacer une cavité après sélection ;
- calculer une miniature par matérialisation Fusion.
