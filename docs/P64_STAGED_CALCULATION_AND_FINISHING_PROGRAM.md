# P64-A02 — Programme de calcul étagé et finalisation explicite

Statut : architecture acceptée le 2026-07-21 ; documentation validée seulement.
Runtime courant inchangé : P44-M007 continue de programmer le solve automatique
tant que P64-L03/L03V n'ont pas été implémentés et observés dans Fusion.

ADR principale :
[ADR-0071](DECISIONS/ADR-0071-staged-local-analysis-explicit-solve-and-finalization.md).
ADR liées : ADR-0054, ADR-0056, ADR-0068, ADR-0069 et ADR-0070.

Capability principale : `C-USABILITY`. Capabilities associées : `C-ASSET`,
`C-GEOMETRY`, `C-SOLVER`, `C-LAYOUT`, `C-QUALITY`, `C-FUSION-UI`.

## 1. Résultat produit attendu

Le parcours cible sépare quatre décisions visibles :

```text
Éditer
  -> analyser localement
  -> calculer l'agencement global
  -> finaliser le volume
  -> matérialiser dans Fusion
```

Pendant l'édition, BGIG met à jour les dimensions, erreurs et possibilités du
seul périmètre affecté. Il ne relance pas le portefeuille global. La personne
peut modifier plusieurs valeurs sans déclencher une succession de recherches
devenues obsolètes.

Le solveur global utilise ensuite des frontières locales déjà certifiées et
mises en cache. La finalisation transforme seulement un placement global
valide. Fusion consomme exclusivement un plan final courant et ne recalcule
aucune décision.

## 2. Non-objectifs immédiats

- aucun runtime dans P64-A02 ;
- aucune modification de `bgig.project.v1` dans le lot documentaire ;
- aucune suppression immédiate du cycle P44-M007 ;
- aucun nouveau default physique, jeu ou tolérance ;
- aucune forme P45 anticipée ;
- aucune promesse d'optimalité locale ou globale ;
- aucune grille dense, dépendance externe ou moteur exact ;
- aucun corps, séparateur, cale ou scène automatique ;
- aucune revendication Fusion ou impression.

## 3. Modèle d'état cible

### `source`

Mesures, quantités, affectations, poses, contraintes, defaults et overrides
explicitement édités. Une mutation source incrémente la révision du projet.

### `local_analysis`

Collection d'analyses indépendantes :

- résolution d'assets ;
- frontière intrinsèque par conteneur ;
- annotations contextuelles boîte/plateaux ;
- scores et diagnostics ;
- bornes globales nécessaires rapides.

Une analyse locale peut être courante pour un conteneur et obsolète pour un
autre. Le statut dérivé n'est plus seulement un booléen projet.

### `global_layout`

Résultat d'une action explicite `Calculer l'agencement`. Il choisit exactement
une variante par conteneur, place tous les participants ou rapporte un arrêt
honnête, puis classifie le résiduel. Il porte un certificat de placement et son
digest de dépendances.

### `finalized_plan`

Résultat d'une action explicite `Finaliser le volume`. Il applique une politique
de fermeture, d'harmonisation, de réserve utile ou de cales explicites, puis
repasse par le validateur commun. Lui seul peut devenir matérialisable.

### `materialized`

Scène Fusion issue d'un digest précis de `finalized_plan`. Toute mutation source
ou finalisation différente rend la scène désynchronisée sans la modifier.

## 4. Digests et cache

Le cache reste interne et reconstructible. Les clés minimales sont :

```text
AssetResolutionKey
  asset_source_digest
  inherited_asset_defaults_digest
  resolver_id + resolver_version

ContainerFrontierKey
  container_source_digest
  ordered_member_asset_resolution_digests
  inherited_container_defaults_digest
  producer_set_digest
  effort_profile

ContextAnnotationKey
  container_frontier_digest
  box_context_digest
  top_reservation_digest

GlobalLayoutKey
  ordered_frontier_digests
  box_context_digest
  solver_method + effort + ranking

FinalizationKey
  global_layout_digest
  finishing_policy + finishing_budget
