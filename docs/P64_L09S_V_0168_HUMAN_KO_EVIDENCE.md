# P64-L09S-V 0.1.68 - preuve human-KO et correctif 0.1.69

mission: P64-L09S-V corrective
failed-package: 0.1.68
candidate-package: 0.1.69
status: automated-validated-awaiting-human-gate

## 1. Statut

Le package `0.1.68` est `human-KO`, non accepte et `do-not-run`.

Le package `0.1.69` est le seul candidat autorise pour la prochaine gate. Il
est valide automatiquement, mais reste `fusion-observed=false` et
`print-validated=false` jusqu'au verdict de Thomas dans Fusion.

## 2. Faits observes

### CasLimite01

- 18 conteneurs varies, sans groupe multi-assets, avec un plateau central a
  100 %.
- Avec plateau, Rapide, Court, Normal, Long et Approfondi ne trouvaient pas de
  calcul exploitable dans `0.1.68`.
- Sans plateau, Normal pouvait trouver une disposition, mais elle compactait
  trop les conteneurs en hauteur au lieu de conserver une base basse favorable
  aux reservations superieures.
- La jauge avancait quelques secondes, sautait par exemple de 4 a 10 s ou de
  7 a 20 s, puis semblait gelee jusqu'au retour du calcul.

### CasLimite02

- Le calcul et la finition pouvaient terminer rapidement avec un plateau et un
  livret.
- Le bac de cartes debout conservait `63.6 mm` avant finition, puis sa cavite
  etait rabotee jusqu'a environ `24 mm`.
- Les volumes d'encastrement etaient appliques sur une geometrie qui ne
  correspondait plus au corps final.

Ces observations sont incompatibles avec la protection des minima et avec la
verite du cycle. Elles imposent le verdict `human-KO`.

## 3. Diagnostic CasLimite01

La reservation plateau doit participer au calcul comme un prisme virtuel
interdit, toujours au-dessus. Elle ne devient jamais un corps utilisateur et ne
peut jamais allonger un conteneur pour fabriquer un support.

Le correctif `0.1.69` ajoute une voie bornee de piles posees au sol pour les
grands cas avec reservations superieures. Elle :

- ne place que les enveloppes minimales certifiees ;
- construit des piles verticales legales ;
- range leurs bases sur le fond en respectant les prismes reserves ;
- s'arrete a 1024 etats et 1024 tentatives de rangement ;
- repasse toujours par le certificat BGIG commun.

Le repli composite de finition repart du plan minimal certifie original. Il ne
reutilise plus une croissance continue partielle qui a deja echoue.

## 4. Diagnostic CasLimite02

La profondeur de cavite utilisait l'axe brut avant orientation. Pour un bac de
cartes debout, cet axe valait `24 mm` alors que la profondeur canonique courante
valait `63.6 mm`.

Le correctif reconstruit la base dans l'orientation canonique, retire une
ancienne compensation eventuelle, puis ajoute uniquement l'encastrement courant.
Sur le projet exact :

- profondeur source : `63.6 mm` ;
- compensation locale plateau/livret : `4.0 mm` ;
- profondeur finale et coupe CAD : `67.6 mm` ;
- fond conserve : `2.2 mm`.

Les unions des corps finaux precedent les coupes. Une encoche ne touche qu'un
corps qui atteint vraiment le plan reserve et chevauche son empreinte.

## 5. Reactivite et identite

Le worker Python signale maintenant sa fin par un evenement Fusion. La palette
garde son propre affichage temporel local a une seconde et ne traverse plus le
pont Python toutes les secondes.

Le budget contractuel reste stable dans l'identite du solveur. Le temps restant
avant la deadline globale agit comme une limite d'execution distincte ; les
millisecondes du systeme ne changent plus l'empreinte d'un plan identique.

## 6. Validation automatisee

Rejeu local exact, sans versionner les projets personnels :

- `CasLimite01` : calcul certifie en `3.321 s`, `18/18` placements minimaux ;
- `CasLimite01` : finition en `11.132 s`, `18/18` corps finaux,
  `printable_residual_volume_mm3=0`, plan final courant et recertifie ;
- `CasLimite01` : `7` reservations, `5` coupes reelles, `18` composants CAD,
  `20` coupes de cavite et `5` coupes d'encastrement ;
- `CasLimite02` : calcul, finition et CAD verts, cavite finale `67.6 mm`,
  aucune reduction de minimum.

Suite complete :

- `authorized-suite: 910/910` en `329.251 s` ;
- un test SCIP natif ignore sous Python 3.10 ;
- corpus CI rejoue deux fois par cas avec empreinte fonctionnelle stable ;
- le test de sidecar synthetique confirme `solver_invocation_count=0` ;
- aucun benchmark, tuning ou holdout solveur n'a ete execute.

## 7. Gate successeur

La gate `P64-L09S-V` doit rejouer le smoke public, `CasLimite01` et
`CasLimite02` avec le package `0.1.69` construit depuis le SHA integre dans
`main`.

Le verdict reste humain. Avant ce verdict :

- `fusion-observed=false` ;
- `fusion-validated=false` ;
- `print-validated=false`.
