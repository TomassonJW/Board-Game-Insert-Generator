# ADR-0097 — Épaisseur minimale distincte des séparateurs d'assets

## Statut

Proposée après le retour produit du 2026-07-27.

La sémantique est cadrée, mais la valeur par défaut reste une gate physique
humaine. Cette ADR ne change pas le runtime de 0.1.72.

## Contexte

Le projet distingue aujourd'hui :

- l'épaisseur de paroi extérieure ;
- l'épaisseur du fond.

La même épaisseur de paroi sert aussi de minimum entre deux cavités d'assets.
Thomas demande un troisième réglage explicite pour contrôler séparément cette
matière intérieure.

## Décision proposée

Ajouter `asset_separator_thickness_mm`, présenté comme
« Séparateur d'éléments » dans les épaisseurs minimales.

Il signifie la bande minimale de matière imprimable entre deux cavités
appartenant à des éléments distincts d'un même conteneur.

Il ne remplace pas :

- `wall_thickness_mm` entre une cavité et l'extérieur du conteneur ;
- `floor_thickness_mm` sous une cavité ;
- les jeux fonctionnels autour d'un asset ;
- les jeux entre conteneurs ;
- la couture interne sans jeu d'une annexe composite et de son propriétaire.

## Propagation obligatoire

La valeur résolue doit appartenir :

- au schéma et à la migration ;
- aux defaults projet et éventuelles surcharges de conteneur ;
- aux digests et invalidations ;
- à la génération et certification des variantes locales ;
- aux enveloppes minimales ;
- au solveur global et à ses diagnostics ;
- au CAD IR, aux mesures et aux certificats ;
- à l'aperçu et à la palette Fusion.

Une variante est rejetée si la matière réelle entre deux cavités est inférieure
à la valeur résolue. Aucune cavité ne peut être réduite ou déplacée pour masquer
le rejet.

## Migration proposée

Pour un ancien projet sans ce champ :

- la valeur résolue hérite de l'épaisseur de paroi déjà résolue ;
- le fichier n'est pas réécrit à la lecture ;
- une sauvegarde explicite peut écrire le nouveau champ selon la version de
  schéma retenue.

Cette migration préserve exactement la géométrie historique et n'invente aucune
nouvelle valeur physique.

## Gate restante

Avant activation comme réglage autonome, Thomas doit accepter :

- la valeur par défaut des nouveaux projets ;
- la plage UI et le pas ;
- la possibilité ou non d'une surcharge par conteneur ;
- le protocole d'impression et de mesure.

## Alternatives refusées

- modifier silencieusement la valeur de paroi existante ;
- confondre séparateur imprimable et jeu fonctionnel ;
- utiliser une constante cachée ;
- changer la géométrie des anciens projets à la lecture ;
- revendiquer `print-validated` sans essai physique.
