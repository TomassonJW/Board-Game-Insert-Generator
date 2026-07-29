# P64-L09U-R8-V — recette Fusion 0.1.79

Statut courant : `ready-human-gate`, candidate 0.1.79 installée depuis
`8baaaa9`,
`fusion-validated=false`, `print-validated=false`.

Cette recette ne concerne que la candidate 0.1.79. Ne rejoue pas la gate
0.1.78. Ne sauvegarde ni `CasLimite02+` ni `CasLimite02++`.

## 1. Démarrage

1. Ferme complètement Fusion 360.
2. Rouvre Fusion 360.
3. Recharge l’add-in Board Game Insert Generator.
4. Vérifie que la version affichée est `0.1.79`.

Si la version n’est pas `0.1.79`, arrête la gate et rapporte la version vue.

## 2. CasLimite02+ — matière strictement soustractive

1. Ouvre `CasLimite02+.bgig.json` sans l’enregistrer.
2. Lance `Calculer` et note le temps exact ainsi que le niveau d’effort qui
   trouve la première solution.
3. Lance `Finaliser` et note le temps exact jusqu’à `Plan final prêt`.
4. Lance `Matérialiser` et note le temps exact jusqu’à
   `scene_synchronized`.
5. Compare l’aperçu final et la scène Fusion.
6. Inspecte les cavités sous et autour des empreintes plates, si besoin avec
   une coupe d’analyse Fusion.

Résultat attendu :

- les seuls corps imprimables sont les conteneurs finalisés ;
- aucun plateau, livret, support ou fermeture n’est un corps ;
- aucune plaque, rail, pont, appui ou surplomb n’est ajouté sous un élément
  plat ;
- les empreintes des éléments plats sont uniquement creusées dans les
  conteneurs ;
- toutes les cavités restent creusées, ouvertes et accessibles ;
- profondeurs, accès partiels et continuité directe acquis en R6 sont
  inchangés ;
- aucune encoche parasite ni micro-fragment de paroi ;
- chaque paroi ou séparation utile conserve au moins `1,2 mm` ;
- l’aperçu et Fusion montrent les mêmes empreintes locales.

Au premier écart, arrête ce cas et relève le conteneur, l’étape, la mesure et
une capture.

## 3. CasLimite02++ — pile et profondeurs locales

1. Ouvre `CasLimite02++.bgig.json` sans l’enregistrer.
2. Lance `Calculer`, `Finaliser`, puis `Matérialiser`, en notant les trois
   temps exacts.
3. Repère une zone couverte seulement par le livret, une zone couverte
   seulement par le plateau et leur zone de recouvrement.
4. Mesure les profondeurs locales depuis le sommet du conteneur.
5. Compare l’aperçu final et la scène Fusion.

Résultat attendu :

- livret orienté, plus petit : dessous ;
- plateau principal, plus grand : dessus ;
- zone livret seul : `2 mm` de profondeur ;
- zone plateau seul : `4 mm` de profondeur ;
- recouvrement : `6 mm` de profondeur ;
- paliers nets et conformes aux empreintes, sans couture parasite ;
- aucun volume positif, support, union, plaque ou nouveau corps lié aux
  éléments plats ;
- aucune cavité rebouchée ou rendue inaccessible ;
- profondeur des cavités, y compris les micro-chevauchements, inchangée.

## 4. Verdict à renvoyer

Si tout passe :

```text
P64-L09U-R8-V Fusion OK 0.1.79
CasLimite02+ : effort=... calcul=... finalisation=... matérialisation=...
CasLimite02++ : effort=... calcul=... finalisation=... matérialisation=...
profondeurs mesurées : livret=... plateau=... recouvrement=...
paroi minimale mesurée=...
corps imprimables observés=...
captures=...
```

Sinon :

```text
P64-L09U-R8-V Fusion KO 0.1.79
première divergence=...
projet=...
étape=...
conteneur/région=...
mesure=...
capture=...
```

Une gate Fusion OK ne vaut pas validation d’impression :
`print-validated=false`.