```

Règles :

1. aucune clé partielle n'est acceptée ;
2. un changement de version invalide l'entrée ;
3. les caches ne participent pas au fichier projet ;
4. les résultats obsolètes peuvent rester visibles mais jamais consommables ;
5. les réponses portent révision source et identité de requête ;
6. une réponse tardive ne peint jamais un état courant ;
7. l'éviction du cache change seulement la performance, jamais le résultat.

## 5. Matrice d'invalidation normative

| Mutation | Asset | Frontière locale | Contexte boîte | Agencement | Finalisation | Scène |
| --- | --- | --- | --- | --- | --- | --- |
| Dimension/quantité/pose d'un asset | asset seul | conteneur propriétaire | ce conteneur | obsolète | obsolète | désynchronisée |
| Jeu de cavité d'un asset | asset seul | conteneur propriétaire | ce conteneur | obsolète | obsolète | désynchronisée |
| Paramètre local de conteneur | inchangé | ce conteneur | ce conteneur | obsolète | obsolète | désynchronisée |
| Asset déplacé | asset courant | ancien + nouveau conteneur | les deux | obsolète | obsolète | désynchronisée |
| Dimensions de boîte | réutilisable | réutilisable si intrinsèque | tous | obsolète | obsolète | désynchronisée |
| Plateau/livret | réutilisable | réutilisable | tous les recouvrements possibles | obsolète | obsolète | désynchronisée |
| Default asset | héritiers | conteneurs propriétaires | concernés | obsolète | obsolète | désynchronisée |
| Default paroi/fond | inchangé | conteneurs héritiers | concernés | obsolète | obsolète | désynchronisée |
| Override local | propriétaire | propriétaire | propriétaire | obsolète | obsolète | désynchronisée |
| Méthode/effort/classement | inchangé | réutilisable ou étendu | inchangé | obsolète | obsolète | désynchronisée |
| Politique de finition | inchangé | inchangé | inchangé | courant | obsolète | désynchronisée |

`Réutilisable` signifie que le digest intrinsèque reste valide. L'annotation
contextuelle est toujours reconstruite quand boîte ou réservation change.

## 6. Analyse locale automatique

Une édition ordinaire suit cette chaîne bornée :

1. normaliser le fragment source concerné ;
2. résoudre l'asset si nécessaire ;
3. reconstruire la frontière du conteneur si sa clé a changé ;
4. certifier, dédupliquer et éliminer les variantes dominées ;
5. annoter la compatibilité avec la boîte et les réservations ;
6. mettre à jour le résumé local sans reconstruire le DOM éditable ;
7. marquer agencement et finalisation obsolètes ;
8. enrichir éventuellement la frontière pendant l'inactivité.

Le calcul local n'est pas « illimité ». Il utilise les caps H03B comme point de
départ mesuré et peut définir des caps spécifiques après benchmark. Un futur
producteur P45 plus coûteux doit déclarer ses propres limites.

## 7. Enrichissement progressif

Trois profondeurs sont distinguées :

- `aperçu local` : minima, canonique et petite frontière diverse ;
- `analyse locale étendue` : davantage de variantes pendant l'inactivité ou sur
  demande ;
- `expansion de solvage` : ouverture paresseuse pilotée par l'effort global.

Une analyse plus profonde ne supprime jamais une variante déjà certifiée d'un
préfixe moins profond. Elle peut ajouter des variantes ou enrichir les raisons.

Le temps mural reste une métrique, pas le contrat. Les limites de variantes,
états et essais sont le contrat observable.

## 8. Frontière et shortlist visible

La frontière interne reste plus large que la shortlist UI. Le résumé montre au
maximum trois représentants :

1. `Compact` : faible volume extérieur parmi les candidats certifiés ;
2. `Équilibré` : faible pénalité d'aspect et axes moins extrêmes ;
3. `Bas` : faible Z et meilleure compatibilité contextuelle sous plateau.

Si deux profils désignent la même géométrie, le résumé ne duplique pas la carte
et indique plusieurs qualités. Le diagnostic secondaire peut exposer toute la
frontière retenue.

Le solveur global commence par une sélection diverse, pas obligatoirement les
trois cartes peintes. En cas d'échec, il ouvre les options suivantes dans la
limite de l'effort. Une shortlist UI ne change donc jamais la sémantique
`no_solution_within_budget`.

## 9. Score local explicable

Avant scoring, les contraintes dures éliminent les variantes invalides. Le score
compare seulement des candidats certifiés.

Sous-scores minimaux :

| Sous-score | Mesure | Ne prouve pas |
| --- | --- | --- |
| `envelope_efficiency` | volume contracté des cavités / volume extérieur minimal | matière imprimée |
| `volume_mm3` | X × Y × Z de l'enveloppe minimale | disposition globale |
| `footprint_area_mm2` | X × Y | compatibilité plateau complète |
| `aspect_penalty` | écart logarithmique entre X et Y | ergonomie |
| `height_mm` | Z minimal | retrait ou support |
| `layout_complexity` | rangées, cloisons, changements de coupe | imprimabilité physique |
| `box_axis_fit` | orientations tenant par axe dans la boîte | placement multi-conteneurs |
| `top_context` | compatible, conditionnelle, incompatible par réservation | certificat global |

Un total UI éventuel reste une projection expliquée. Le vecteur, la Pareto et
les raisons sont l'autorité interne.

## 10. Compatibilité sous plateaux et livrets

Chaque candidat porte par réservation :

- `compatible` : il reste sous le plan d'appui pour tout recouvrement admissible ;
- `conditional` : une position, rotation ou coupe localisée peut fonctionner ;
- `incompatible` : aucun cas localement admissible ne respecte hauteur, cavités
  et fond ;
- `unknown` : information insuffisante ou budget atteint.

Le statut ne modifie ni le digest de géométrie locale, ni la certification
locale. La position finale et le validateur global restent autoritaires.

## 11. Parois, cloisons et defaults

Le comportement existant reste normatif au premier incrément :

- `layout.default_wall_thickness_mm` est le minimum global ;
- `container_groups[].wall_thickness_mm = null` signifie héritage ;
- une valeur locale positive remplace le default pour ce conteneur ;
- la même valeur borne actuellement parois extérieures et cloisons internes ;
- les épaisseurs restent des minima non calibrés physiquement.

UX cible : le résumé compact conserve `Parois : Défaut` ou la valeur locale. Un
détail replié explique que les cloisons héritent du même minimum.

Une séparation `external_wall_thickness_mm` / `internal_divider_thickness_mm`
est seulement une option P45 future. Elle exige ADR, migration additive,
provenance visible et coupons physiques ; elle n'est pas créée par P64-A02.

## 12. Bornes globales réactives autorisées

Après édition, BGIG peut recalculer sans bouton des conditions nécessaires très
rapides :

- somme des volumes minimaux contre volume utile ;
- plus grande dimension par axe et orientation autorisée ;
- hauteur minimale et plans de réservation ;
- nombre de conteneurs sans candidat local certifié ;
- état courant/obsolète des analyses.

Ces bornes alimentent un indicateur de santé du projet. Elles ne lancent aucun
placement et ne produisent jamais `proven_impossible` hors contradiction formelle
explicitement couverte.

## 13. Action `Calculer l'agencement`

