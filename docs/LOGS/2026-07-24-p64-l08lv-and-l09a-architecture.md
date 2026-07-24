# Journal — P64-L08LV validée et P64-L09A cadrée

## Déclencheur

Thomas confirme dans Fusion 360 avec l'add-in 0.1.62 :

- environ 25 secondes sur le cas préparé ;
- environ 34 secondes après ajout d'un bac de cartes jugé très compliqué.

La correction du plafond 29–30 secondes est donc observée positivement.

## Observations nouvelles

- un petit conteneur peut être empilé au-dessus d'une ouverture dans laquelle il
  pourrait tomber ;
- la couverture d'appui actuelle repose encore sur les enveloppes XY et ne
  représente pas toute la matière des rebords ;
- un plateau provoque un refus avant SCIP par
  `top_inset_reservations_not_supported` ;
- `has_lid` ne suffit pas pour autoriser une surface porteuse ou une nouvelle
  pose.

## Décision

ADR-0087 accepte :

1. un certificat d'appui fondé sur la matière ;
2. une règle anti-chute et un pontage matériel certifié ;
3. l'intégration fidèle des réservations dans SCIP ;
4. une boucle bornée placement, expansion, réparation et certification ;
5. une certification mécanique distincte avant toute pose de conteneur fermé.

## Portée

Mission d'architecture documentaire. Aucun code métier, benchmark, holdout,
runtime binaire, tolérance, valeur physique ou schéma produit n'est modifié.

La suite complète a révélé une incohérence préexistante sur `origin/main` :
`.gitattributes` impose LF au fichier licence HiGHS, tandis que son manifest
attendait encore les octets CRLF. Seuls la taille et le SHA-256 de cette entrée
du manifest sont réalignés sur le fichier versionné ; la licence et le runtime
restent inchangés.

## Validation

- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- garde HiGHS ciblée : 5/5 ;
- suite complète canonique : 834/834 ;
- `git diff --check` : OK.

## Suite

P64-L09B est la prochaine mission unique : durcir le certificat commun contre
les appuis sur le vide avant d'élargir la capacité SCIP aux réservations.
