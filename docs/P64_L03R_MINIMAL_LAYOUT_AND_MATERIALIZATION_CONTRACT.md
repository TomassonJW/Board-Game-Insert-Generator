# P64-L03R — Contrat d'agencement minimal et de matérialisation duale

## 1. Résultat produit attendu

Après chaque édition, BGIG maintient les dimensions et variantes locales des
conteneurs sans lancer de placement monde. Sur action explicite, le solveur
compose uniquement leurs enveloppes minimales dans la boîte. L'aperçu montre ce
groupe compact et le résiduel encore libre.

La personne peut alors :

- matérialiser ou exporter les volumes minimaux ;
- choisir une méthode de finalisation qui transforme le résiduel ;
- modifier le projet et recalculer sans toucher automatiquement à la scène.

Le calcul minimal ne prétend pas fermer la boîte. La finalisation ne prétend pas
être nécessaire à l'imprimabilité logicielle du plan minimal.

## 2. Vocabulaire normatif

### `local_minimum_variant`

Variante de conteneur certifiée par P45/P64-L02 avec enveloppe extérieure
minimale, cavités, jeux, parois et fonds résolus. Elle ne connaît aucune pose
monde.

### `minimal_layout`

Sélection d'une variante minimale par conteneur, placements monde, résiduel
classifié, certificat global et provenance de recherche. Aucun surplus de boîte
n'est attribué aux conteneurs.

### `finishing_policy`

Décision explicite qui transforme ou qualifie le résiduel du `minimal_layout`.
Elle possède son budget, ses raisons et son digest.

### `finalized_plan`

Résultat certifié d'une politique de finition. Il référence le digest exact du
`minimal_layout` source.

### `materialized_scene`

Scène Fusion possédée par BGIG et issue d'un `minimal_layout` ou d'un
`finalized_plan` précis. Son existence ne prouve aucune impression réelle.

## 3. Frontières absolues

- Le cœur Python reste sans import `adsk`.
- P45 possède les formes, poses et variantes locales ; P64 ne les redéfinit pas.
- X/Y peuvent utiliser les rotations déjà autorisées ; Z ne permute jamais avec
  X ou Y sans intention locale certifiée.
- Le solve minimal n'ajoute ni cale, ni réserve utile, ni complément, ni corps
  automatique.
- Les jeux, tolérances, parois, fonds, defaults et valeurs physiques restent
  inchangés.
- Une marge volumique positive ne prouve pas un placement.
- Un budget épuisé reste `no_solution_within_budget`.
- La scène ne change jamais automatiquement.
- `fusion-validated` et `print-validated` restent faux sans preuve distincte.

## 4. Invariant géométrique du `minimal_layout`

Pour tout placement de conteneur :

```text
final_outer_dimensions_mm == selected_variant.minimum_outer_dimensions_mm
surplus_distribution_mm == {x: 0, y: 0, z: 0}
automatic_body_count == 0
```

Une dimension locale explicitement `fixed` peut naturellement être supérieure
à un minimum alternatif, mais le solve global ne l'augmente pas. Une cible
souple n'est jamais utilisée pour fermer implicitement une rangée ou un étage.

Le résiduel est mesuré dans la boîte utilisable après jeux et réservations. Il
reste non imprimé et non attribué jusqu'à une décision de finition.

## 5. Mesure de rareté de placement

Le moteur ne confond pas longueur absolue et contrainte. Pour chaque orientation
locale autorisée, il calcule au minimum :

```text
pressure_x = size_x / usable_box_x
pressure_y = size_y / usable_box_y
pressure_z = size_z / usable_box_z
```

Le classement de difficulté conserve des composantes séparées :

- pression maximale et deuxième pression ;
- nombre d'orientations admissibles ;
- axes fixes ou cibles ;
- empreinte XY et côté long normalisés ;
- hauteur et volume minimal ;
- compatibilité sous plateau et déficit de headroom ;
- rareté des surfaces capables de supporter le corps.

Ces composantes ordonnent les branches. Elles ne sont ni un certificat, ni un
score produit opaque.

