# ADR-0106 — Préfixe interne certifié avant SCIP

## Statut

Acceptée pour implémentation dans P64-L09U-R9-B.

Cette ADR ne valide ni Fusion ni l'impression. Elle ne change aucune valeur
physique, aucune grille, aucun epsilon, aucun budget et aucun plafond de
candidats.

## Contexte

R9-A établit que les deux projets autoritaires produisent le même payload SCIP
avec ou sans éléments plats.

La voie 0.1.79 :

1. lance ce payload une première fois pendant environ 12 s ;
2. relance le même payload ;
3. obtient un témoin natif après environ 56 s ;
4. rejette ce témoin par `MINIMAL_ENVELOPE_EXPANDED` ;
5. trouve finalement le résultat autoritaire dans le repli interne.

Le résultat humain validé porte le digest de placement
`a3ef2f440a212ed29496fe50072e065a0c861388e6e55e68c548c2bf8817bc46`.

Une projection interne Normal retrouve quelques secondes, mais produit
`3ca1d3d419717645a890406f7ef1370586907dd1762e2708df961fc063e1696a`.
Elle change donc la disposition et n'est pas admissible.

## Options comparées

### Option A — Accélérer seulement SCIP

Pistes :

- casser les symétries ;
- ajouter un incumbent natif ;
- propager davantage les contraintes ;
- réduire le presolve.

Avantages :

- conserve une voie de programmation entière ;
- peut servir d'autres problèmes.

Refus pour R9-B :

- le seul témoin obtenu sur le cas autoritaire est rejeté par le produit ;
- le modèle SCIP honore une expansion fixe que le certificat minimal refuse ;
- le coût racine précède l'obtention du témoin ;
- rendre plus rapide un témoin non certifiable ne récupère pas le résultat
  humain.

SCIP reste un repli borné ; sa formulation pourra être corrigée dans une
mission distincte si un cas certifiable l'exige.

### Option B — Utiliser la projection interne Normal

Avantages :

- 3,9 à 4,1 s sur les deux projets ;
- code court ;
- aucun appel natif.

Refus :

- le digest de placement change ;
- la disposition humaine 0.1.79 n'est pas conservée ;
- le profil Normal ne voit que six complétions et ne contient pas le candidat
  autoritaire d'index 10.

### Option C — Exécuter tout le portfolio interne Approfondi

Avantages :

- résultat autoritaire exact ;
- aucun témoin SCIP rejeté.

Refus comme résultat final :

- environ 24 s ;
- huit lanes supplémentaires n'apportent aucune complétion ;
- les certifications plates restent répétées.

Cette option sert de référence de fidélité.

### Option D — Préfixe interne certifié inchangé et repli SCIP

La première lane interne Approfondie est exécutée avec son arrêt historique
exact à `max_complete_candidates`. Le solveur ne termine pas le front au-delà
de ce point et n'élargit donc pas l'ensemble de candidats examiné.

Dès qu'une lane possède au moins une solution certifiée, cette lane devient
l'autorité du run. SCIP et les lanes suivantes ne sont plus exécutés.

SCIP reste disponible seulement si le préfixe interne ne produit aucune
solution certifiée.

Cette option est retenue.

## Décision

### 1. Ordre des voies

Pour un projet avec éléments plats et moins de douze groupes, la recherche
essaie d'abord le préfixe interne contre le projet complet.

La projection sans éléments plats ne lance plus SCIP avant ce préfixe.

SCIP n'est appelé que si :

- aucune solution interne certifiée n'a été trouvée ;
- le budget global restant le permet ;
- aucune annulation ou obsolescence n'est active.

### 2. Ensemble de complétions strictement inchangé

Le beam conserve son arrêt historique dès que
`max_complete_candidates` est atteint.

Un essai R9-B a terminé le front Normal déjà ouvert sans augmenter les limites
publiées. Il a observé 83 complétions, n'en a retenu que 6 et a réduit le temps
à `6,618 s`, mais le digest final est devenu
`269f9cdc4265bac3d10aa3480ff699c34ca7a49fc633e4222829ba23867fc009`.

Cet essai est rejeté : terminer le front élargit réellement l'ensemble des
solutions parmi lesquelles le produit choisit, même si le nombre finalement
certifié reste plafonné. Le résultat fonctionnel 0.1.79 n'est alors plus
préservé.

