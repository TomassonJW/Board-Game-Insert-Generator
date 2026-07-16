# ADR-0064 - Jeux externes des conteneurs exclusivement globaux

## Statut

Acceptée le 2026-07-16 par décision produit explicite pendant la revue Fusion de P44-M009H02.

Cette ADR remplace uniquement la partie de l’ADR-0063 qui autorisait des overrides externes par conteneur. Les overrides par asset, plateau et livret restent acceptés.

## Cartes liées

- P44-M009H03 - Retrait des jeux externes par bac et refonte dense de Réglages
- P44-M009H03V - Vérification humaine Fusion du package 0.1.34
- P44-M007 - Reste bloquée jusqu’à P44-M009H03V

## Contexte

Les essais Fusion 0.1.32 puis 0.1.33 ont montré que l’édition d’un jeu externe sur une carte de conteneur n’est ni compréhensible ni utile dans le parcours produit. Les jeux entre conteneurs et entre conteneurs et boîte décrivent l’assemblage global du projet, alors que les jeux asset-cavité et plateau/livret-logement décrivent réellement un objet local.

Conserver des valeurs externes par bac ajoute une ambiguïté d’interface, une provenance difficile à expliquer et une règle de paire sans bénéfice produit établi.

## Options considérées

### A - Corriger encore les overrides externes par bac

Préserve l’ADR-0063 intégralement, mais conserve une complexité produit non justifiée et une UX difficile à expliquer.

### B - Politique globale, données historiques conservées mais inactives

Supprime l’édition et l’effet runtime des jeux externes par bac. Les anciennes données restent chargeables et roundtrippables sans migration destructive.

### C - Supprimer aussi les champs historiques du schéma

Simplifie le schéma immédiatement, mais détruit de l’information enregistrée et impose une migration prématurée.

## Décision

L’option B est retenue.

1. `layout.clearance_defaults_v1.container_between_mm` définit globalement le jeu entre tous les conteneurs : X/Y dans le plan, Z entre niveaux superposés.
2. `layout.clearance_defaults_v1.container_box_per_side_xy_mm` définit globalement le jeu X/Y, par côté, entre les conteneurs et la boîte.
3. `box.lid_clearance_mm` est présenté comme le jeu Z conteneur-boîte et reste la marge retirée de la hauteur de conception.
4. `container_groups[].clearance_overrides_v1` reste accepté, validé et sérialisé pour préserver les anciens projets, mais ne contribue plus à `clearance_effective_v1` ni aux solveurs.
5. Aucun contrôle de jeu externe n’apparaît dans une carte de conteneur.
6. `contents[].clearance_override_mm` et `flat_items[].clearance_override_mm` restent actifs, par objet, avec un champ X/Y commun et un champ Z distinct.
7. L’onglet Réglages expose un tableau global à deux colonnes X/Y et Z, avec trois lignes : jeu entre conteneurs, jeu conteneur-boîte et jeu élément-cavité par défaut.

## Compatibilité

Il n’y a aucune migration destructive. Un projet historique conserve ses valeurs `clearance_overrides_v1` au roundtrip, mais les effectifs externes de tous ses conteneurs sont recalculés depuis les defaults globaux du projet.

Les scalaires historiques restent synchronisés avec les vecteurs par rôle pour la compatibilité des anciens lecteurs. Les anciens overrides asset et plateau/livret continuent de fonctionner.

## Conséquences

Positives : comportement explicable, aucune propagation locale possible, interface plus dense, moins de bruit dans les cartes et mapping direct entre réglage et effet physique.

Coût : des données historiques par bac restent présentes mais inactives jusqu’à une éventuelle migration de schéma future explicitement décidée.

## Limites

Cette décision ne recalibre aucune valeur, ne change aucune tolérance par défaut, n’ajoute aucune scène automatique et ne constitue pas une validation d’impression.

`fusion-validated: false` jusqu’à P44-M009H03V. `print-validated: false`.