## 6. Portfolio de graines déterministes

Le solveur retient plusieurs participants graines parmi les plus contraints. Il
ne fixe pas définitivement le premier module à la seule valeur maximale.

Ordres minimaux à comparer :

1. rareté de placement décroissante ;
2. pression d'axe décroissante ;
3. côté long XY normalisé décroissant ;
4. empreinte XY décroissante ;
5. hauteur décroissante ;
6. volume minimal décroissant ;
7. interleaving des extrêmes épais/fins ou grands/petits.

Les égalités sont résolues par identités stables. L'ordre de saisie utilisateur
ne devient jamais un hasard algorithmique.

## 7. Ancres de départ

Pour chaque graine et orientation retenues, le portfolio peut ouvrir :

- `compact_corner` : coin canonique de l'enveloppe compacte en construction ;
- `aligned_edge` : bord aligné sur le grand axe XY de la graine ;
- `compact_center` : centre local pour une propagation radiale ;
- `lowest_surface` : surface de support faisable au Z minimal.

Les quatre coins physiques de la boîte ne sont pas essayés sans nécessité. Une
boîte et des réservations symétriques sont canoniquement dédupliquées. Une
réservation localisée, une incompatibilité sous plateau ou une contrainte de
retrait peut casser cette symétrie et rouvrir les ancres concernées.

## 8. Propagations

Une branche propage les placements selon une politique explicite :

- `inward_contact` : maximiser les contacts contre l'enveloppe existante ;
- `long_axis_spine` : construire une colonne vertébrale le long d'un axe ;
- `radial_compact` : étendre le groupe autour d'un centre local ;
- `lowest_supported_surface_first` : choisir d'abord le Z faisable le plus bas.

La propagation génère plusieurs positions de contact et orientations. Le beam
peut conserver des états qui déplacent ou réarrangent les premiers placements ;
une pose déjà essayée n'est pas verrouillée par l'heuristique.

## 9. Couches locales, skyline et support

« Remplir le fond puis remonter » est une préférence de recherche, pas une slab
globale. Le solveur maintient une carte de surfaces support disponibles ou une
représentation équivalente. Un corps haut peut traverser plusieurs intervalles Z
à côté d'une pile de corps fins.

Un placement au-dessus du fond doit satisfaire le validateur commun :

- absence de collision ;
- couverture de support minimale déjà contractuelle ;
- aucune portée ou pont implicite non autorisé ;
- jeux verticaux respectés ;
- retrait et réservations supérieures non invalidés.

Les corps épais sont de bons candidats graines, mais leur hauteur ne prime pas
automatiquement sur une empreinte longue, une orientation unique ou une
réservation plus contraignante.

## 10. Score incrémental explicable

Le classement des états expose séparément :

- `lowest_z` : altitude de pose et hauteur totale ;
- `cluster_growth_xy` : croissance de l'enveloppe compacte ;
- `internal_gap` : espaces entre modules dans cette enveloppe ;
- `residual_fragmentation` : nombre et qualité des régions libres ;
- `contact` : faces ou segments adjacents utiles ;
- `support` : couverture et stabilité mesurées ;
- `top_compatibility` : respect des plateaux et headrooms ;
- `removal` : contraintes de retrait réellement disponibles.

Aucun total opaque n'est affiché comme vérité utilisateur. Les poids servent à
ordonner une lane et restent observables dans la télémétrie.

## 11. Progressive widening et budgets

Les profils sont monotones :

- Rapide : petit nombre d'ordres, graines `compact_corner` et `aligned_edge` ;
- Normal : préfixe Rapide puis centre, skyline et graines supplémentaires ;
- Approfondi : préfixe Normal puis orientations, propagations et beam élargis.

Les caps portent au minimum sur : graines, ancres, orientations, propagations,
états générés, états validés, largeur de beam et essais de placement. Chaque
arrêt publie la limite atteinte.

## 12. Dominance, diversité et symétries

Deux états géométriquement équivalents sous une symétrie encore valide sont
dédupliqués par une signature canonique. Un état peut en dominer un autre si,
pour les mêmes participants placés, il n'est pire sur aucune contrainte dure et
est au moins aussi bon sur enveloppe, hauteur, support et fragmentation.

