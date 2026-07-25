# ADR-0088 — Calcul minimal, finition optionnelle et budgets visibles

## Statut

Acceptée.

## Date

2026-07-25.

## Carte liée

- P64-L09R-A — Recadrage calcul, finition et progression.

## Remplace partiellement

- ADR-0087.

## Contexte

La correction P64-L08L a été validée dans Fusion 0.1.62 : environ 25 secondes
sur le cas préparé, puis environ 34 secondes après ajout d'un bac de cartes très
compliqué. Le plafond artificiel observé auparavant est donc corrigé.

Les lots P64-L09B, P64-L09C, P64-F01B et la partie admissible de P64-F02B ont
ensuite :

- remplacé l'appui sur enveloppe XY par un certificat de matière porteuse ;
- transmis les réservations supérieures au problème SCIP ;
- rendu la fermeture couplée obligatoire avant matérialisation pour les projets
  avec réservation ;
- préparé une gate Fusion 0.1.63 fondée sur cette trajectoire.

Thomas précise maintenant que la chute théorique dans l'ouverture d'un
conteneur inférieur n'est pas un défaut produit prioritaire : le conteneur sera
rempli par ses assets. La règle matérielle dure réduit la capacité de recherche
et peut empêcher un calcul utile. En revanche, l'ordre visuel et pratique reste
important : lorsque plusieurs solutions existent, les petits conteneurs doivent
de préférence se trouver sous les grands.

Le parcours courant mélange aussi trop fortement calcul minimal, finition et
matérialisation. Une opération longue donne l'impression que la palette est
figée, les budgets réels ne sont pas assez lisibles et l'utilisateur ne peut
pas toujours matérialiser un plan minimal pourtant valable avec ses plateaux.

## Options

1. Conserver ADR-0087, le certificat de matière porteuse et la fermeture
   obligatoire avant toute matérialisation avec réservation.
2. Revenir entièrement au comportement antérieur à P64-L09, y compris au refus
   des réservations supérieures dans SCIP.
3. Faire un retour sélectif : rétablir l'appui dur sur enveloppe, conserver les
   réservations SCIP, rendre la finition optionnelle, ajouter une préférence
   souple petits-dessous/grands-dessus et rendre budgets et activité visibles.

## Décision

L'option 3 est retenue.

### 1. Revenir à un certificat d'appui par enveloppe

Pour le placement global, une enveloppe extérieure XY admissible redevient la
surface d'appui dure d'un conteneur. Un conteneur supérieur peut donc être
placé au-dessus de l'ouverture d'un conteneur inférieur si les règles
d'enveloppe, de couverture, de stabilité, de collision, de jeux, de boîte et de
retrait sont satisfaites.

La vérification `falls_through_opening` de P64-L09B n'est plus une condition de
faisabilité du produit. Les calculs de matière réelle peuvent rester disponibles
comme diagnostic ou comme base de recherche future, mais ils ne doivent plus
rejeter un plan qui respecte le contrat d'enveloppe.

Cette décision ne transforme pas `has_lid` en certificat. Un couvercle reste
sans effet sur les poses globales tant qu'un mécanisme distinct n'a pas certifié
fermeture, rétention, épaisseur extérieure, appuis, stabilité, accès, retrait et
poses autorisées.

### 2. Préférer les petits conteneurs sous les grands sans durcir la faisabilité

Le solveur doit chercher en priorité les plans où les petites empreintes XY sont
plus basses et les grandes plus hautes. Cette préférence est une heuristique de
recherche et un départ proposé à SCIP, jamais une contrainte dure.

La comparaison initiale repose sur l'aire extérieure XY, puis sur le plus petit
côté, le volume et l'identité stable pour départager de façon déterministe.
L'implémentation pourra combiner :

- ordre des candidats et des variantes avant le solve ;
- incumbent ou warm start construit avec les petits conteneurs en base ;
- priorités de branchement ou objectif secondaire lexicographique ;
- classement final à faisabilité et qualité principale égales.