R9-B ne change donc ni :

- l'ordre d'exploration du beam ;
- son point d'arrêt ;
- `max_complete_candidates` ;
- `max_search_states` ;
- `max_placement_trials` ;
- `max_elapsed_ms` ;
- la deadline globale.

### 3. Classement avant certification

Le préclassement utilise seulement des faits géométriques exacts déjà présents
dans les placements :

- nombre de conteneurs élevés ;
- somme des bases Z ;
- volume élevé ;
- empreinte, volume, vide interne et hauteur du cluster ;
- fragmentation ;
- contacts ;
- support ;
- digest déterministe.

La compatibilité avec les éléments plats n'est jamais supposée. Le certificat
complet reste l'unique autorité pour :

- la pose automatique des éléments plats ;
- les parois ;
- les cavités ;
- l'accès ;
- les réservations ;
- l'ordre de retrait ;
- la géométrie soustractive.

### 4. Arrêt sur la première lane certifiée

Une lane qui publie au moins une solution certifiée termine la recherche du
run.

Le résultat est le meilleur candidat certifié de cette lane selon le
classement produit existant.

La télémétrie doit exposer :

- `first_certified_lane_authority=true` ;
- les limites inchangées ;
- les complétions géométriques et les candidats certifiés ;
- les lanes non exécutées ;
- l'absence ou la présence d'un repli SCIP.

Le texte « best certified proposal found within budget » doit être précisé
comme « best certified proposal from the first certified lane within budget ».

### 5. Déduplication locale des rangs plats

La résolution automatique peut mémoriser un rang uniquement :

- pendant un appel ;
- avec une clé géométrique exacte ;
- avec les placements, la boîte, le sommet de conception et le mode de
  réservation dans la clé ;
- sans réutilisation entre projets, révisions, candidats ou runs.

Aucun témoin, plan, cache ou résultat périmé ne peut être réutilisé.

### 6. Invariants inchangés

Restent autoritaires :

- grille produit de 0,1 mm ;
- epsilon interne distinct ;
- enveloppes minimales ;
- ordre petit-dessous/grand-dessus ;
- cavités, accès, parois et profondeurs 2/4/6 mm ;
- finalisation avant soustractions plates ;
- zéro volume, union ou corps positif attribué aux éléments plats ;
- aperçu, certificat, CAD IR, plan Fusion et BRep cohérents ;
- rollback, BRep transitoire et fichiers personnels préservés ;
- aucun faux impossible et aucun timeout maquillé.

## Conséquences

### Positives

- le travail certifiable devient prioritaire ;
- le témoin SCIP rejeté ne monopolise plus le run ;
- le candidat humain reste atteignable sans changer le front historique ;
- la stratégie est déterministe et testable ;
- SCIP reste disponible pour les échecs internes réels.

### Coûts

- la télémétrie et les tests de préfixe doivent être adaptés ;
- le contrat de sélection passe du meilleur portfolio entier à la première
  lane certifiée ;
- les digests de provenance changent même si la géométrie reste identique.

### Risques

- un autre projet pourrait préférer un candidat d'une lane ultérieure ;
- un préclassement incomplet pourrait écarter un candidat qui aurait mieux
  interagi avec un élément plat ;
- une mémorisation trop large pourrait devenir périmée.

Ces risques sont fermés par :

- le certificat complet avant publication ;
- le plafond inchangé ;
- la gate des deux digests autoritaires ;
- la suite autorisée complète ;
- un cache strictement local à un appel ;
- le repli SCIP seulement après échec certifié du préfixe interne.

## Gate de mise en œuvre

R9-B est acceptable seulement si :

1. les deux projets personnels restent bit à bit inchangés ;
2. le digest de placement autoritaire est conservé ;
3. la géométrie finale et les signatures CAD de 0.1.79 restent identiques ;
4. les deux calculs trouvent une solution certifiée ;
5. aucun budget ni plafond de candidats n'augmente ;
6. les tests ciblés et la suite autorisée passent ;
7. le coût ne se déplace pas vers la finalisation ou la matérialisation.

Si le digest autoritaire change, l'incrément est rejeté.
