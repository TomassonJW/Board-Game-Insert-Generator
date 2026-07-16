# ADR-0063 - Jeux par role avec héritage et overrides par objet

## Statut

Acceptée le 2026-07-16 après la gate humaine P44-M008. L’option B est la décision applicable.

## Carte liee

- P44-M008 - Contrat de jeux hérités et overrides par objet
- P44-M009 - Implementation après gate humaine

## Contexte

P44 doit offrir des jeux par objet sans confondre la cavité, l encastrement
superieur et l espace externe des corps. Les scalaires historiques emploient
deja des sémantiques par côté, total et unidirectionnelle.

## Options

### A - Un champ universel

Simple en apparence mais ambigu et incompatible avec les sémantiques existantes.

### B - Trois roles, héritage par axe et vecteurs additifs

Chaque valeur effective est explicable. Les conteneurs gardent deux
sous-vecteurs : perimetre boîte par côté et voisinage total.

### C - Conserver les scalaires et des exceptions UI

Cout court terme faible, dette forte et zéro ambigu.

## Décision

L option B est acceptée. Null signifie héritage, zéro est explicite.
Les formules preservent les règles P65 et la paire de conteneurs utilise max,
jamais une somme. Les valeurs historiques sont projetees sans recalibration.

Cette ADR ne devient acceptee qu après la gate humaine des formules, defaults et
migration. Elle n autorise aucun changement runtime dans P44-M008.

## Consequences

Positives : valeurs auditables, compatibilite historique, UI compacte mais
experte, base propre pour P68.

Risques : schema conteneur plus riche, regression si implementation prematuree,
aucune valeur print-validated.

## Alternatives refusees

A melange des objets physiques differents. C ne satisfait pas l override
partiel ni la provenance par axe.

## Suivi

P44-M009 implémente le schéma, loader, cœur, palette, rapports, CAD IR et tests. P44-M007 est la prochaine mission sur GO explicite.
