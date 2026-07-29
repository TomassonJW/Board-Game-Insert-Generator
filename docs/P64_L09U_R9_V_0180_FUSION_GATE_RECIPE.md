# P64-L09U-R9-V — recette Fusion 0.1.80

Statut : candidate installée localement, gate humaine à exécuter.
`fusion-validated=false`, `print-validated=false`.

Cette recette vérifie uniquement la récupération de performance R9 sur la
candidate 0.1.80. Le résultat fonctionnel de 0.1.79 est déjà acquis : ne rejoue
pas la recette R8 et ne refais pas une campagne géométrique complète.

Ne sauvegarde ni `CasLimite02+.bgig.json` ni
`CasLimite02++.bgig.json`.

## 1. Démarrage

1. Ferme complètement Fusion 360.
2. Rouvre Fusion 360.
3. Recharge l’add-in Board Game Insert Generator.
4. Vérifie que la version affichée est `0.1.80`.

Si la version n’est pas `0.1.80`, arrête la gate et rapporte la version vue.

## 2. CasLimite02+

1. Ouvre `CasLimite02+.bgig.json` sans l’enregistrer.
2. Dans les réglages de recherche, choisis `Auto intelligent` et
   `Approfondi`.
3. Lance une seule fois `Calculer`.
4. Note le temps exact jusqu’à la première solution certifiée.
5. Vérifie que le résultat n’est pas annoncé comme repris du cache. Un ancien
   témoin peut être rejeté ou recertifié, mais la recherche courante doit avoir
   été exécutée.
6. Lance `Finaliser` et note son temps séparément.
7. Lance `Matérialiser` et note son temps séparément.
8. Confirme en un coup d’œil le résultat déjà accepté :
   même disposition, mêmes conteneurs, mêmes cavités et aucune géométrie
   positive liée aux éléments plats.

Au premier écart fonctionnel, arrête ce cas et relève l’étape, le conteneur ou
la région concernée, la mesure et une capture.

## 3. CasLimite02++

1. Ouvre `CasLimite02++.bgig.json` sans l’enregistrer.
2. Garde `Auto intelligent` et `Approfondi`.
3. Lance une seule fois `Calculer`, puis note le temps exact jusqu’à la
   première solution certifiée.
4. Vérifie que la recherche courante a été exécutée et que le résultat n’est
   pas un simple cache.
5. Lance `Finaliser`, puis `Matérialiser`, en notant les deux temps séparément.
6. Confirme en un coup d’œil les invariants déjà acceptés :
   petit livret dessous, grand plateau dessus, profondeurs locales
   `2 mm`, `4 mm` et `6 mm`, cavités ouvertes, aucun nouveau corps plat.

## 4. Verdict à renvoyer

Si la performance est redevenue satisfaisante et que le résultat reste
conforme :

```text
P64-L09U-R9-V Fusion OK 0.1.80
CasLimite02+ : calcul=... finalisation=... matérialisation=...
CasLimite02++ : calcul=... finalisation=... matérialisation=...
source du calcul : frais / témoin recertifié + recherche
résultat fonctionnel 0.1.79 conservé : oui
captures=...
```

Sinon :

```text
P64-L09U-R9-V Fusion KO 0.1.80
première divergence=performance / résultat / cache / installation
projet=...
étape=...
temps ou mesure=...
capture=...
```

Le retour vers quelques secondes est l’objectif observé automatiquement, pas
une promesse de seuil universel. Thomas garde l’autorité sur le verdict humain.
Une gate Fusion OK ne vaut pas validation d’impression :
`print-validated=false`.
