# ADR-0012 - Capability-driven product pilotage

## Statut

Accepte

## Date

2026-07-04

## Carte liee

- `P0-M009 - Realigner North Star, capabilities et roadmap volumetrique`

## Contexte

BGIG a progresse au-dela du generateur initial de trays rectangulaires : moteur
Python pur, layouts 2D, tolerances par faces, profils d'impression, CAD IR,
add-in Fusion, blanks Fusion valides manuellement, export CAD IR, cavites et
features ergonomiques abstraites.

La cible long terme est maintenant plus large : un generateur intelligent de
systemes volumetriques modulaires asset-first pour inserts de jeux de societe.
Le pilotage par simple prochaine mission ne suffit plus a proteger la trajectoire.

## Options

1. Garder seulement roadmap/backlog/NEXT_ACTIONS.
2. Ajouter une capability map sans changer la boucle d'autonomie.
3. Piloter les missions par North Star, Product Pillars, capabilities,
   milestones, epics, missions, gates et validations.

## Decision

Adopter le pilotage par capabilities.

Chaque mission significative doit maintenant identifier la capability servie, le
milestone vise, la gate eventuelle et la validation attendue. `docs/CAPABILITY_MAP.md`
devient le pont entre North Star, roadmap et backlog. Les statuts de capabilities
sont distincts des statuts de missions : une capability peut etre implementee
dans le coeur, transportee dans la CAD IR, validee dans Fusion ou seulement
prevue.

## Consequences

Effets positifs :

- Codex peut choisir les missions selon la trajectoire produit, pas seulement
  selon proximite technique.
- Les gates Fusion, impression, architecture et schema deviennent plus visibles.
- Les phases longues asset-first, volumetriques, solveur, composites et beta sont
  explicitement reliees a des capabilities.

Risques :

- Le pilotage ajoute une couche documentaire a maintenir.
- Les statuts peuvent devenir trompeurs s'ils ne sont pas relies a des preuves.
- Le backlog doit rester actionnable et ne pas devenir une carte decorative.

## Alternatives refusees

- Roadmap/backlog seuls : trop faible pour une cible produit volumetrique longue.
- Capability map informative seulement : insuffisant si l'autonomie ne l'utilise
  pas dans la selection de mission.
- Implementer directement le solveur 3D : hors scope, premature et non valide par
  gate.

## Suivi

- Maintenir `docs/CAPABILITY_MAP.md` apres chaque mission qui change une
  capability.
- Garder `docs/NEXT_ACTIONS.md` court et priorise.
- Ne pas debloquer les capabilities Fusion reelles sans gate humaine.
- Etendre les tests documentaires pour verifier les nouveaux documents de
  pilotage.