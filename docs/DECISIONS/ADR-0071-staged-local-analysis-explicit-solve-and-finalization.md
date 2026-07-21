# ADR-0071 — Analyse locale réactive, solvage explicite et finalisation séparée

## Statut

Acceptée le 2026-07-21 comme architecture produit future, sur validation humaine
explicite. Cette décision est documentaire : elle ne modifie pas encore le
runtime 0.1.55, ne ferme pas P64-V2H03V et ne rend aucune mission P45/P46 prête.

## Date

2026-07-21

## Cartes liées

- `P64-A02 — Calcul étagé et réutilisation de capacité` ;
- `P64-L01 — État dérivé incrémental et cache local` ;
- `P64-L02 — Frontières locales, scores et résumé progressif` ;
- `P64-L03 — Solvage global explicite et progressive widening` ;
- `P64-L03V — Gate Fusion du cycle de calcul étagé` ;
- `P64-F01` à `P64-F03` pour la finalisation du volume ;
- `P45-M001` pour les sémantiques de disposition et futures formes.

## Contexte

ADR-0056 avait retenu quatre états `source`, `derived`, `solved` et
`materialized` : une édition devait recalculer seulement les dérivés rapides,
rendre l'ancien plan obsolète et laisser le solveur global explicite.
P44-M007 a ensuite privilégié la fluidité perçue en lançant automatiquement
`validate_project` après 350 ms puis `solve_project` après 1 500 ms de stabilité.

Cette orchestration est robuste contre les réponses obsolètes, mais elle relance
une recherche globale alors que la personne peut encore modifier plusieurs
assets ou conteneurs. Elle confond également trois coûts et trois intentions :

- résoudre un asset et ses dimensions physiques ;
- explorer les dispositions internes d'un conteneur ;
- placer tous les conteneurs et finaliser le volume de la boîte.

P64-V2H03B fournit désormais une frontière locale certifiée, déterministe et
bornée par conteneur. P64-V2H03C sait consommer ces variantes paresseusement
pendant le placement global. ADR-0069 sépare déjà faisabilité et finition. Le
produit peut donc exposer un cycle plus explicite sans déplacer de logique dans
JavaScript ou Fusion.

Contraintes non négociables :

- le cœur Python reste la source de vérité et ne dépend pas d'`adsk` ;
- aucune édition ne matérialise ou ne régénère automatiquement la scène ;
- un cache ne devient jamais une source projet ni un certificat implicite ;
- un résultat lié à une ancienne révision reste obsolète et non matérialisable ;
- une limitation de shortlist ne peut pas transformer un échec heuristique en
  impossibilité ;
- les cavités, jeux, parois minimales, fonds et réservations ne changent pas par
  effet de score ou de finition ;
- les chemins baseline, EMS, greedy, beam et les efforts monotones restent
  disponibles.

## Options

### Option A — Conserver le solve automatique complet

- Avantage : aucun clic supplémentaire lorsque le projet est petit.
- Inconvénient : recherches répétées pendant une séquence d'édition et coût peu
  prévisible.
- Risque : bruit CPU, réponses obsolètes, impression que chaque saisie produit
  déjà une solution globale.

### Option B — Désactiver tout calcul automatique

- Avantage : comportement totalement explicite.
- Inconvénient : dimensions résolues, erreurs locales et possibilités de
  conteneur resteraient anciennes jusqu'à une action manuelle.
- Risque : boucle d'édition lente et erreurs découvertes trop tard.

### Option C — Analyse locale réactive, solvage global explicite, finalisation séparée

- Avantage : retour local rapide, réutilisation des calculs, contrôle humain du
  coût global et séparation honnête des statuts.
- Inconvénient : état produit et invalidation plus détaillés.
- Risque : incohérence de cache si les dépendances ne sont pas contractualisées.

## Décision

Retenir l'option C.

### Cycle produit cible

```text
source éditée
  -> analyses locales courantes
  -> agencement global courant
  -> plan finalisé courant
  -> scène Fusion matérialisée depuis ce plan précis
```

Une édition déclenche automatiquement seulement les analyses locales et les
bornes contextuelles rapides. Elle rend `global_layout`, `finalized_plan` et la
matérialisabilité obsolètes. Elle conserve l'ancien aperçu en lecture seule et
grisé jusqu'au prochain solvage explicite.

Le bouton primaire suit l'état courant :

1. `Calculer l'agencement` ;
2. `Finaliser le volume` ;
3. `Matérialiser dans Fusion`.

Les trois actions restent conceptuellement distinctes, même si l'interface n'en
affiche qu'une comme prochaine action primaire.

### Analyse locale intrinsèque et annotation contextuelle

La dérivation locale intrinsèque dépend des assets du conteneur, de leurs poses,
quantités, jeux internes, parois, cloisons, fonds et modes locaux. Elle produit
une frontière immuable certifiée sans connaître le placement monde.

Une annotation contextuelle légère applique ensuite boîte, hauteur utile et
réservations supérieures sans modifier l'identité locale. La compatibilité sous
plateau est au minimum ternaire : `compatible`, `conditionnelle` ou
`incompatible`. Une réservation localisée ne peut pas devenir un booléen local
mensonger.

### Invalidation par dépendances

- un asset invalide sa résolution, son conteneur, l'agencement et la finalisation ;
- un conteneur invalide sa frontière, l'agencement et la finalisation, jamais
  les mesures sources de ses assets ;
