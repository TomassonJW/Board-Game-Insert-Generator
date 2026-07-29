# ADR-0107 — Campagne produit fermée et vérités reconstructibles

## Statut

Acceptée pour P64-L09W-B à P64-L09W-E.

Cette ADR ne change ni le solveur, ni les budgets, ni la grille produit, ni
l’epsilon, ni une valeur physique. Elle définit comment une future mesure peut
devenir une preuve produit honnête.

## Contexte

Les campagnes L05 à L08 ont fourni des régressions, des recettes générées, des
témoins construits, des contrôles impossibles et des runners reprenables. Leurs
holdouts ont été ouverts et sont donc consommés.

L’audit P64-L09W-A montre aussi que les fixtures historiques ne sont pas toutes
reconstructibles sous la sémantique 0.1.80 :

- trois projets L05 conservent une origine fixe d’élément plat que la
  normalisation courante retire ;
- 94 recettes L06 et 68 recettes L07 à réservation contraignante reconstruisent
  aujourd’hui un autre digest de projet ;
- le corpus L08 décrit des problèmes 3D de cœur, pas le parcours produit
  complet du projet à la matérialisation.

Réécrire silencieusement les anciens digests créerait une nouvelle vérité sous
un ancien nom. À l’inverse, compter ces dérives comme des échecs du solveur
fausserait la baseline.

## Options comparées

### Option A — Réutiliser tous les anciens manifests tels quels

Avantages :

- peu de code ;
- historique immédiatement disponible.

Refus :

- une partie des recettes ne reconstruit plus le projet engagé ;
- les holdouts sont connus ;
- les cas L08 ne prouvent pas la chaîne produit ;
- les taux obtenus mélangeraient dérive de fixture et capacité du solveur.

### Option B — Régénérer les anciens digests avec le code courant

Avantages :

- manifests à nouveau canoniques ;
- réutilisation des générateurs existants.

Refus :

- la vérité historique serait modifiée ;
- les témoins plats à origine fixe ne prouvent pas le placement automatique
  actuel ;
- les résultats L06/L07 ne seraient plus comparables à leurs preuves publiées.

### Option C — Versionner des milliers de projets et leurs témoins

Avantages :

- lecture directe ;
- dépendance réduite au générateur.

Refus :

- dépôt inutilement lourd ;
- duplication massive ;
- maintenance et revue difficiles ;
- le risque de témoins périmés demeure.

### Option D — Nouvelle campagne par recettes, engagements et ouverture unique

Chaque cas nouveau possède :

- une recette et une graine déterministes ;
- un projet effectif normalisé par le contrat courant ;
- pour un cas positif, un témoin construit indépendamment puis recertifié ;
- pour un cas négatif, une borne formelle distincte ;
- des digests séparés de recette, projet effectif, vérité et séquence
  d’édition ;
- un split fixé avant mesure.

Les anciens cas restent des régressions publiques. Le nouveau holdout est
engagé avant toute optimisation, fermé pendant discovery et tuning, puis ouvert
une seule fois pour un candidat gelé.

Cette option est retenue.

## Décision

### 1. Trois classes de fixtures historiques

Une fixture existante est classée avant exécution :

1. `current-reconstructible` : la reconstruction courante reproduit tous les
   digests engagés ;
2. `historical-semantic-drift` : la source reste utile pour l’audit, mais son
   projet ou sa vérité ne sont plus reconstructibles à l’identique ;
3. `core-only` : la vérité reste reconstruite, mais elle ne traverse pas le
   parcours produit complet.

Seule la première classe contribue à un taux produit courant. La deuxième
contribue au diagnostic de maintenance, jamais au dénominateur du solveur. La
troisième publie un taux de cœur séparé.

Les manifests L05 à L08 restent immuables.

La validation de leur reçu historique est distincte de leur reconstructibilité
courante. Le validateur peut conserver un ancien `origin_mm` manuel seulement
si :

- le digest du projet stocké et le digest du corpus sont exacts ;
- le projet reste valide ;
- la seule différence avec la normalisation courante est la migration connue
  de cet `origin_mm` vers `None`.

