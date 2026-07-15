# P44-M005 — Création pilotée et presets

## Statut

implemented, automated-validation-required, human-fusion-gate-required.
Package cible : palette Fusion 0.1.28.

## Objectif

Rendre la création d’un élément explicite et compacte dans l’onglet Conteneurs
et éléments, sans modifier le modèle de projet ni déplacer de logique métier
dans la palette.

## Parcours livré

1. Le contrôle collant Créer propose un sélecteur unique : Élément sur mesure,
   presets BGIG et presets personnels.
2. Un second sélecteur choisit Nouveau conteneur lié ou un conteneur existant.
3. Ajouter crée exactement un élément dans la destination choisie. Une nouvelle
   destination crée exactement un conteneur lié à cet élément.
4. Le bouton + d’un conteneur réutilise le preset sélectionné mais force ce
   conteneur comme destination : c’est le raccourci local.
5. Conteneur crée seulement un conteneur vide normal, jamais un complément.
6. Mes presets conserve import, export et suppression du preset personnel
   sélectionné. L’édition reste hors P44-M005.

## Invariants

- contents[].container_group_id reste la seule relation parent / enfant ;
- aucun champ de schéma, migration, bridge, solveur, tolérance, géométrie, CAD
  IR ou scène Fusion ne change ;
- les dimensions créées restent éditables ;
- les presets personnels restent atomiques et hors du package ;
- Bac vide, Bloc plein / cale et Séparateur restent absents du parcours normal.

## Preuves automatisées

- DOM : un sélecteur de preset, une destination, Ajouter et le raccourci local ;
- bridge et stockage personnel existants inchangés ;
- roundtrip des presets personnels et projets existants ;
- syntaxe JavaScript, suite complète, compileall, frontière adsk et diff-check.

## Gate humaine P44-M005V

Dans Fusion avec le package 0.1.28 :

1. choisir un preset BGIG et Nouveau conteneur lié, puis vérifier la création
   d’un seul conteneur contenant un seul élément ;
2. choisir un conteneur existant, ajouter un preset puis vérifier qu’aucun
   conteneur supplémentaire n’apparaît ;
3. sélectionner un preset personnel, utiliser Ajouter puis le + local d’un
   conteneur, vérifier les destinations ;
4. supprimer le preset personnel sélectionné, puis vérifier que les éléments
   existants restent inchangés ;
5. confirmer qu’aucun complément, calcul ou scène Fusion ne démarre
   automatiquement.

Retour attendu : P44-M005 Fusion OK 0.1.28 - commit <sha>.

Cette gate ne valide ni géométrie, ni tolérance, ni impression.
