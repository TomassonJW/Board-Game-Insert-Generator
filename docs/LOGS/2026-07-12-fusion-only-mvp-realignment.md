# 2026-07-12 - Realignement integral Fusion-only

## Decision

Thomas confirme que BGIG est un module Fusion 360. Le MVP ne comporte aucune
application web locale externe.

## Changements de pilotage

- ADR-0055 supersede ADR-0040/0041/0042 pour le MVP.
- La palette embarquee devient la surface principale.
- Le coeur Python reste pur et la scene Fusion reste une projection.
- P56-P60 sont redefinis pour un parcours integral dans Fusion.
- La branche codex/p56-premium-editor f669b82 est abandonnee et non integree.

## Frontieres

- Aucun localhost, Vite ou navigateur dans le runtime MVP.
- CommandInputs reste expert/secours.
- frontend et local_composer restent historiques jusqu a un lot de retrait.
- P55 reste valide pour son contrat pur.

## Validation

Tests documentaires Fusion-only, suite Python, tests Fusion hors API et
git diff --check avant integration.
