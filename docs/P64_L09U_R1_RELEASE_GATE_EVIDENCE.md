# P64-L09U-R1 — correctif Fusion et candidate 0.1.72

## 1. Statut

- source corrective : `automated-validated` ;
- candidate : `0.1.72` ;
- gate : `prepared-not-human-observed` ;
- `fusion-validated=false` ;
- `print-validated=false`.

0.1.71 reste `human-KO` et `do-not-run`.

## 2. Références de corps Fusion

La persistance des boîtes outils respecte maintenant le cycle réel d'une
BaseFeature :

1. ouvrir la BaseFeature ;
2. ajouter tous les BRep transitoires ;
3. terminer l'édition ;
4. relire exactement le même nombre de corps résultats depuis
   `baseFeature.bodies` ;
5. fournir uniquement ces corps résultats au Combine ;
6. ne jamais conserver les corps sources comme outils après `finishEdit`.

Un test de contrat reproduit `ALL_TOOL_BODY_REFERENCE_LOST` lorsqu'un faux
adaptateur tente de réutiliser un corps source. Les lots Join et Cut testés
acceptent uniquement les corps résultats.

## 3. Rollback de scène

Toute erreur pendant la génération, l'inspection ou la validation de la scène
déclenche désormais la suppression des objets BGIG de la génération.

- si le registre revient à zéro, l'erreur Fusion originale est remontée ;
- si des objets restent, l'erreur indique le nombre restant ;
- les objets non BGIG du document ne sont jamais ciblés.

Ce rollback complète les validations fail-closed du plan et empêche une scène
partielle de passer pour une matérialisation.

## 4. Acquis conservés

- session vierge non enregistrée ;
- aucun témoin intersession ;
- calcul explicite frais ;
- réservation supérieure automatique ;
- priorité plancher d'abord ;
- cavités figées ;
- fermeture composite et résiduel nul ;
- opérations CAD logiques conservées ;
- lots Fusion par propriétaire.

## 5. Validations

- tests ciblés adaptateur, palette, release et non-régressions :
  `149/149`, avec une intégration SCIP native ignorée ;
- six replays personnels exacts : `6/6`, lecture seule et sources inchangées ;
- suite globale autorisée : `881/881` en `408.131 s` ;
- modules exécutés : `113` ;
- modules benchmark/corpus/tournoi exclus : `12` ;
- test ignoré : `1`, intégration SCIP native indisponible sous Python 3.10 ;
- preflight public 0.1.72 :
  `b3f8c6cfc183c4a929516d46d44e03e4cbb22cafd6f2c1f9a35a958cc80e555b` ;
- aucun benchmark ou holdout exécuté.

La vérification du package installé est réalisée après intégration dans
`origin/main`.

## 6. Limites

- aucun appel réel à l'API Fusion ne peut être certifié par les tests Python ;
- seul Thomas peut confirmer le temps, la réactivité, la géométrie et la
  synchronisation de scène de 0.1.72 ;
- l'annulation coopérative et la progression par lot ne font pas partie de ce
  correctif atomique ;
- le cas `CasLimite01++` n'est pas revendiqué comme résolu automatiquement ;
- aucune impression n'a été réalisée.
