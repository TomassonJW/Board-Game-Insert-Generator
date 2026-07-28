# P64-L09U-R7-V — recette Fusion 0.1.78

Statut : `prepared-not-human-observed`.

Cette gate doit être faite dans Fusion 360. Ne sauvegarde ni
`CasLimite02+` ni `CasLimite02++`.

## 1. Démarrage

1. Ferme complètement Fusion 360.
2. Rouvre Fusion 360.
3. Recharge l'add-in Board Game Insert Generator.
4. Vérifie que la version affichée est `0.1.78`.

Si la version n'est pas `0.1.78`, arrête la gate et rapporte la version vue.

## 2. CasLimite02+ — placement et parois

1. Ouvre `CasLimite02+.bgig.json`.
2. Lance `Calculer` et note le temps ainsi que le résultat.
3. Lance `Finaliser` et note le temps ainsi que le certificat.
4. Lance `Matérialiser` et note le temps jusqu'à la scène synchronisée.
5. Compare l'aperçu et la scène Fusion.
6. Avec l'outil de mesure Fusion, contrôle les morceaux de paroi les plus fins
   autour du livret, des plateaux, des cavités et du bord de boîte.

Résultat attendu :

- aucune découpe ne rejoint gratuitement le bord de boîte ;
- chaque paroi ou séparation utile conserve au moins `1,2 mm` ;
- aucun fragment proche de `0,4 mm` ;
- les encoches sont utiles et centrées sur la matière/cavité concernée ;
- aucune micro-encoche proche de `0,5–0,6 mm` de large et `6 mm` de profondeur ;
- aucune plaque, fermeture ou surplomb au-dessus des corps ;
- profondeurs, accès partiels et continuité directe R6 inchangés.

Au premier écart, arrête ce cas et relève le conteneur, la mesure, l'étape
`Calculer`/`Finaliser`/`Matérialiser`, ainsi qu'une capture.

## 3. CasLimite02++ — pile forcée

1. Ouvre `CasLimite02++.bgig.json` sans enregistrer.
2. Lance `Calculer`, `Finaliser`, puis `Matérialiser`, en notant les trois
   temps.
3. Observe séparément les zones couvertes par un seul élément et leur zone de
   recouvrement.
4. Compare l'aperçu et la scène Fusion.

Résultat attendu dans la zone de recouvrement :

- livret orienté, plus petit : dessous ;
- plateau principal, plus grand : dessus ;
- intervalles Z contigus et paliers correspondant exactement aux empreintes ;
- aucune couture transformée en micro-encoche ;
- aucun volume additif, plaque de fermeture ou surplomb ;
- les cavités restent accessibles sous et hors empreinte selon leur géométrie
  certifiée ;
- profondeur des cavités, y compris micro-chevauchements, inchangée.

## 4. Verdict à renvoyer

Si tout passe :

```text
P64-L09U-R7-V Fusion OK 0.1.78
CasLimite02+ : calcul=... finalisation=... matérialisation=...
CasLimite02++ : calcul=... finalisation=... matérialisation=...
paroi minimale mesurée=...
captures=...
```

Sinon :

```text
P64-L09U-R7-V Fusion KO 0.1.78
première divergence=...
projet=...
étape=...
conteneur/région=...
mesure=...
capture=...
```

Une gate Fusion OK ne vaut pas validation d'impression :
`print-validated=false`.
