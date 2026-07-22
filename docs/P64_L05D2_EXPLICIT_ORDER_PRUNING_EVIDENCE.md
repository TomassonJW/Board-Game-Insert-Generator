# P64-L05D2 - Preuve elagage sous ordre explicite

## Resultat

Statut : implemented-core, automated-validated.

fusion-validated: false. print-validated: false.

Une lane a ordre explicite cesse maintenant d'evaluer les participants apres le
quota de participants non vides qui peut reellement etre retenu. La voie
heuristique sans ordre reste strictement exhaustive sur les participants
restants.

## Test d'invariant

Le test P64-L05D2 utilise quatre participants tous admissibles et un quota de
deux :

- avant changement, la voie explicite evalue `a, b, c, d` ;
- apres changement, elle evalue seulement `a, b` ;
- la voie sans ordre continue d'evaluer `a, b, c, d` ;
- les deux voies conservent une solution ;
- les essais de placement de la voie explicite sont strictement inferieurs.

Le test rouge a ete observe avant implementation, puis passe apres les sept
lignes de coupure bornee.

## Comparaison A/B du corpus complet

Meme corpus :
`409c75095c47c4ca85a6dda469e986d36d67d460bf308ac9a96e1d3898ac26cf`.

- 7 cas, tiers CI + extended, 3 repetitions ;
- baseline fonctionnelle :
  `218cbe112bf1199aacdf0dc5936f8e128e74c59ffb54d02bfb8784a3736ed0bf` ;
- candidat fonctionnel :
  `bb8c36bdf46f7a13211f9fdf7e91cdec454f0aa84e02bcd02b130f6d38757493` ;
- regression fonctionnelle : 0 ;
- perte de solution ou certificat : 0 ;
- changement de prefixe de lanes : 0 ;
- attentes violees : 0 ;
- candidat A/B accepte : oui.

Travail total observe :

- essais de placement : 57 329 -> 31 901, soit -44,355 % ;
- etats explores : 2 581 -> 3 333, soit +29,136 % sous les memes caps.

Cas les plus affectes :

- fermeture continue Normal : 50 436 -> 30 662 essais et
  1 853 -> 2 593 etats ;
- dense 11 x 34 Rapide : 6 546 -> 892 essais et 532 -> 544 etats.

Les temps medians cumules passent de 3 376,002 ms a 3 473,315 ms,
soit +2,883 %. Cette variation reste dans la tolerance A/B de 10 % mais n'est
pas revendiquee comme gain global de vitesse. Le cas dense est plus rapide dans
cet echantillon ; le cas continu utilise le budget libere pour explorer
davantage d'etats.

## Projet personnel en lecture seule

SHA-256 avant et apres :
`4613C7BB3EA01FA4678640BA4C52C82D46D440FB26313E4239E55D56DD687E15`.

Apres optimisation :

- Rapide : 0,160 s, 2 176 essais, 298 etats, profondeur maximale 7 ;
- Normal : 1,862 s, 21 623 essais, 3 304 etats, profondeur maximale 7 ;
- Approfondi : 8,162 s, 80 713 essais, 12 520 etats, profondeur maximale 7 ;
- aucune completion geometrique ;
- Approfondi reste `deep_extension_exhausted_without_incumbent`.

L'optimisation reduit du travail inutile mais ne reconstruit pas encore ce cas.
Aucune donnee du projet n'est commitee et aucune solution n'est revendiquee.

## Validations ciblees

- invariant L05D2 : 1/1 ;
- beam 3D libre : 4/4 ;
- solveur minimal : 14/14 ;
- corpus : 5/5 ;
- comparaison A/B : acceptee ;
- Ruff cible : OK ;
- py_compile et compileall : OK ;
- frontiere adsk du coeur pur : OK ;
- suite complete : 680/680 en 144,846 s ;
- git diff --check et staged diff-check : OK avant commit.

## Limites honnetes

- aucun nouveau cas passe de l'echec a la solution dans le corpus initial ;
- le temps global n'est pas ameliore sur cet echantillon ;
- le projet personnel reste hors capacite ;
- aucune observation Fusion ;
- manifest Fusion inchange a 0.1.58 ;
- aucune nouvelle revendication sur le cas dense 11 x 34.
