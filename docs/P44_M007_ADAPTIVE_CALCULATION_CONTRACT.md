# P44-M007 - Calcul adaptatif et Aperçu priorisé

Statut : implémenté et automated-validated dans le package Fusion 0.1.39 ; gate corrective P44-M007H02V requise, fusion-validated: false, print-validated: false.

## Objectif

Rendre la boucle de conception fluide sans introduire de seconde logique métier :
la palette observe les éditions, demande au cœur Python les dérivations puis la
proposition complète après stabilisation, affiche l’Aperçu avant les détails et
ne touche jamais à la scène Fusion sans action explicite.

Le retour humain sur le package 0.1.37 a révélé qu’autosave, validation et solve
reconstruisaient chacun le DOM éditable. Cette reconstruction retirait le focus,
la sélection et parfois la position de saisie. P44-M007H01 corrige cette cause
structurelle. P44-M007H02 conserve cette correction et finalise la présentation
cartes/sleeves demandée dans le même périmètre UX.

## Périmètre autorisé

- orchestration JavaScript de la palette embarquée ;
- états UI du calcul et traitement logique des réponses obsolètes ;
- hiérarchie de l’onglet Aperçu ;
- fallback manuel `Recalculer maintenant` ;
- présentation dérivée et grisée de `Hauteur de conception` ;
- rafraîchissement non destructif des faits calculés pendant l’édition ;
- présentation conditionnelle de la méthode de mesure des cartes ;
- deltas de sleeves explicites et optionnels ;
- conteneurs repliables, sans changer le modèle projet ;
- tests DOM, syntaxe, packaging et préparation de gate Fusion.

Le bridge JSON, le solveur, ses budgets, ses heuristiques, les tolérances, la
géométrie, la CAD IR et la matérialisation restent inchangés. L’extension de
`bgig.project.v1` est strictement additive pour les deux deltas de sleeves et le
Z de paquet déclaré, nécessaire pour empêcher un cumul au roundtrip.
Aucun import `adsk` n’entre dans le cœur Python.

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

## Invariant de focus P44-M007H01

Une réponse silencieuse d’autosave, de validation ou de solve ne doit jamais
appeler `renderAll()`. Elle peut mettre à jour les statuts, l’Aperçu et les
actions persistantes, mais pas remplacer les nœuds `input`, `select` ou
`textarea` de la zone éditable.

Les faits dérivés situés dans la zone éditable sont peints de manière ciblée.
Si un champ éditable est actif, cette peinture et le recalcul de la présentation
des dimensions de conteneur sont différés. Ils sont appliqués après
`focusout`, seulement quand aucun autre champ éditable n’a reçu le focus.

Un rendu complet reste autorisé après une mutation structurelle explicite :
forme, déplacement de conteneur, activation des sleeves, méthode de mesure ou
mode de dimensionnement. Les éditions ordinaires ne font que marquer le projet
sale et planifier le cycle adaptatif.

## Cartes et sleeves

Le preset intégré s’appelle `Cartes` et crée une carte non sleevée par défaut.
`Sleeves` reste une option volontaire.

Dans la première ligne, `Méthode de mesure` est placée à droite, immédiatement
avant le menu `...` :

- `Épaisseur paquet` affiche Z et masque Qté et Épaisseur carte ;
- `Épaisseur carte × nb` masque Z et affiche Qté et Épaisseur carte ;
- avec `Sleeves`, `Delta sleeve X/Y` et `Delta sleeve Z / carte` sont visibles
  dans les deux méthodes.

Lorsqu’un utilisateur active les sleeves dans la nouvelle UI, les valeurs de
départ éditables sont 3,0 mm au total sur X/Y et 0,19 mm par carte sur Z.
Elles ne sont pas une calibration physique.

En mode `thickness`, le Z saisi est conservé séparément dans le champ additif
`card_stack_declared_thickness_mm`. La quantité estimée affichée en lecture
seule est :

```text
estimated_count = max(1, floor(declared_Z / 0.31 + 0.5))
resolved_Z = declared_Z + estimated_count * sleeve_extra_z_mm_per_card
```

Ainsi, 24 mm donnent 77 cartes estimées et, avec 0,19 mm par carte, un Z résolu
de 38,63 mm. Le champ déclaré empêche tout cumul lors d’un nouveau roundtrip,
d’un autosave ou d’une réouverture. Décocher les sleeves retire les deltas du
résultat sans perdre le Z déclaré.

