# Product Brief

## Produit

Board Game Insert Generator est un outil local de conception parametrique d'inserts de jeux de societe pour impression 3D FDM.

## Utilisateurs cibles

- Createurs d'inserts qui veulent automatiser les bases repetitives.
- Joueurs experts qui rangent beaucoup de jeux et veulent des modules adaptes.
- Makers equipes d'une imprimante FDM.
- Designers techniques qui veulent une base parametrique extensible.
- Developpeurs ou agents qui doivent generer des variantes de rangement a partir de donnees structurees.

## Cas d'usage initiaux

- Decrire une boite et obtenir un layout rectangulaire simple.
- Comparer dimensions theoriques et dimensions imprimables.
- Produire un rapport partageable avant modelisation CAD.
- Preparer une integration Fusion 360 propre.

## Objectifs

- Garder toutes les dimensions en millimetres.
- Rendre les tolerances explicites et modifiables.
- Separer configuration, layout, tolerances, geometrie abstraite et cible Fusion 360.
- Fournir des erreurs lisibles.
- Permettre des tests unitaires sans Fusion 360.

## Non-objectifs V0

- Optimisation automatique parfaite.
- Generation STL ou 3MF directe.
- Interface graphique.
- Connexion Google Sheets.
- Interpretation IA libre du contenu utilisateur.
- Modelisation de cavites complexes.
- Garantie d'impression sans prototype physique.

## Hypotheses de depart

- Les boites et modules V0 sont axes selon X/Y/Z et alignes sur une grille orthogonale.
- Les modules V0 sont rectangulaires.
- Les modules composites sont un concept de modele, mais pas encore une capacite de layout avancee.
- L'utilisateur accepte de fournir des dimensions fiables.

## Critere de reussite V0

Un developpeur doit pouvoir cloner le depot, lancer les tests, executer un exemple et comprendre comment ajouter la generation Fusion 360 sans deplacer le coeur metier.
