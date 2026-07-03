# Log - Autonomous Git Integration Policy

Date : 2026-07-03

## Decision

La validation humaine autorise Codex a gerer automatiquement les operations Git
normales apres chaque mission reussie.

## Portee autorisee

- creation de branche de mission ;
- commit ;
- fetch/pull/rebase simple ;
- push ;
- PR et merge automatique si les regles GitHub le permettent ;
- push fast-forward vers `main` si autorise ;
- nettoyage raisonnable de branche integree ;
- reprise depuis une branche propre basee sur `origin/main`.

## Conditions

L'integration automatique exige un workspace propre, des tests pertinents OK,
`git diff --check` OK et aucune gate humaine produit ou infrastructure.

## Arrets

Codex s'arrete sur vraie gate produit, echec test non reparable, conflit Git,
protection de branche, authentification indisponible, review humaine obligatoire
ou risque de perte de travail.