En mode `count`, Z reste dérivé de la quantité multipliée par l’épaisseur
d’une carte plus le delta sleeve Z par carte. Le delta X/Y reste un ajout total,
identique sur X et Y.

Compatibilité : si les deltas sont absents d’un ancien projet, le comportement
catalogue antérieur est conservé. Le normaliseur ne les injecte pas et aucune
migration silencieuse ne change ses dimensions. Le champ déclaré est ajouté
uniquement lorsque le nouveau calcul thickness+sleeves en a besoin. Les valeurs
3,0 mm, 0,19 mm et 0,31 mm restent non fusion-validated physiquement et
non print-validated.

## Conteneurs repliables

Chaque conteneur est une section repliable, de type accordéon indépendant.
Son en-tête reste toujours visible : nom, nombre d’éléments, minimum calculé,
mode, dimensions cibles éventuelles, épaisseurs, ajout et suppression. Replier
masque uniquement le détail et les assets. L’état replié est local à la palette
et n’entre pas dans le schéma projet.

## Aperçu priorisé

Pour une proposition complète ou partielle, l’ordre visible est :

1. statut compact `Prêt`, `À recalculer`, `Partiel` ou `Calcul impossible` ;
2. vue de dessus et coupe X/Z issues de `result_view` ;
3. alertes actionnables et diagnostics ;
4. détails de score, corps, appuis, retrait et résiduels.

La palette ne force pas un changement d’onglet pendant la saisie.
`Matérialiser dans Fusion` reste l’unique action primaire persistante de
matérialisation ; elle n’est jamais appelée par le cycle adaptatif.
`Régénérer` reste borné à une scène déjà matérialisée et à une proposition
courante.

## Hauteur de conception

`Hauteur de conception` reste calculée comme hauteur intérieure Z moins le jeu
Z conteneur-boîte. Le champ :

- n’écrit aucun chemin projet ;
- reste `readonly` et `aria-readonly` ;
- est retiré de l’ordre de tabulation ;
- affiche un fond et un texte grisés avec la mention `Calculée automatiquement`.

Aucune valeur physique n’est recalibrée par cette présentation.

## Critères d’acceptation automatisés

- délais 350 ms et 1 500 ms déclarés et testés par marqueurs ;
- double garde d’obsolescence couverte ;
- aucune réponse silencieuse ne reconstruit le DOM éditable ;
- peinture dérivée différée tant qu’un champ éditable est actif ;
- rerender complet limité aux mutations structurelles ;
- visibilité conditionnelle des champs cartes couverte ;
- deltas de sleeves validés et rétrocompatibilité couverte ;
- conteneurs repliables et attributs d’accessibilité couverts ;
- action `Vérifier` absente du parcours normal ;
- fallback `Recalculer maintenant` présent ;
- exactement une action `materialize_project` dans le DOM ;
- statut et projections placés avant les détails ;
- hauteur dérivée non éditable et visiblement grisée ;
- syntaxe JavaScript, tests ciblés, suite complète, `compileall`, exemple CLI,
  frontière `adsk` du cœur et `git diff --check` passés ;
- manifest et runtime installé en 0.1.39.

## Gate humaine P44-M007H02V

P44-M007H01V est supersédée avant observation par cette gate qui inclut le
correctif cartes/sleeves 0.1.39.

Après intégration dans `main` et installation du package 0.1.39, Thomas vérifie
uniquement dans Fusion :

1. saisie rapide dans plusieurs champs sans perte de focus ni de sélection ;
2. dernier calcul visible après stabilisation ;
3. preset `Cartes` non sleevé et méthode placée juste avant le menu ;
4. visibilité conditionnelle Z ou Qté/Épaisseur carte ;
5. deltas sleeves 3 mm et 0,19 mm visibles dans les deux méthodes ;
6. estimation grisée de 77 cartes pour Z = 24 mm et Z résolu = 38,63 mm ;
7. retour à Z = 24 mm après désactivation des sleeves ;
8. repli des conteneurs, ordre de l’Aperçu, fallback et hauteur grisée ;
9. absence de scène automatique.

La preuve attendue est :

```text
P44-M007H02 Fusion OK 0.1.39 - commit <sha>
```

Cette preuve qualifie l’UX et le calcul logiciel observés, mais ne calibre ni les
valeurs physiques, ni la géométrie imprimée, ni l’impression.
`print-validated: false` reste obligatoire.
