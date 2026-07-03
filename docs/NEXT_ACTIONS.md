# Next Actions

Derniere mise a jour : 2026-07-04

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Politique active - Integration Git autonome

Statut : `active`.

Le chemin standard est `direct-to-main` : une mission doit etre testee, commitee,
integree directement dans `main`, puis poussee vers `origin/main` avant selection
d'une mission suivante. Les pull requests sont reservees aux cas de repli :
protection GitHub, review imposee, conflit, divergence non triviale, risque
structurant, authentification absente ou refus de push direct.

## Gate humaine active

Statut : `blocked`.

Decision demandee : autoriser ou recadrer `P5-M004 - Ajouter encoches de doigts
et fonds arrondis`.

Contexte :

- `P5-M001` modele les cavites rectangulaires simples abstraites ;
- `P5-M002` specialise les clearances de logements `cards` et `sleeved_cards` ;
- `P5-M003` specialise les receptacles ouverts `tokens`, `dice` et `meeples` ;
- la gate P5 validee couvrait les cavites simples cote moteur/CAD IR ;
- `P5-M004` parle d'encoches de doigts et de fonds arrondis, ce qui peut sortir
  du simple volume rectangulaire et toucher aux features, fillets/conges ou a une
  future generation Fusion soustractive.

Options :

1. Autoriser uniquement des features abstraites CAD-agnostic sans Fusion et sans
   fillets reels.
2. Recadrer P5-M004 en simple documentation/specification ergonomique sans code.
3. Reporter P5-M004 et revenir a une autre mission moteur non gated.
4. Autoriser une etude Fusion/cuts/booleans, ce qui declenche une gate Fusion
   separee avant implementation.

Recommandation : option 1 ou 2. Garder les encoches/fonds arrondis abstraits tant
qu'aucune gate Fusion soustractive n'est explicitement validee.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.

## Mission ready

Aucune mission `ready` ne doit etre lancee tant que la gate P5-M004 n'est pas
tranchee ou qu'une autre mission explicitement non gated n'est pas selectionnee.

## Gate obligatoire suivante

Si la prochaine mission implique de creer reellement les cavites dans Fusion 360,
par sketch, extrusion cut, boolean ou toute operation geometrique Fusion
soustractive, Codex doit s'arreter avec un rapport de gate Fusion dedie.
