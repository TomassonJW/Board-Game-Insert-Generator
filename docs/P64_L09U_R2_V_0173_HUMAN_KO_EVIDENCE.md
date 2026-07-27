# P64-L09U-R2-V — preuve humaine KO 0.1.73

## Verdict

Verdict de Thomas le 2026-07-28 :

```text
P64-L09U-R2-V Fusion KO 0.1.73
```

Le verdict est `human-KO`, `do-not-run` pour une utilisation finale ou une
impression. Il ne retire pas les gains humains confirmés sur le nouveau chemin
de matérialisation.

`fusion-validated=false`, `print-validated=false`.

## Acquis humains confirmés

### CasLimite01+

- calcul en effort Normal : environ `4 s` ;
- finalisation : environ `18 s` ;
- matérialisation : quelques secondes ;
- les conteneurs apparaissent progressivement dans Fusion ;
- Fusion reste réactive ;
- la scène finale correspond à l'aperçu ;
- aucune erreur `ALL_TOOL_BODY_REFERENCE_LOST` observée ;
- un ajout local non sauvegardé a encore calculé en environ `4,5 s`, finalisé
  en environ `17 s`, puis été matérialisé correctement.

### CasLimite02+

- calcul en quelques secondes ;
- finalisation observée à environ `866 ms` ;
- matérialisation presque immédiate et progressive ;
- aucun retour aux longues attentes de 0.1.70 à 0.1.72.

### CasLimite01++

- calcul presque instantané ;
- répartition visuellement propre ;
- la correction du support tardif est confirmée utile.

Ces observations valident humainement le principe du corps BRep transitoire,
la respiration entre modules et la fidélité générale aperçu/scène. Elles ne
valident pas encore la géométrie fonctionnelle finale.

## Défaut bloquant 1 — profondeur des cavités après finalisation

Le plan minimal conserve une profondeur cohérente. Après `Finaliser`, les corps
gagnent de la hauteur mais les cavités deviennent beaucoup trop profondes.

Mesure humaine explicite sur le conteneur anonymisé 001 :

- hauteur d'asset : `10 mm` ;
- jeu Z configuré : `0,6 mm` ;
- profondeur calibrée attendue : `10,6 mm` ;
- profondeur mesurée après finalisation : `18,2 mm`.

Le comportement attendu est :

- la profondeur calibrée reste exactement dérivée de l'asset et de son jeu Z ;
- la finalisation peut épaissir le fond apparent ou déplacer verticalement la
  cavité dans le corps final ;
- elle ne peut pas allonger la cavité pour rejoindre la face supérieure ;
- sous une réservation supérieure, la cavité descend sous la découpe locale
  tout en conservant sa profondeur et la paroi minimale canonique ;
- hors réservation supérieure, elle reste correctement ancrée par rapport à
  la face supérieure finale.

Ce défaut affecte les cavités avec ou sans plateau et plusieurs étages.

## Défaut bloquant 2 — plusieurs plateaux traités globalement

`CasLimite02+` contient deux plateaux de dimensions différentes. La scène donne
l'impression que leurs hauteurs sont cumulées dans un encastrement global,
au lieu de produire les découpes locales propres à leurs empreintes et niveaux.

Le comportement attendu est :

- chaque réservation conserve son identité, son empreinte XY, son épaisseur et
  son intervalle Z ;
- deux réservations côte à côte ne cumulent pas leur hauteur ;
- deux réservations qui se recouvrent se composent seulement dans leur zone de
  recouvrement et selon leur ordre vertical ;
- aucune profondeur globale ou rectangle englobant ne s'applique à tous les
  corps du sommet.

## Défaut complémentaire — plafond de calcul dépassé

Dans une variante locale non sauvegardée de `CasLimite01+`, après l'ajout de
deux petits assets, l'interface a annoncé environ `24 s` écoulées pour un
plafond affiché de `20 s`.

Cette observation n'est pas encore une fixture reproductible, mais elle est
un défaut d'honnêteté du contrat :

- soit le plafond mural est réellement appliqué ;
- soit le budget contractuel et la terminaison/cleanup sont affichés
  séparément ;
- une durée présentée comme « maximum 20 s » ne peut pas être rapportée comme
  `24 s` sans explication.

## Hors de cette preuve

- Les modifications locales de Thomas n'ont pas été sauvegardées.
- Aucun projet personnel n'est modifié ou versionné.
- Les jobs annulables, miniatures de variantes et l'épaisseur distincte de
  séparateur restent hors du correctif R3.
- Aucun benchmark ou holdout solveur n'est autorisé par cette preuve.
