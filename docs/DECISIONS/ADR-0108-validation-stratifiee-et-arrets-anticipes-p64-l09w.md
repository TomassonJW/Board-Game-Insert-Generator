# ADR-0108 — Validation stratifiée et arrêts anticipés P64-L09W

## Statut

Acceptée le 2026-07-30 pour la reprise P64-L09W-D à F.

Thomas demande explicitement de réduire fortement le temps et les tokens, de
préserver les preuves déjà acquises, de garder le holdout fermé jusqu’à E et de
ne l’ouvrir qu’une seule fois.

## Contexte

La campagne D complète prévue par C devait rejouer les 400 cas ouverts deux
fois. Elle est arrêtée proprement après 39 cas, avec 361 cas restants, 18
résultats prêts contre 8 en C et aucune régression observée d’un résultat déjà
prêt.

Le changement D courant ne modifie que la finalisation composite XY après une
solution minimale certifiée. Il ne change ni la recherche, ni les budgets, ni
la grille, ni l’epsilon, ni une valeur physique. Rejouer mécaniquement les 361
cas restants testerait surtout des chemins que ce changement ne peut pas
affecter.

La référence C contient :

- 61 résultats déjà prêts hors Fusion, dont 8 déjà rejoués dans D ;
- 237 pertes `xy_composite_residual_owner_not_found`, dont 25 déjà rejouées ;
- 332/400 solutions certifiées, dont 200/240 dans `common`.

Le candidat courant ne peut donc pas, par construction, transformer 332 en
380 solutions certifiées ou 200 en 238 résultats `common`. Ouvrir E après ce
seul changement consommerait le holdout sans possibilité de passer les seuils.

## Options

### A — Terminer les 361 cas

Refusée pour le changement D courant :

- 722 replays supplémentaires ;
- coût élevé sur la longue traîne `stress` ;
- faible pouvoir causal sur un changement limité à la finalisation ;
- aucune amélioration possible du nombre de solutions minimales certifiées.

### B — Échantillon opportuniste rapide

Refusée :

- risque de sélectionner seulement les cas faciles ;
- absence de couverture prouvée des axes ;
- aucune garantie sur les 61 résultats déjà prêts ;
- risque de transformer un échantillon de diagnostic en taux trompeur.

### C — Validation stratifiée déterministe et arrêts anticipés

Retenue :

- conserver les 39 résultats D déjà checkpointés sous le même bundle ;
- imposer les deux cas causaux `common` et `stress` ;
- rejouer tous les 61 résultats C déjà prêts, une fois lorsque D ne les a pas
  déjà exécutés ;
- rejouer deux fois un échantillon causal de huit cas `common` et huit cas
  `stress`, couvrant toutes les valeurs observées sur les axes choisis et les
  quantiles de temps 10 %, 50 % et 90 % ;
- arrêter immédiatement sur une régression ou une preuve invalide ;
- ne tirer aucun taux de réussite de cet échantillon.

## Décision

### D — preuve ciblée

Les 361 cas restants sont **non nécessaires** pour décider du changement de
finalisation courant. Ils sont remplacés par le plan
`bgig.p64_l09w_d_stratified_validation_plan.v1`.

Le plan local autoritaire est dérivé des checkpoints C et D et ne possède aucun
argument de holdout. Il doit publier `sample_is_rate_estimator=false`.

Une différence sur un résultat déjà prêt déclenche un second replay de
diagnostic puis un arrêt. Elle ne peut pas être moyennée avec les gains.

Un non-déterminisme déjà présent dans C n’est pas imputé à D. Il reste publié
comme dette préexistante et n’est acceptable que si le statut, la signature
solveur, la route et le placement du premier replay restent identiques. Le
digest fonctionnel aval peut changer lorsque la finalisation ciblée réussit.
L’apparition d’un nouveau non-déterminisme sur une référence déterministe reste
un arrêt dur.

### E — holdout intact

Le holdout reste fermé tant qu’un candidat ne peut pas raisonnablement atteindre
les seuils gelés. Le changement de finalisation D courant ne satisfait pas cette
précondition.

Quand un candidat unique sera admissible, E :

1. engage commit, configuration, limites, bundle et ordre des cas ;
2. écrit le reçu irréversible avant le premier solve ;
3. ouvre le holdout une seule fois ;
4. exécute d’abord un replay primaire ;
5. s’arrête dès que plus de 2 cas `common` échouent, plus de 20 cas globaux
   échouent, ou qu’une invalidation dure apparaît ;
6. n’exécute le second replay complet que si le premier conserve encore la
   possibilité de passer.

Une réussite E exige toujours la totalité des 400 cas et leur replay. Un
échantillon ne peut jamais justifier 380/400 ou 238/240.

### F — strictement conditionnelle

F est exécutée uniquement si un changement produit est réellement retenu et si
E autorise une candidate. Sans changement retenu, ou après rejet du candidat,
F est omise. Aucune candidate Fusion ni recette humaine n’est créée pour
compenser un verdict E négatif.

## Conséquences

### Positives

- forte réduction du coût D sans masquer une régression déjà connue ;
- couverture déterministe des deux strates et des axes causaux ;
- holdout protégé contre une ouverture manifestement futile ;
- seuils E inchangés ;
- F ne consomme du temps que pour une candidate réelle.

### Limites

- D ne mesure plus un taux global ouvert après ce seul changement ;
- l’échantillon causal ne prouve pas que les 237 pertes sont toutes corrigées ;
- un passage E reste coûteux lorsqu’il réussit, car les seuils exigent les
  400 cas et le replay ;
- une future optimisation de recherche devra recevoir son propre plan causal
  avant de rendre E admissible.

## Gate

Le recadrage est valide seulement si :

1. le plan est dérivé des checkpoints intacts C et D ;
2. les 61 résultats prêts sont tous présents ;
3. les deux cas causaux sont présents ;
4. chaque strate couvre toutes les valeurs observées sur les axes sélectionnés ;
5. aucune lecture ou invocation holdout n’est possible dans le planificateur ;
6. les règles d’arrêt et l’absence de revendication de taux sont testées ;
7. le checkpoint D original reste inchangé avant toute nouvelle campagne.