Préconditions :

- source normalisée ;
- aucune erreur locale bloquante ;
- frontières minimales courantes ou reconstructibles ;
- méthode et effort connus ;
- aucune requête globale identique déjà active.

Le run :

1. fige les digests de dépendances ;
2. exécute les lanes canoniques préservées ;
3. ouvre les variantes selon progressive widening ;
4. compare seulement les candidats complets admis ;
5. classifie le résiduel et les contraintes de finalisation ;
6. produit `solution_found`, `no_solution_within_budget`, `proven_impossible`,
   `invalid_input` ou `stale_or_cancelled` selon ADR-0068 ;
7. n'active jamais directement Fusion.

Le résultat est `placement-certifié` seulement si tous les participants et
contraintes de placement passent. Il peut rester `à finaliser` si le résiduel
allocable n'a pas encore reçu de politique.

## 14. Action `Finaliser le volume`

La première décision choisit la nature de la finalisation :

- `Agrandir les conteneurs` ;
- `Cales explicites` ;
- `Hybride` ;
- `Réserve utile`, lorsque le contrat P64-C03 l'autorise.

Pour l'agrandissement, la seconde décision choisit l'objectif :

### Fermeture simple

Absorber le résiduel par faces entières en minimisant opérations, fragmentation
et changement relatif. C'est le candidat par défaut le plus robuste.

