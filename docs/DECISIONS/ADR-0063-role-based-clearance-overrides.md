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

## Amendement P44-M009H01 - édition X/Y commune

Le retour humain du 2026-07-16 corrige la présentation acceptée initialement :
le parcours normal ne doit pas permettre de saisir X et Y séparément. Pour
chaque rôle, la palette expose un seul jeu horizontal X/Y et, lorsque le rôle le
prévoit, un jeu vertical Z distinct.

Le schéma additif et la résolution interne par axe sont conservés pour ne pas
détruire les projets 0.1.31 déjà enregistrés ni les imports historiques
anisotropes. Si X et Y diffèrent, la palette le signale sans les réécrire. La
première saisie dans le champ X/Y applique la même valeur aux deux axes. Cette
décision est une contrainte d’édition UI, pas une recalibration des jeux, une
migration de schéma ou un changement des formules physiques.

## Correctif P44-M009H02 - cohérence UI, sans changement de décision

L’observation Fusion 0.1.32 ne remet pas en cause la cascade acceptée. Elle
révèle deux défauts d’adaptation : les champs globaux historiques n’écrivaient
pas les defaults par rôle déjà présents, et l’UI pouvait lire une ancienne
valeur effective après un recalcul silencieux.

P44-M009H02 impose donc :

1. toute édition globale synchronise le scalaire compatible, le vecteur de rôle
   concerné et sa provenance `project_default` ;
2. toute carte affiche l’effectif du dernier projet dérivé pour son propre id ;
3. un override local reste prioritaire même inférieur ;
4. `max` s’applique seulement à l’interface d’une paire de voisins, sans mutation
   ni propagation vers leurs autres cartes.

Aucune formule, valeur par défaut, migration ou sémantique physique ne change.
