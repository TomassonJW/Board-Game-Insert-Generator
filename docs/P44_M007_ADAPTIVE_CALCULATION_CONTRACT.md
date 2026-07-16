# P44-M007 - Calcul adaptatif et Aperçu priorisé

Statut : accepté pour implémentation par le GO transmis ; implémentation bornée au package Fusion 0.1.37.

## Objectif

Rendre la boucle de conception fluide sans introduire de seconde logique métier :
la palette observe les éditions, demande au cœur Python les dérivations puis la
proposition complète après stabilisation, affiche l’Aperçu avant les détails et
ne touche jamais à la scène Fusion sans action explicite.

## Périmètre autorisé

- orchestration JavaScript de la palette embarquée ;
- états UI du calcul et traitement logique des réponses obsolètes ;
- hiérarchie de l’onglet Aperçu ;
- fallback manuel `Recalculer maintenant` ;
- présentation dérivée et grisée de `Hauteur de conception` ;
- tests DOM, syntaxe, packaging et préparation de gate Fusion.

Le bridge JSON, `bgig.project.v1`, le solveur, ses budgets, ses heuristiques, les
valeurs physiques, les tolérances, la géométrie, la CAD IR et la matérialisation
restent inchangés. Aucun import `adsk` n’entre dans le cœur Python.

## Cycle adaptatif

Une édition incrémente `sourceRevision`, invalide visiblement la dernière
proposition et annule le solve planifié qui n’a pas encore démarré.

1. Après 350 ms sans nouvelle édition, la palette envoie `validate_project`.
2. Si cette validation courante est acceptée, elle programme `solve_project`
   pour atteindre 1 500 ms de stabilité depuis la dernière édition.
3. Une seule requête solve courante est lancée ; une requête déjà en cours n’est
   pas dupliquée.
4. Une réponse dérivée est ignorée si sa `sourceRevision` n’est plus courante.
5. Entre deux requêtes du même type et de la même révision, seule la dernière
   identité de requête peut mettre à jour l’UI.
6. Un timeout, une erreur de bridge ou un projet invalide arrête le cycle et
   rend `Recalculer maintenant` disponible comme fallback explicite.

Le transport ne promet pas une annulation physique d’un calcul Python déjà
entré dans le handler Fusion. La garantie est une annulation logique : aucune
réponse obsolète ne devient l’état visible ou matérialisable.

## Aperçu priorisé

Pour une proposition complète ou partielle, l’ordre visible est :

1. statut compact `Prêt`, `À recalculer`, `Partiel` ou `Calcul impossible` ;
2. vue de dessus et coupe X/Z issues de `result_view` ;
3. alertes actionnables et diagnostics ;
4. détails de score, corps, appuis, retrait et résiduels.

La palette ne force pas un changement d’onglet pendant la saisie : le focus, la
sélection et le scroll actifs restent prioritaires. `Matérialiser dans Fusion`
reste l’unique action primaire persistante de matérialisation ; elle n’est
jamais appelée par le cycle adaptatif. `Régénérer` reste borné à une scène déjà
matérialisée et à une proposition courante.

## Hauteur de conception

`Hauteur de conception` reste calculée comme hauteur intérieure Z moins le jeu Z
conteneur-boîte. Le champ :

- n’écrit aucun chemin projet ;
- reste `readonly` et `aria-readonly` ;
- est retiré de l’ordre de tabulation ;
- affiche un fond et un texte grisés avec la mention `Calculée automatiquement`.

Aucune valeur physique n’est recalibrée par cette présentation.

## Critères d’acceptation automatisés

- délais 350 ms et 1 500 ms déclarés et testés par marqueurs ;
- double garde d’obsolescence couverte ;
- action `Vérifier` absente du parcours normal ;
- fallback `Recalculer maintenant` présent ;
- exactement une action `materialize_project` dans le DOM ;
- statut et projections placés avant les détails ;
- hauteur dérivée non éditable et visiblement grisée ;
- syntaxe JavaScript, tests ciblés, suite complète, `compileall`, exemple CLI,
  frontière `adsk` du cœur et `git diff --check` passés ;
- manifest et runtime installé en 0.1.37.

## Gate humaine P44-M007V

Après intégration dans `main` et installation du package 0.1.37, Thomas vérifie
uniquement dans Fusion : stabilité pendant des éditions rapides, dernier calcul
visible, ordre de l’Aperçu, fallback manuel, hauteur grisée et absence de scène
automatique. La preuve attendue est :

```text
P44-M007 Fusion OK 0.1.37 - commit <sha>
```

Cette preuve ne valide ni les valeurs physiques, ni la géométrie imprimée, ni
l’impression. `print-validated: false` reste obligatoire.
