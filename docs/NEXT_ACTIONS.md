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

Decision demandee : autoriser, reporter ou recadrer la premiere generation Fusion
reelle des cavites et features abstraites P5.

Contexte :

- `P5-M001` modele les cavites rectangulaires simples abstraites ;
- `P5-M002` specialise les clearances de logements `cards` et `sleeved_cards` ;
- `P5-M003` specialise les receptacles ouverts `tokens`, `dice` et `meeples` ;
- `P5-M004` decrit les encoches de doigts, encoches laterales/centrales,
  demi-lunes, fonds arrondis et aides de prise en main comme features abstraites
  CAD-agnostic ;
- les rapports Markdown/JSON et la CAD IR exposent `subtract_rectangular_cavity`
  et `describe_cavity_feature` avec `fusion_generation: not_implemented` ;
- l'add-in Fusion actuel doit rester limite aux blanks rectangulaires tant qu'une
  nouvelle gate n'autorise pas les operations soustractives ou courbes reelles.

Options :

1. Autoriser une mission Fusion limitee aux cavites rectangulaires simples par
   sketch + extrusion cut/boolean, sans encoche ni fond arrondi.
2. Autoriser une mission d'etude/ADR Fusion sur la strategie de cuts, booleans,
   fillets et geometry robustness, sans generation executable.
3. Reporter la generation Fusion reelle et poursuivre une mission moteur non
   gated.
4. Autoriser directement encoches/fonds arrondis reels dans Fusion : option plus
   risquee, a cadrer fortement avant implementation.

Recommandation : option 1 ou 2. Commencer par la generation Fusion reelle de
cavites rectangulaires simples, ou par une ADR technique si le choix cut/boolean
reste incertain. Ne pas commencer par les demi-lunes ou fonds arrondis reels tant
que les cuts rectangulaires ne sont pas stables.

Validation attendue de l'humain :

- perimetre Fusion autorise ;
- types d'operations CAD autorisees ;
- limites explicites sur encoches, fonds arrondis, fillets et booleans ;
- procedure de smoke test manuel attendue dans Fusion 360.

## Mission ready

Aucune mission `ready` ne doit etre lancee tant que la gate Fusion reelle de
cavites/features n'est pas tranchee ou qu'une autre mission explicitement non
gated n'est pas selectionnee.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