La dominance ne supprime pas toutes les familles d'ancre ou de propagation. Le
beam conserve une diversité bornée afin qu'une lane centrale, latérale ou par
skyline puisse survivre à un meilleur score local précoce.

## 13. Placement final dans la boîte

La recherche relative produit une enveloppe compacte. Elle est ensuite translatée
dans le domaine XY admissible : centrage par défaut, puis ajustement déterministe
si les réservations supérieures ou contraintes du monde rendent le centre
invalide.

Cette translation ne modifie ni tailles, ni relations internes, ni certificat
local. Le certificat global est produit sur les coordonnées monde finales.

## 14. Résultat et vérité

Le solve retourne uniquement les statuts canoniques : `solution_found`,
`no_solution_within_budget`, `proven_impossible`, `invalid_input` ou
`stale_or_cancelled` selon ADR-0068.

Une solution expose :

- variantes retenues et digests ;
- graine, ancre, propagation et ordre gagnants ;
- budgets et compteurs ;
- certificat global ;
- enveloppe du groupe et résiduel classifié ;
- raisons de classement ;
- formulation « meilleure proposition certifiée trouvée dans le budget ».

## 15. Matérialisation minimale

Un `minimal_layout` courant devient matérialisable si :

- toutes ses variantes locales sont certifiées ;
- son certificat global est courant ;
- sa CAD IR est produite et validée ;
- aucun digest de dépendance n'est stale.

L'action est nommée `Matérialiser les volumes minimaux` ou équivalent explicite.
Elle ne crée aucun remplissage et ne change pas le statut de finalisation.

L'export des imprimables minimaux est permis sous les mêmes préconditions. Il
reste `preprint` et `print-validated: false`.

## 16. Finalisation optionnelle

`Finaliser le volume` consomme un `minimal_layout` courant et une politique
explicite. La politique peut être :

- fermeture simple par expansion admissible ;
- répartition équilibrée ;
- répartition proportionnelle ;
- hybride, cales ou réserve utile seulement dans leurs lots autorisés.

La finalisation produit un nouvel artefact. Elle n'écrase pas le plan minimal.
En cas d'échec, le plan minimal reste courant, consultable et matérialisable.

## 17. Identité et remplacement de scène Fusion

La scène BGIG transporte au minimum :

- `artifact_kind` : `minimal_layout` ou `finalized_plan` ;
- `artifact_digest` ;
- `partition_plan_digest` ;
- `cad_ir_digest` ;
- `source_revision`.

Une scène est `current` seulement si toutes les identités correspondent à
l'artefact sélectionné. La simple présence d'un ancien digest ne suffit pas.

La mise à jour suit une transaction bornée :

1. construire et valider la nouvelle CAD IR ;
2. inspecter la propriété de la scène existante ;
3. refuser en présence de plusieurs racines ou d'objets ambigus ;
4. supprimer uniquement la racine et les objets tagués BGIG ;
5. générer la scène de remplacement ;
6. inspecter le nombre et les identités des corps produits.

Les objets utilisateur non BGIG ne sont jamais supprimés. Une édition rend la
scène `desynchronized` sans la modifier.

## 18. UX progressive

Après `Calculer`, l'aperçu affiche :

- le groupe minimal, sa boîte englobante et son centrage ;
- les espaces résiduels non imprimés ;
- la meilleure proposition trouvée et ses limites de budget ;
- deux branches visibles : matérialiser minimal ou choisir une finition.

Les graines, ancres, propagations, scores et compteurs restent dans un détail
expert replié. Une seule action primaire contextuelle peut être mise en avant,
mais l'autre branche ne doit pas disparaître.

Après une modification, l'ancien aperçu et la scène restent visibles avec un
statut obsolète. Les actions de matérialisation sont fail-closed jusqu'au nouveau
certificat.

## 19. Fixtures automatisées obligatoires

