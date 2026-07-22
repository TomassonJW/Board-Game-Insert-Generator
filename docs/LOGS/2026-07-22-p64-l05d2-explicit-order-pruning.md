# Journal P64-L05D2 - elagage sous ordre explicite

Date : 2026-07-22.

## Mission

Utiliser la gate L05D1 pour conserver une premiere optimisation interne
seulement si elle ne regresse aucun fait fonctionnel.

## Changement

Lorsque l'ordre des participants est explicite, son index est la premiere cle de
tri. Apres le quota de participants non vides, les suivants ne peuvent plus etre
retenus. Leur evaluation est maintenant omise. La voie heuristique sans ordre
reste inchangee.

## Mesures

Sur sept cas et trois repetitions :

- 0 regression fonctionnelle ;
- 57 329 -> 31 901 essais de placement ;
- 2 581 -> 3 333 etats explores sous les memes caps ;
- temps median cumule +2,883 %, dans la tolerance mais sans revendication de
  gain global de vitesse.

Le projet personnel reste sans completion geometrique. Son SHA-256 est identique
avant et apres le replay en lecture seule.

## Decision

Conserver l'optimisation : elle supprime 44,355 % d'essais inutiles sur le
corpus et permet aux lanes bornees de depenser ce budget sur des branches
selectionnables. Elle n'est pas presentee comme resolution du cas humain.

Aucune ADR nouvelle : la gate et ses criteres sont ceux de l'ADR-0079.