Cette compatibilité prouve l’intégrité du reçu, pas sa vérité produit actuelle.
La classification `historical-semantic-drift` reste obligatoire avant toute
mesure.

### 2. Vérité positive indépendante

Le générateur P64-L09W-B construit d’abord un placement complet sans appeler le
solveur évalué. Il dérive ensuite le projet présenté au solveur, retire le
témoin de l’entrée, puis recertifie ce témoin avec le certificateur BGIG
courant.

Un cas positif n’est publié que si cette reconstruction reproduit :

- le digest de recette ;
- le digest du projet normalisé ;
- le digest du témoin ;
- le digest du certificat de vérité.

Un timeout, un épuisement heuristique ou un échec de reconstruction ne devient
jamais une preuve d’impossibilité.

### 3. Contrôles impossibles séparés

Les cas négatifs possèdent une borne géométrique formelle vérifiable sans
résultat du solveur. Ils forment un contrôle séparé et ne sont pas mélangés au
taux de récupération des cas faisables.

Une réponse `impossible` sur un cas positif est un faux impossible et invalide
la candidate. Une absence de solution dans la limite reste
`bounded_unknown`.

### 4. Jeux et autorité

- `regression` : fixtures historiques reconstructibles et défauts corrigés ;
- `discovery` : localisation des pertes ;
- `tuning` : comparaison des hypothèses retenues ;
- `holdout` : cas nouveaux engagés avant optimisation et ouverts une fois ;
- `soak` : grande campagne déterministe, reprenable et hors gate courte.

Discovery et tuning peuvent exposer leurs recettes et témoins. Le solveur ne
reçoit jamais les témoins. Le holdout ne peut être lu par un runner de
discovery ou de tuning.

L’ouverture exige un candidat unique engagé par commit, configuration, limites
et digest. Un reçu d’ouverture irréversible est écrit avant la première
exécution. Après ouverture, aucune retouche n’est autorisée ; une nouvelle
itération demande un nouveau holdout.

### 5. Unité de résultat

Chaque ligne de résultat engage au minimum :

- l’identité du cas, sa strate et son split ;
- les digests de recette, projet, vérité, configuration et résultat ;
- le statut honnête ;
- la route et les limites réellement utilisées ;
- les compteurs de recherche et de certification ;
- les temps séparés et la mémoire de pointe ;
- les résultats de finalisation et de CAD IR lorsqu’une solution est
  certifiée ;
- la matérialisation comme phase distincte, ou explicitement
  `not-measured-offline`.

Les métriques volatiles ne participent jamais à un digest fonctionnel.

## Conséquences

### Positives

- aucune dérive historique n’est maquillée en résultat solveur ;
- le futur taux de succès porte sur une distribution déclarée ;
- les vérités restent indépendantes du moteur évalué ;
- l’ouverture unique empêche le réglage sur le holdout ;
- les coûts aval ne peuvent pas être absorbés dans le seul temps de calcul.

### Coûts

- un nouveau générateur produit et un nouveau schéma de résultats sont
  nécessaires ;
- la reconstruction, le certificat de vérité et les engagements ajoutent une
  gate avant chaque exécution ;
- la matérialisation Fusion demande un échantillon séparé après le verdict
  hors ligne.

### Risques

- une distribution trop régulière pourrait rester facile à suradapter ;
- un taux global pourrait masquer une famille faible ;
- une ouverture accidentelle du holdout le consommerait.

Ces risques sont fermés par les strates préenregistrées, les résultats par
famille, les minima de couverture, les contrôles de split du runner et le reçu
d’ouverture unique.

## Gate d’implémentation

P64-L09W-B est acceptable seulement si :

1. les anciens manifests restent bit à bit inchangés ;
2. toute vérité positive est reconstruite et recertifiée ;
3. tout cas négatif possède une borne indépendante ;
4. les splits sont disjoints par digest de projet et de vérité ;
5. le holdout ne fournit aucun témoin au solveur et n’est pas exécuté ;
6. les budgets, grilles, epsilon et valeurs physiques restent inchangés ;
7. le générateur et le runner sont déterministes, testés et reprenables.
