# P60 - Correctif bridge QT de la palette

## Retour humain

L UI est jugee impeccable, mais les actions projet ne chargent pas le projet,
expirent apres 8 secondes et produisent `Action inconnue`. Effacer la scene et
les reglages experts restent actifs car ils utilisent des actions directes.

## Cause

Le navigateur QT renvoie chaque `sendInfoToHTML` comme action entrante
`response`. Le handler repondait a cet accuse par une nouvelle notification,
entretenant la boucle.

## Correctif

- ignorer `response` avant tout routage ou envoi ;
- acquitter les commandes HTML avec `returnData = OK` ;
- taille palette initiale/minimale 1120 x 760 ;
- add-in 0.1.7 ;
- tests de transport et de dimensions.

## Validation restante

Recharger l add-in dans Fusion et rejouer P60. Aucune validation d impression.