# P64-L09S-V — preuve du KO humain 0.1.69

## 1. Statut

- package observé : `0.1.69` ;
- commit source : `21d4eebaac1ee64f0fe715560a58e79dc51c3291` ;
- verdict : `human-KO` avec acquis partiels positifs ;
- package : `do-not-run` pour une nouvelle gate ;
- suite corrective : P64-L09T ;
- `fusion-validated=false` ;
- `print-validated=false`.

Cette preuve enregistre le retour dicté par Thomas le 2026-07-26 puis son
arbitrage explicite du 2026-07-27. Les projets personnels et journaux locaux ne
sont pas ajoutés au dépôt.

## 2. Acquis observés

Thomas rapporte :

- `CasLimite01` de base semble calculer et finaliser correctement ;
- `CasLimite02` de base semble conserver la cavité attendue et se matérialiser ;
- la jauge reste active et fluide pendant le calcul et la finition ;
- la correction des réservations virtuelles et de la cavité orientée est
  visiblement meilleure que dans 0.1.68.

Ces faits sont conservés comme résultats positifs partiels. Ils ne suffisent pas
à promouvoir la capability globale.

## 3. CasLimite01+

Le projet ajoute :

- trois contenus `20 x 20 x 10 mm` dans un conteneur existant ;
- un nouveau conteneur ;
- deux contenus supplémentaires dans ce nouveau conteneur.

Le calcul Normal réussit autour de `8.3 s`. La finition échoue :

- Normal autour de `17.2 s` ;
- Long autour de `20.6 s` ;
- motif persistant :
  `xy_composite_product_certificate_rejected`.

La réservation du plateau est en mode sans origine explicite, mais le runtime
la traduit seulement en `auto_center`. Le témoin minimal respecte cette
réservation centrée ; le KO précis n'est donc pas une collision directe prouvée
avec le plateau. Le rejet interne détaillé du certificat produit n'est pas
persisté dans le journal et devra être rendu observable.

Le placement montre aussi plusieurs conteneurs élevés alors que la couche basse
paraît exploitable. Le classement de la voie de piles minimise d'abord la somme
des surfaces de base et le nombre de piles ; il favorise donc la compacité par
empilement avant l'occupation des couches basses.

## 4. CasLimite02+

Le projet ajoute jusqu'à trois contenus `20 x 20 x 10 mm` dans `c4`. Il modifie
aussi les jeux globaux vers `0.4 mm`; ce cas n'est donc pas un delta à une seule
variable.

Le calcul Rapide réussit entre environ `0.5 s` et `0.9 s`. La finition échoue
avec un, deux ou trois contenus ajoutés, selon les essais entre environ `3 s`
et `14 s`.

Le motif persistant est :

`xy_composite_gross_partition_not_found`

Le projet de base peut finaliser avec une solution minimale et échouer avec une
autre. La capacité de finition dépend donc encore trop du candidat minimal et
de la fermeture rectangulaire préalable.

## 5. Diagnostic structurel

Le repli `close_xy_composite_partition` :

1. appelle d'abord une fermeture rectangulaire brute sans réservations hautes ;
2. abandonne si cette fermeture laisse un espace ;
3. ne construit les corps composites qu'après une fermeture brute complète.

Il ne sait donc pas encore attribuer directement un trou intérieur résiduel à
un propriétaire adjacent, contrairement à l'intention d'ADR-0089.

Pour `CasLimite01+`, la fermeture composite atteint le certificat produit, mais
la recertification consomme encore la fermeture brute au lieu de prendre les
corps composites finaux comme autorité géométrique. Cette frontière doit être
auditée et corrigée ; la preuve actuelle ne permet pas d'affirmer un sous-code
de rejet plus précis.

## 6. Défauts produit ajoutés au correctif

Thomas confirme les exigences suivantes :

- supprimer définitivement la réutilisation automatique d'un plan après ajout
  ou modification d'un contenu ou d'un conteneur ;
- conserver seulement dépendances, invalidation, statuts et cache exact lors
  d'un calcul explicite ;
- retirer les origines X/Y des plateaux et livrets du parcours produit ;
- faire choisir leur pose par le calcul tout en les gardant virtuels et au plus
  haut ;
- privilégier les couches basses avant l'empilement, sans règle gloutonne qui
  détruirait une solution globale ;
- figer corps minimaux, cavités et réservations avant la finition ;
- préserver une épaisseur de paroi minimale entre toute cavité et toute coupe
  de plateau/livret ;
- afficher la vraie raison d'un arrêt avant le plafond de budget.

## 7. Stratégie de finition acceptée

La seule stratégie immédiate est :

1. figer les corps minimaux, cavités et réservations ;
2. tenter les extensions rectangulaires ;
3. découper le résiduel en annexes rectangulaires ;
4. rattacher chaque annexe à un conteneur adjacent ;
5. unir l'annexe au conteneur sans déplacer sa cavité ;
6. certifier jeux, réservations, unions, coupes et résiduel nul.

L'interface entre annexe et propriétaire devient interne au même corps : le jeu
y est nul. Tous les jeux externes avec les autres corps, la boîte, les cavités,
les réservations et les vides techniques restent obligatoires.

## 8. Horizons différés

Trois familles sont conservées dans le pilotage, sans runtime dans P64-L09T :

- cales solides imprimées séparément ;
- séparateurs sans fond ;
- conteneurs de finition générés.

Elles devront apparaître dans une surface future distincte des conteneurs et
éléments source.

## 9. Gate successeur

P64-L09T exécute des missions atomiques et intégrées une par une. Il prépare
une nouvelle candidate seulement après :

- suppression des réutilisations automatiques ;
- placement automatique et certifié des réservations ;
- priorité basse corrigée ;
- fermeture hybride réelle ;
- certificat et CAD composites concordants ;
- régressions isolées dérivées de `CasLimite01+` et `CasLimite02+` ;
- suite complète verte.

La gate P64-L09T-V reste humaine. Elle ne vaut jamais validation d'impression.

## 10. Conclusion

0.1.69 conserve des avancées importantes, mais ne satisfait pas la robustesse
de calcul et de finition demandée. Le verdict autoritaire est `human-KO`,
`do-not-run`, `fusion-validated=false`, `print-validated=false`.