### Répartition équilibrée

Viser une quantité absolue similaire de volume extérieur ajouté par conteneur,
sous caps de déformation. Le volume impossible à attribuer à un conteneur est
redistribué sans violer les contraintes.

### Répartition proportionnelle

Viser un ratio similaire `volume final / volume minimal`, ce qui tend à donner
le même taux de croissance. La référence est le volume extérieur, jamais le
volume de matière plastique.

### Alignement structurel futur

Privilégier plans communs, hauteurs et trames locales. Cette politique reste
P64-F02 et n'est pas implicitement fusionnée aux trois premières.

Toutes les politiques :

- préservent cavités, jeux, minima et axes Fixe ;
- ne comptent pas les jeux comme volume à absorber ;
- produisent un score et des raisons ;
- ont un budget propre ;
- conservent le placement de base si la transformation échoue ;
- requièrent un nouveau certificat avant matérialisation.

## 15. Cales et formes spéciales

Minimiser seulement le nombre de cales est insuffisant. Le classement est :

1. constructibilité contractuelle ;
2. retrait et manipulation ;
3. stabilité ;
4. géométrie simple ;
5. nombre de pièces ;
6. matière estimée seulement si la mesure est implémentée.

P64-F03 ne crée une cale qu'après action explicite. Les formes spéciales
d'encastrement, nervures ou mécanismes dépendent de P45/P46 et d'une preuve
physique ; elles ne sont pas un fallback automatique.

## 16. UX progressive

### Parcours normal

- l'en-tête du conteneur montre minimum, nombre de variantes et meilleur résumé ;
- un détail `Possibilités d'agencement` reste fermé ;
- l'ancien résultat global est grisé après édition ;
- la barre persistante montre une seule prochaine action primaire ;
- méthode et effort restent dans Réglages ou un détail avancé ;
- aucun diagnostic technique n'est peint dans les cartes ordinaires.

### Parcours expert

- frontière locale, sous-scores, digests et rejets ;
- compatibilités par réservation ;
- budgets locaux et globaux ;
- cache hit/miss et causes d'invalidation ;
- progressive widening et motif d'arrêt ;
- statistiques de finalisation.

### Libellés d'état

- `Analyse locale en cours` ;
- `Possibilités à jour` ;
- `Agencement à recalculer` ;
- `Calcul de l'agencement en cours` ;
- `Agencement trouvé — finalisation requise` ;
- `Plan final prêt` ;
- `Scène Fusion désynchronisée`.

## 17. Télémétrie minimale

- révision et digests source/local/contexte/global/final ;
- objets invalidés et raison ;
- cache hits, misses et versions ;
- variantes générées, certifiées, dominées et retenues par conteneur ;
- candidats visibles et représentants choisis ;
- durée et caps des analyses locales ;
- lanes, états, essais et progressive widening global ;
- politique, itérations et résiduel de finalisation ;
- annulation, stale, timeout ou certificat obtenu.

La télémétrie ne contient ni chemin local sensible, ni contenu de document
Fusion non BGIG.

## 18. Fixtures obligatoires

1. modifier un asset : seul son conteneur perd son digest local ;
2. modifier un conteneur : les mesures sources de ses assets restent stables ;
3. déplacer un asset : exactement deux frontières sont invalidées ;
4. changer la boîte : géométries locales réutilisées, contextes tous renouvelés ;
5. changer un default : seuls les héritiers sont invalidés ;
6. override local : aucun voisin non concerné n'est recalculé ;
7. top 3 UI : échec initial puis succès après élargissement interne ;
8. compatibilité plateau ternaire et réservation localisée ;
9. ancienne réponse locale ignorée après nouvelle frappe ;
10. solve global jamais lancé automatiquement après édition ;
11. ancien placement visible mais non matérialisable ;
12. trois politiques de répartition avec contraintes asymétriques ;
13. échec de finalisation : placement de base conservé ;
14. mutation pendant solve/finalisation : `stale_or_cancelled` ;
15. projet 11 × 34 : arrêt borné et statut honnête ;
16. scène inchangée avant action explicite.