- un déplacement d'asset invalide les deux conteneurs ;
- la boîte ou une réservation invalide les annotations contextuelles de tous les
  candidats et les étapes globales, mais peut réutiliser leurs géométries
  intrinsèques ;
- un default global invalide uniquement les objets qui l'héritent ;
- un override local invalide uniquement son objet propriétaire ;
- un changement de méthode, effort ou classement invalide l'agencement, pas les
  sources ;
- un changement de politique de finition invalide seulement la finalisation.

Chaque artefact porte son propre digest, la version de son producteur et les
digests exacts de ses dépendances. Le cache est fail-closed : clé absente,
version différente ou dépendance inconnue signifie recalcul, jamais réutilisation
supposée.

### Frontière, shortlist et score

Le moteur conserve une frontière de Pareto bornée. L'interface peut résumer
trois candidats représentatifs — compact, équilibré et bas — mais le solveur
n'est jamais limité définitivement à ces trois entrées.

Le solvage global utilise un élargissement progressif : il commence par une
petite sélection diverse, puis ouvre paresseusement davantage de variantes selon
le profil d'effort. Rapide reste un préfixe de Normal, lui-même préfixe
d'Approfondi.

Le score local reste décomposé : enveloppes X/Y/Z, volume extérieur, aire,
efficacité d'enveloppe, aspect, hauteur, nombre de rangées/cloisons et
compatibilités réellement mesurées. Il ordonne et explique ; il ne certifie pas
le placement global et ne revendique ni accessibilité, ni matière, ni
imprimabilité sans métrique correspondante.

### Parois et cloisons

Le premier incrément réutilise `layout.default_wall_thickness_mm` et
`container_groups[].wall_thickness_mm`, déjà globaux avec override local. Il ne
crée pas un champ doublon.

Une éventuelle séparation future entre paroi extérieure et cloison interne
appartient à P45 et exige un contrat géométrique, une migration additive, des
minima fail-closed et une validation physique. Par défaut, une future cloison
distincte hériterait de la paroi du conteneur.

### Solvage et finalisation

`Calculer l'agencement` choisit variantes et placements, classifie le résiduel
et produit un certificat de placement. Il ne promet pas encore un plan final
matérialisable si le volume imprimable reste non attribué ou instable.

`Finaliser le volume` applique une stratégie explicitement choisie : expansion
des enveloppes, cales explicites, hybride ou réserve utile autorisée. La
politique de distribution peut être simple, équilibrée ou proportionnelle. Les
transformations portent leur propre budget et repassent par le validateur
commun. Seul un plan final certifié active la matérialisation.

La conservation du volume porte sur le volume allocable après retrait des jeux
et réservations. Les vides techniques restent des vides. Une réserve utile est
intentionnelle, nommée et certifiée ; elle n'est jamais un résiduel oublié.

### Compatibilité avec les décisions existantes

- ADR-0056 est réaffirmée et étendue avec un état `finalized` explicite.
- Le solve automatique P44-M007 reste le runtime courant jusqu'à une mission et
  une gate dédiées ; cette ADR le supersédera uniquement après validation.
- ADR-0054 conserve les cavités fixes, enveloppes extensibles et l'interdiction
  des corps automatiques ; la décision de finition devient explicite dans le
  cycle utilisateur.
- ADR-0069 conserve la finition post-faisabilité et ses fallbacks.
- ADR-0070 conserve la propriété P45/P64 et les deux certificats.

## Conséquences

### Positives

- les éditions ordinaires ne relancent plus le coût global ;
- les conteneurs non touchés réutilisent leurs frontières certifiées ;
- le résultat obsolète, le placement et la finalisation deviennent distincts ;
- les scores locaux aident le solveur sans devenir une vérité globale ;
- l'UX rend chaque coût et chaque mutation explicite.

### Négatives

- les digests, dépendances et statuts sont plus nombreux ;
- l'utilisateur effectue une action supplémentaire avant matérialisation ;
- l'ancien contrat DOM adaptatif doit être amendé et revalidé dans Fusion.

### Risques et mitigations

- cache obsolète : digests de dépendances, version de producteur et fail-closed ;
- shortlist trop agressive : diversité et progressive widening ;
- score opaque : sous-scores et raisons obligatoires ;
- surcharge de boutons : une seule prochaine action primaire contextuelle ;
- calcul local futur trop cher : caps, annulation, stale et enrichissement
  progressif pendant l'inactivité.

## Alternatives refusées

- conserver le solve complet automatique comme unique parcours ;
- supprimer toutes les dérivations réactives ;
- persister les caches ou variantes comme vérité utilisateur implicite ;
- limiter le moteur au top 3 visible ;
- permettre la matérialisation d'un placement non finalisé ;
- ajouter un nouveau paramètre de cloison sans contrat P45 et preuve physique.

## Suivi

- Contrat détaillé :
  `docs/P64_STAGED_CALCULATION_AND_FINISHING_PROGRAM.md`.
- La carte P64-A02 clôt uniquement l'architecture documentaire.
- P64-L01 est automated-validated ; P64-L02 devient ready ; P64-L03 reste
  bloquée par L02 et sa future gate.
- Toute mutation runtime exige tests purs, DOM, bridge, stale/annulation,
  monotonie, suite complète et gate Fusion P64-L03V.
- `fusion-validated: false` et `print-validated: false` pour cette trajectoire.
