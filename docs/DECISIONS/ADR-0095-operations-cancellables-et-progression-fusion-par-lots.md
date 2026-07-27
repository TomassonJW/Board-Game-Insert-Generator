# ADR-0095 — Opérations annulables et progression Fusion par lots

## Statut

Proposée après le retour humain 0.1.71 du 2026-07-27.

Cette ADR ne change pas le runtime de 0.1.72.

## Contexte

La palette expose déjà une jauge temporelle honnête pour Calculer, Finaliser et
Matérialiser. Elle n'affiche volontairement aucun bouton d'annulation :
`cancel_supported=false`.

Thomas demande :

- une progression de matérialisation liée au travail réellement accompli ;
- un rafraîchissement visible pendant la construction ;
- un bouton d'annulation pour calcul, finalisation et matérialisation.

Un simple bouton qui masque la jauge serait trompeur. Une annulation fiable doit
arrêter le travail, empêcher toute publication tardive et remettre la scène
Fusion dans un état propre.

## Décision proposée

### 1. Modèle commun de job

Chaque opération longue devient un job identifié par :

- type d'opération ;
- révision et digest d'entrée ;
- état `queued`, `running`, `cancelling`, `cancelled`, `succeeded` ou `failed` ;
- étape courante ;
- unités terminées et totales lorsqu'elles sont connues ;
- jeton d'annulation coopérative ;
- reçu terminal unique.

Un résultat d'un job annulé ou devenu obsolète ne peut jamais être publié.

### 2. Calcul et finalisation

Les boucles et lanes consultent le jeton à des frontières sûres déjà
déterministes. L'annulation devient `user_cancelled`, distincte de deadline,
impossibilité et invalidation stale.

Un solveur natif non interruptible est isolé derrière une frontière qui peut
refuser sa publication, même s'il termine après l'annulation logique.

### 3. Matérialisation Fusion

La progression avance par unité métier :

- préparation d'un composant ;
- création du corps ;
- lot Join ;
- lot Cut ;
- validation du composant ;
- validation finale de scène.

Elle n'avance pas à chaque appel API élémentaire. Ce niveau serait trop coûteux,
instable et susceptible de créer de la réentrance dans Fusion.

Le rafraîchissement de l'interface est borné, au plus à chaque lot ou selon une
cadence minimale. Il reste sur le thread Fusion autorisé.

### 4. Annulation et rollback

Une annulation de matérialisation :

1. cesse de démarrer de nouveaux lots ;
2. termine proprement l'appel Fusion déjà engagé ;
3. supprime toute la scène BGIG du job ;
4. vérifie qu'il ne reste aucun objet BGIG ;
5. publie seulement alors `cancelled`.

Un rollback incomplet produit `failed_cleanup`, jamais `cancelled`.

## Conséquences

- la jauge devient déterminée lorsque le nombre de lots est connu ;
- le temps écoulé reste visible sans inventer d'ETA ;
- le bouton Annuler n'apparaît que si le job sait réellement coopérer ;
- le transport palette/Fusion doit devenir asynchrone et testable ;
- les logs conservent la cause terminale et les unités accomplies.

## Alternatives refusées

- appeler un rafraîchissement après chaque commande Fusion ;
- tuer Fusion ou un processus solveur ;
- masquer seulement la jauge ;
- appeler `cancelled` un résultat devenu simplement stale ;
- conserver une scène partielle après annulation.