## 19. Découpage des missions

### P64-A02 — Architecture et pilotage

- Statut après intégration : `done-documentation`, `architecture-accepted`.
- Livrables : ADR-0071, ADR-0072, ce programme, contrat capacité, roadmap,
  backlog, gates, capabilities, tests documentaires et log.
- Runtime : aucun.

### P64-L01 — État dérivé incrémental et cache local

- Statut : `done-code`, `implemented-core`, `automated-validated` le 2026-07-21.
- Livrables : clés/digests versionnés, graphe d'invalidation, cache LRU
  fail-closed, jetons stale à usage unique et API cœur sans changement UI.
- Critères obtenus : fixtures 1 à 6 et 9, parité de dérivation, corpus borné à
  cinquante conteneurs et suite complète.
- Preuve : `docs/P64_L01_INCREMENTAL_STATE_EVIDENCE.md`.
- Limite : aucune orchestration locale, suppression d'auto-solve, UI ou scène ;
  `fusion-validated: false`, `print-validated: false`.

### P64-L02 — Frontières, scores et résumé progressif

- Statut : `ready` après P64-L01.
- Dépendance : L01.
- Livrables : annotations contextuelles, représentants UI, sous-scores, détail
  replié et bornes globales rapides.
- Critères : fixtures 7 et 8 ; aucun score magique ; aucun solve automatique.

### P64-L03 — Solvage explicite et finalisation staged

- Dépendance : L02. Réutiliser le contrat d'annulation H07/H03C ; P64-U01
  reste un lot UX séparé et n'est pas ouvert implicitement.
- Livrables : suppression du timer global automatique, action primaire
  contextuelle, progressive widening, état `finalized` et matérialisabilité.
- Critères : fixtures 10 à 16, bridge, DOM, focus, suite complète.

### P64-L03V — Gate Fusion

- Observer éditions rapides, analyses locales ciblées, absence de solve global,
  bouton explicite, résultat obsolète, finalisation et scène inchangée.
- Cette gate ne valide aucune valeur physique ni impression.

### P64-F01/F02/F03

- F01 élargit les politiques de fermeture continue ;
- F02 livre équilibré, proportionnel et alignement modulaire adaptatif ;
- F03 livre réserve utile et cales explicites sous préconditions physiques.

## 20. Séquence et verrouillage

Séquence recommandée :

```text
P64-V2H03V retour humain
  -> clôture H03
  -> P44-V requalification
  -> P45-M001 contrat de disposition
  -> P64-L01
  -> P64-L02
  -> P64-L03 / L03V
  -> P45/P46 selon contrats
  -> P64-F01
  -> P64-F02
  -> P64-C01/C02
  -> P64-F03
  -> P64-C03/CV
```

Ce document n'ouvre aucune de ces missions runtime. `NEXT_ACTIONS.md` reste
autoritaire ; P64-V2H03V est clôturée et P44-V doit être requalifiée avant
toute ouverture runtime L01.

## 21. Vérifications minimales futures

- tests unitaires ciblés par couche ;
- parité des dérivations et variantes H03 ;
- monotonie Rapide/Normal/Approfondi ;
- stale, annulation et timeout ;
- tests DOM sans perte de focus ;
- roundtrip projet sans cache persisté ;
- bridge Python/Fusion ;
- suite complète `unittest` ;
- `compileall` ;
- absence d'import `adsk` dans le cœur ;
- `git diff --check` ;
- gate Fusion distincte ;
- impression réelle avant toute calibration ou revendication physique.

## 22. Hors scope absolu

- local_composer, frontend ou Vite comme surface produit ;
- calcul métier JavaScript ou `adsk` ;
- auto-solve global caché dans une dérivation locale ;
- cache persistant faisant autorité ;
- limite moteur définitive au top 3 ;
- score non décomposé ;
- modification automatique des assets ou cavités ;
- matérialisation d'un plan seulement placé ;
- corps automatique, valeur physique ou forme P45 implicite ;
- preuve d'impossibilité issue d'un budget heuristique ;
- revendication Fusion ou impression sans preuve correspondante.
