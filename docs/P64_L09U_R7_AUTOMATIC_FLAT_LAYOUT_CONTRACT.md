# P64-L09U-R7 — contrat de disposition automatique des éléments plats

## Entrées

- boîte intérieure et hauteur utile ;
- réglages canoniques de paroi, fond et jeux ;
- éléments plats avec dimensions, quantité et rotation ;
- corps/cavités minimaux puis finaux certifiés ;
- grille produit `0,1 mm`.

Le futur mode manuel est hors de ce contrat.

## Sortie minimale

Chaque élément plat publie :

- empreinte orientée et pose XY en ticks ;
- ordre source et ordre automatique effectif ;
- position dans la pile et intervalles Z locaux ;
- score détaillé ;
- enveloppes de paroi attendues ;
- certificat de pose minimale ;
- statut de migration éventuel.

## Faisabilité

Une pose automatique est admissible seulement si :

1. chaque bord d'empreinte conserve la paroi minimale au bord de boîte ;
2. chaque séparation positive entre zones/cavités conserve son minimum ;
3. aucun fragment de matière final n'est positif et inférieur au minimum ;
4. chaque intersection de coupe utile avec un corps est assez large pour être
   matérialisée sans micro-encoche ;
5. fonds et cavités figées restent conformes ;
6. aucun corps artificiel n'est requis ;
7. toutes les coordonnées et dimensions dérivées sont sur la grille.

## Classement

Les candidats faisables sont comparés, dans l'ordre :

1. couverture intérieure utile maximale ;
2. recouvrement sain de pile maximal ;
3. marge minimale de matière maximale ;
4. centrage sur la couverture utile ;
5. centrage de boîte ;
6. signature stable.

## Ordre vertical

Après rotation, le bas-vers-haut suit :

```text
aire orientée
-> plus grand côté
-> plus petit côté
-> ancien stack_order seulement à empreinte égale
-> identifiant stable
```

Un petit élément est toujours sous un grand élément dans le mode automatique.

Une contradiction de l'ancien `stack_order` est signalée et normalisée dans
l'artefact dérivé, sans réécriture du projet.

## Recertification finale

La finalisation reçoit la pose minimale exacte et reconstruit les corps finaux :

- pose toujours valide : elle est conservée ;
- pose invalide : le plan est refusé avec la première divergence ;
- aucun autre cas : aucun déplacement silencieux.

Les coupes finales doivent rester soustractives, dans l'enveloppe du corps
cible et sans dimension XY positive inférieure à la paroi minimale, sauf
continuité de vide explicitement certifiée.

## Propagation

Le résultat, l'aperçu, la CAD IR et le plan Fusion doivent partager :

- identifiants d'élément/région ;
- pose XY ;
- ordre effectif ;
- intervalles Z ;
- dimensions en ticks ;
- digest de grille ;
- nombre de micro-fragments : `0` ;
- volume additif hors enveloppe finale : `0`.

## Compatibilité

- projets historiques lus sans écriture ;
- dérivations antérieures invalidées ;
- `origin_mm` manuel historique toujours ignoré dans le mode automatique ;
- futur mode manuel réservé à une politique explicite et à une gate distincte.