Une solution qui inverse cet ordre reste admissible si elle est la première
solution certifiée ou si elle est nécessaire à la faisabilité. Le budget ne doit
pas être consommé uniquement pour satisfaire cette préférence.

### 3. Conserver les réservations supérieures dans le calcul minimal

P64-L09C reste normative. Plateaux et livrets représentables doivent atteindre
SCIP avec empreinte, profondeur, plan d'appui, fond, cavités, jeux et ordre de
retrait fidèles.

`Calculer` doit produire un plan minimal certifié qui tient déjà compte de ces
réservations. La compensation Z strictement nécessaire au plateau ou au livret
fait partie de ce plan minimal. Elle ne peut ni réduire une cavité d'asset, ni
percer un fond ou une paroi minimale.

Un plan minimal ainsi certifié est matérialisable immédiatement. La présence
d'un plateau ne rend plus la finition obligatoire.

### 4. Séparer à nouveau calcul et finition

Le calcul de base cherche un placement 3D faisable et minimal. Il ne distribue
pas le volume résiduel de la boîte au-delà de ce qui est nécessaire aux
contraintes actives.

La finition devient une opération facultative et indépendante. Elle reçoit le
plan minimal comme incumbent, épaissit proprement parois et fonds selon les
règles existantes, distribue le volume résiduel entre les conteneurs dans leurs
bounds sûres, préserve réservations et cavités, puis tente des réparations
locales avant tout rappel global.

La boucle de finition reste bornée :

1. reprendre le plan minimal certifié ;
2. restaurer réservations et enveloppes mécaniques déjà certifiées ;
3. proposer une répartition du volume résiduel ;
4. réparer localement les conflits créés par l'expansion ;
5. répéter sous une deadline et un nombre d'itérations communs ;
6. rejouer le certificat global ;
7. publier seulement un plan final certifié.

Un échec de finition ne détruit pas le plan minimal. Il reste courant et
matérialisable. La finition n'a pas le droit de transformer cet échec en
impossibilité de placement.

### 5. Exposer cinq budgets de calcul

Le calcul de base offre cinq niveaux initiaux :

| Niveau | Budget total maximal |
| --- | ---: |
| Rapide | 3 s |
| Court | 10 s |
| Normal | 20 s |
| Long | 60 s |
| Approfondi | 180 s, soit 3 min |

Le budget est une deadline totale partagée par tout le calcul de base, et non
une durée réinitialisée pour chaque voie. Une solution peut terminer avant.

Le réglage de finition est indépendant. Il utilise initialement la même grille
de cinq budgets, mais choisir un niveau de finition ne modifie ni le niveau ni
le plan minimal du calcul de base.

Dans l'onglet Réglages, chaque sélecteur de niveau possède immédiatement à côté
un petit champ en lecture seule affichant la limite réelle, par exemple
`20 s max` ou `3 min max`. Le sélecteur de finition se trouve juste sous celui
du calcul et affiche son propre budget réel.

### 6. Garder les trois actions visibles

Les actions `Calculer`, `Finaliser` et `Matérialiser` restent toujours visibles
en bas de la palette.

- Au départ, seul `Calculer` est activable.
- Après un calcul minimal courant, `Calculer` se grise jusqu'à une modification
  pertinente ; `Finaliser` et `Matérialiser` deviennent activables.
- `Matérialiser` utilise le plan minimal tant qu'aucun plan final courant
  n'existe, puis le plan final courant après une finition réussie.
- Une modification de source, de géométrie, de réservation ou de réglage du
  calcul rend les plans obsolètes et réactive `Calculer`.
- Une modification du seul réglage de finition invalide seulement le plan final :
  le plan minimal reste matérialisable.
- Une opération active bloque seulement les actions incompatibles et les doubles
  lancements.

### 7. Afficher une progression uniquement pendant une opération

Une jauge horizontale occupe la largeur disponible juste au-dessus des trois
boutons, mais son conteneur n'existe visuellement que pendant une opération.

Quand aucune opération n'est active :