1. un seul conteneur extensible reste exactement à son minimum après solve ;
2. aucun surplus X/Y/Z n'apparaît dans un `minimal_layout` ;
3. deux modules longs s'emboîtent via au moins deux graines alternatives ;
4. une hauteur absolue forte ne domine pas une empreinte plus rare ;
5. coin, bord et centre sont dédupliqués sous symétrie ;
6. une réservation asymétrique rouvre les ancres pertinentes ;
7. un corps haut traverse plusieurs intervalles à côté de piles fines ;
8. aucun empilement sans support suffisant n'est certifié ;
9. Rapide est préfixe de Normal, Normal d'Approfondi ;
10. un échec borné reste `no_solution_within_budget` ;
11. matérialisation minimale acceptée avant finalisation ;
12. échec de finalisation conserve le plan minimal matérialisable ;
13. nouvelle révision rend l'ancienne scène désynchronisée ;
14. un digest ancien ne masque pas `Mettre à jour la scène` ;
15. régénération remplace une seule scène BGIG et préserve les objets utilisateur ;
16. aucune édition locale ne lance solve, finalisation ou scène ;
17. plateaux et réservations supérieures restent contraignants ;
18. cas dense 11 × 34 : statut honnête inchangé si aucun nouveau certificat.

## 20. Découpage de livraison

### P64-L03R-A — Contrat correctif

- ADR-0074, présent contrat, gate KO, pilotage et fixtures contractuelles.
- Aucun runtime, schéma, valeur physique ou scène.

### P64-L03R-B — Solveur minimal multi-graines

- retirer l'allocation implicite des surplus du chemin minimal ;
- produire `minimal_layout`, résiduel et télémétrie multi-graines ;
- préserver les lanes historiques comme comparateurs/fallbacks minimaux ;
- tests cœur, monotonie et non-régression du cas dense.
- Statut d'exécution au 2026-07-21 : `implemented-core`,
  `automated-validated` ; preuve
  `docs/P64_L03R_B_MINIMAL_SOLVER_EVIDENCE.md`.

### P64-L03R-C — Matérialisation duale et scène courante

- autoriser CAD IR et export depuis `minimal_layout` ;
- sélectionner artefact minimal ou finalisé ;
- comparer les digests exacts et exposer `Mettre à jour la scène` ;
- remplacer atomiquement la seule scène BGIG possédée ;
- tests bridge, DOM et registre Fusion simulé.
- Statut d'exécution au 2026-07-21 : `implemented-core`,
  `implemented-fusion-bridge`, `implemented-fusion-ui`,
  `automated-validated` ; preuve
  `docs/P64_L03R_C_DUAL_MATERIALIZATION_EVIDENCE.md`.

### P64-L03R-V — Gate Fusion corrective

- observer géométrie minimale non remplie ;
- matérialiser le plan minimal ;
- modifier, recalculer et remplacer la scène sans doublon ;
- vérifier scène stale, objets utilisateur préservés et aucun auto-solve ;
- aucune validation physique ou impression.

### P64-F01A02 et suivants

- implémenter ensuite les transformations réelles de finition ;
- ne pas réintroduire d'expansion dans le solve minimal.

## 21. Validation minimale par lot runtime

- tests purs de l'algorithme et du validateur commun ;
- monotonie des efforts et caps observables ;
- tests de symétrie, dominance et diversité ;
- tests DOM et bridge pour le lifecycle ;
- suite complète `unittest` ;
- `compileall` ;
- frontière `adsk` du cœur ;
- `git diff --check` ;
- gate Fusion séparée.

## 22. Hors scope absolu

- finition réelle dans L03R-A/B/C ;
- cales, réserves utiles, compléments ou formes P45 implicites ;
- permutation automatique avec Z ;
- modification des valeurs physiques, tolérances ou defaults ;
- remplacement de la scène sans preuve de propriété BGIG ;
- solve ou matérialisation automatique après édition ;
- top 3 moteur fixe ;
- revendication d'optimalité sans preuve exacte ;
- revendication `fusion-validated` ou `print-validated` sans preuve correspondante ;
- ouverture de P46, P47-P50, P67-P69 ou des lots de finition hors dépendances.
