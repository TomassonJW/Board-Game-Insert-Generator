# P64-L09T-V — preuve humaine KO de la candidate 0.1.70

## 1. Statut

- package observé : `0.1.70` ;
- verdict : `human-KO` ;
- exécution recommandée : `do-not-run` ;
- `fusion-validated=false` ;
- `print-validated=false`.

La candidate 0.1.70 calcule et finalise les cas observés, mais sa
matérialisation finale monopolise Fusion pendant une durée incompatible avec
le produit. Elle restaure aussi un état de projet et un témoin de calcul entre
deux sessions alors que le cycle attendu est explicitement neuf.

## 2. Faits observés dans Fusion

Thomas a observé le 2026-07-27 :

- `CasLimite01+` et `CasLimite02+` peuvent être calculés et finalisés ;
- l'aperçu final est disponible avant matérialisation ;
- le calcul intermédiaire peut être matérialisé ;
- la matérialisation du plan final fait afficher
  « Autodesk Fusion ne répond pas » ;
- après plus de cinq minutes, aucune scène n'était encore publiée ;
- `CasLimite01+` a finalement été matérialisé après environ quinze minutes ;
- après fermeture forcée puis redémarrage de Fusion, BGIG rouvre le projet
  précédent ;
- le calcul repart alors presque instantanément et peut produire un résultat
  différent du calcul frais attendu.

Le journal de développement de la session concernée mesure
`706205 ms` entre la requête de matérialisation et la réponse
`scene_synchronized`, soit environ 11 min 46 s côté passerelle. Le temps
ressenti complet d'environ quinze minutes est donc cohérent avec la trace.

## 3. Diagnostic de matérialisation

Fusion n'était pas définitivement planté : le processus restait présent et la
scène a fini par être publiée. Le défaut est une explosion du coût de création
de la chronologie paramétrique.

L'adaptateur 0.1.70 créait une construction complète
plan/esquisse/extrusion pour chaque prisme ajouté et chaque coupe
rectangulaire :

- `CasLimite01+` : plusieurs centaines d'unions logiques et plus de cent
  coupes ;
- `CasLimite02+` : `331` unions logiques et `129` coupes.

Le certificat géométrique n'est pas en cause : le même plan peut être
représenté avec beaucoup moins de features Fusion tout en conservant chaque
opération logique.

## 4. Diagnostic du redémarrage

Deux persistances se cumulaient :

1. `bgig_project_v1.json` rechargeait automatiquement le dernier brouillon ;
2. un témoin certifié intersession pouvait être réinjecté comme incumbent.

La trace du redémarrage montre un cache de session manqué, mais un
`fresh_search_with_certified_witness` terminé en environ `102 ms`. Ce n'était
donc pas un vrai recalcul complet.

Cette persistance masquait aussi un défaut de calcul frais : la voie
déterministe « piles au sol sous réservation » exigeait une pose supérieure
déjà résolue alors que cette pose devait justement être décidée par le
calcul.

## 5. Correctif borné

Le correctif P64-L09U doit :

- démarrer chaque session Fusion sur un projet vierge non enregistré ;
- conserver l'ouverture et l'enregistrement des fichiers nommés uniquement
  comme actions explicites ;
- rendre les anciens fichiers de récupération et témoins intersession
  inertes sans les supprimer ;
- exécuter un vrai calcul complet après redémarrage ;
- rendre la voie « piles au sol » admissible avant résolution finale de la
  pose supérieure ;
- injecter la pose automatique déterministe de la réservation dans cette
  voie dense ;
- préserver toutes les unions et coupes logiques du CAD IR ;
- les matérialiser par lots, par corps propriétaire, avec un nombre de
  features Fusion proportionnel au nombre de corps et non au nombre de
  cellules composites.

## 6. Gate successeur

Le premier successeur autorisé est la candidate `0.1.71`.

La gate doit mesurer séparément :

- le temps de calcul frais ;
- le temps de finalisation ;
- le temps de matérialisation ;
- la réactivité de Fusion ;
- le nombre de composants publiés ;
- la synchronisation de scène ;
- le démarrage vierge après un nouveau redémarrage.

Thomas reste seul habilité à promouvoir `fusion-validated` et
`print-validated`.