- la jauge est totalement invisible ;
- aucun espace vertical ne lui est réservé ;
- aucun état terminal précédent n'y reste affiché.

Pendant `Calculer` ou `Finaliser`, la jauge représente le temps écoulé par
rapport au budget choisi. Elle est rafraîchie environ une fois par seconde. Elle
ne prétend pas mesurer le pourcentage géométrique réellement résolu. Le texte
associé indique au minimum l'opération, l'étape connue, le temps écoulé et la
limite.

Pendant `Matérialiser`, la jauge est indéterminée tant qu'aucun nombre fiable
d'étapes CAD n'est disponible. Des phases réelles peuvent être affichées, mais
aucun faux pourcentage ni fausse estimation de fin ne doit être inventé.

Le résultat terminal reste affiché dans le diagnostic ou le résumé normal de
l'opération ; la jauge disparaît dès que l'opération n'est plus active.

### 8. Préserver la réactivité et la frontière Fusion

Le calcul pur et la finition pure doivent s'exécuter hors du thread d'interface
quand l'environnement Fusion le permet. Aucun appel `adsk` ne peut être fait
depuis ce worker. Le retour vers la palette vérifie les digests et rejette tout
résultat devenu obsolète.

La matérialisation Fusion reste sur le thread autorisé par l'API. Elle doit
publier des phases ou rendre la main entre des blocs sûrs lorsque c'est
possible, sans déplacer la logique métier dans l'adaptateur.

## Conséquences

- La correction de performance P64-L08L et la prise en charge des plateaux
  P64-L09C sont conservées.
- La règle dure de matière réelle P64-L09B et l'obligation de finaliser avant
  matérialisation introduite par P64-F01B sont remplacées.
- Les algorithmes F01B/F02B peuvent être réutilisés dans la finition séparée,
  mais leur cycle de vie produit doit être recâblé.
- La gate P64-L09V préparée sur 0.1.63 est annulée : ses critères anti-chute et
  finalisation obligatoire ne correspondent plus au produit décidé.
- La progression est honnête sur le temps et les phases connues, sans prétendre
  connaître l'avancement interne exact du MIP.
- Aucun changement de tolérance, valeur physique, pose de couvercle ou
  calibration d'impression n'est autorisé par cette ADR.

## Alternatives refusées

- Garder l'anti-chute comme règle dure : coût de recherche et refus produit sans
  bénéfice suffisant pour l'usage réel décidé.
- Supprimer aussi P64-L09C : cela réintroduirait le faux échec des projets avec
  plateau avant même l'appel à SCIP.
- Masquer `Finaliser` tant qu'aucun calcul n'existe : cela rendrait le parcours
  et les étapes moins compréhensibles.
- Conserver une jauge terminale : contraire à l'exigence d'une zone totalement
  invisible hors opération.
- Afficher un pourcentage de solution MIP inventé : trompeur et non testable.

## Suivi

Le contrat `docs/P64_L09R_CALCUL_FINITION_PROGRESS_CONTRACT.md` fixe le
découpage exécutable. La prochaine mission unique est P64-L09R-B.

Une nouvelle gate Fusion P64-L09R-V sera préparée seulement après les preuves
automatisées du calcul, de la finition optionnelle, de l'interface et de la
réactivité. `print-validated=false` reste inchangé.

## Amendement proposé P64-L09S

La gate humaine 0.1.65 invalide la compensation Z décrite aux sections 3 et 4 :
un petit conteneur est allongé arbitrairement pour soutenir 0,75 % du plateau.
La finition échoue ensuite sans plan final tout en annonçant un succès.

ADR-0089 propose de remplacer uniquement ces clauses par : réservations sans
croissance de support, fermeture globale exacte, annexes XY composites en repli
et résultat UI fidèle. Les budgets, la séparation calcul/finition, le support
par enveloppe et la conservation du plan minimal restent acquis.

Cet amendement devient normatif seulement lorsque Thomas lance explicitement le
Goal P64-L09S. Avant ce lancement, aucune implémentation n'est autorisée.
