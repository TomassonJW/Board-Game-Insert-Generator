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

Statut : `validated_for_scope`.

Decision humaine du 2026-07-04 : poursuivre vers les premieres cavites simples
cote moteur Python pur, configuration, rapports et CAD IR.

Perimetre autorise :

- modele de cavite simple ;
- configuration JSON ;
- validation des dimensions, parois et fond ;
- specialisation de clearances pour `cards` et `sleeved_cards` ;
- rapports Markdown/JSON ;
- CAD IR avec operations abstraites de cavite ;
- export CAD IR compatible avec l'add-in existant.

Perimetre toujours bloque sans nouvelle gate :

- creation reelle de cavites dans Fusion ;
- extrusion cut, boolean soustractif ou sketch de coupe Fusion ;
- fillets/conges, couvercles, charnieres ;
- export STL/3MF ;
- validation d'impression reelle.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.

## Mission ready

### P5-M003 - Ajouter bacs a tokens, des et meeples

Statut : `ready`.

Objectif : specialiser les cavites simples pour les receptacles ouverts de
`tokens`, `dice` et `meeples`, en conservant le moteur Python pur et la CAD IR
abstraite.

Livrable attendu :

- regles de clearances fonctionnelles pour tokens, des et meeples ;
- validation des parois/fonds deja existante conservee ;
- exemple ou extension d'exemple ;
- rapports et CAD IR enrichis si necessaire ;
- aucune generation Fusion reelle.

Dependances : `P5-M002` done.

Verifications minimales : suite unitaire, exemples `simple_box`, `simple_tray` et
`simple_card_tray`, export CAD IR, `git diff --check`, absence de `adsk` dans le
coeur.

## Gate obligatoire suivante

Si la prochaine mission implique de creer reellement les cavites dans Fusion 360,
par sketch, extrusion cut, boolean ou toute operation geometrique Fusion
soustractive, Codex doit s'arreter avec un rapport de gate.
