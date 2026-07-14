# P66 - Gate humaine Fusion 360 du MVP V0.1

Statut : `mvp-accepted`, `fusion-validated: true`, `print-validated: false`.

Cette checklist archive la gate P66-V observee dans l add-in Fusion 360 ; aucun navigateur, serveur, Vite ou script utilisateur n a ete requis.

Le package observe est `0.1.20`, commit `6e351bb`. La validation Fusion est acquise pour le MVP V0.1, tandis que `print-validated: false` reste obligatoire.
## Resultat humain enregistre

Le 2026-07-14, Thomas a retourne exactement :

```text
P66 Fusion OK 0.1.20 - commit 6e351bb
```

Le MVP V0.1 Fusion-only est accepte. P67 devient `ready`; P44 reste bloque jusqu a la decision P67 et `print-validated` reste faux.

## Repères attendus avant observation

- fixture complète : 8 corps demandés, 0 complément explicite, 0 corps
  automatique, 2 étages (origines Z `0.0` et `35.6` mm) ;
- partition complète : digest
  `b5bf4e9c164642bfacc51bec038421827a1d30738f22149d2a00e6603d8abc9e` ;
- CAD IR : 8 composants, 9 cavités de contenu, 7 coupes d empreintes
  supérieures, digest
  `d5875dd560805a6420222e115b652027c24cb2e358442266fc1c3cd020025d7b` ;
- plan Fusion compact : 8 occurrences compactes, aucune occurrence éclatée ;
- fixture impossible : statut `impossible`, diagnostic local
  `CONTAINER_MINIMUM_BLOCKED`, aucun composant CAD.

## Checklist P66-V

### A. Accès et chargement

1. Crée un design Fusion compatible Assembly et un corps non BGIG nommé `P66 NON BGIG - KEEP`.
2. Lance BGIG depuis son icône Utilities.
3. Confirme une seule palette, une taille exploitable, aucun ancien dialogue, aucun navigateur et aucun timeout moteur.
4. Confirme que le statut sain est discret et que le rapport technique est replié.

### B. Projet et invalidation

5. Parcours Boîte, Plateaux et livrets, Éléments du jeu, Conteneurs, Réglages, Aperçu. Confirme que Bac vide, Bloc plein / cale et Séparateur ne sont plus proposés dans le parcours normal.
6. Confirme les sleeves, les dimensions résolues, une orientation à plat et une orientation debout.
7. Dans Conteneurs, lance `Estimer les tailles` et confirme minimum, demande, calculée, étage et raisons par axe sans création de scène.
8. Modifie une dimension source. Confirme que le dérivé est actualisé, que l ancien aperçu est grisé, que Materialiser est désactivé et que la scène est inchangée.
9. Restaure la fixture ou annule la modification, puis clique Recalculer.

### C. Résultat complet

10. Confirme le statut construit, exactement 8 corps, 0 automatique et au moins 2 étages.
11. Confirme la vue dessus et la coupe X/Z, le plateau et le livret encastrés, la prise, les appuis, l ordre de retrait et des cavités encore suffisamment profondes sous les plats.
12. Confirme le score et ses sous-critères en langage utilisateur, sans code moteur.

### D. Scène Fusion sûre

13. Clique Materialiser dans Fusion.
14. Confirme une seule racine BGIG, exactement 8 composants et des corps sur au moins deux origines Z.
15. Confirme les coupes localisées des plats, les cavités ouvertes, les noms uniques et les deux sketches de boîte cachés.
16. Confirme que `P66 NON BGIG - KEEP` existe toujours.
17. Clique Regénérer et reconfirme une racine, les mêmes nombres, aucun doublon et l objet non BGIG préservé.

### E. Export, réouverture et refus honnête

18. Exporte les imprimables : un STL par corps explicite, aucun sketch ou référence, manifestes JSON et Markdown présents.
19. Ferme puis relance l add-in et confirme la restauration du projet.
20. Importe la fixture impossible, vérifie le diagnostic local et le bouton Materialiser désactivé ; la scène précédente reste intacte.
21. Efface la scène BGIG et confirme que l objet non BGIG reste présent.

Une seule étape KO rend P66 KO. Une observation partielle ne peut pas accepter le
MVP. Ne modifie pas les réglages du produit pour contourner une fixture ou une
observation KO.

## Retour attendu

En cas de succès complet, réponds exactement :

```text
P66 Fusion OK 0.1.20 - commit <sha>
```

Sinon, réponds exactement :

```text
P66 Fusion KO - etape <n> - attendu <...> - observe <...> - message <...>
```

Un éventuel retour KO devient une mission atomique `P66-Hxxx`. Ne démarre ni
P67 ni P44 avant un retour humain P66 OK explicite.
