# P64-C — Carte de capacité et insertion bornée après solvage

Statut : contrat d'architecture accepté le 2026-07-21 ; aucune implémentation.

ADR :
[ADR-0072](DECISIONS/ADR-0072-post-solve-capacity-maps-and-bounded-reuse.md).

Capabilities : `C-ASSET`, `C-CAVITY`, `C-GEOMETRY`, `C-SOLVER`, `C-LAYOUT`,
`C-USABILITY`, `C-QUALITY`.

## 1. Objectif et promesse honnête

Après un plan global finalisé, détecter des volumes assez structurés pour
accueillir un ajout futur sans déplacer les corps existants. Le système peut
alors tenter une insertion locale et recertifier le plan en réutilisant ses
placements.

La promesse n'est jamais « aucun recalcul ». La promesse est :

> éviter une nouvelle recherche globale lorsque l'enveloppe monde reste
> strictement inchangée, tout en rejouant tous les certificats nécessaires.

Si les invariants ne passent pas, l'ancien plan devient obsolète et le solveur
global reste le seul chemin autoritaire.

## 2. Vocabulaire normatif

### `CapacityOpportunityMap`

Artefact dérivé, immuable et éphémère lié à un projet, un placement et une
finalisation précis. Il contient des opportunités, jamais des objets projet.

### `InternalOpportunityZone`

Région locale potentiellement convertible en cavité ou en réorganisation interne
dans un conteneur dont l'enveloppe extérieure finale reste inchangée.

### `BoxReserveBay`

Région monde intentionnellement préservée pour un futur conteneur autonome.
Elle est distincte des jeux techniques et des résiduels accidentels.

### `CapacityTemplateMatch`

Comparaison explicable entre une zone et les dimensions résolues d'un asset,
d'une cavité ou d'un conteneur existant. Elle n'invente ni quantité ni mesure.

### `IncrementalInsertionAttempt`

Tentative bornée qui garde tous les placements monde existants fixes, ajoute une
demande explicite, reconstruit les géométries touchées et rejoue les certificats.

## 3. Propriété P45/P64

P45 possède :

- la création ou modification de cavités ;
- les cloisons, accès et futures formes ;
- les poses et orientations d'assets ;
- le certificat local du conteneur modifié.

P64 possède :

- la carte de capacité du plan final ;
- les baies de boîte et leurs placements monde ;
- la tentative d'insertion d'un nouveau corps ;
- le certificat global, les budgets et la vérité du résultat.

La carte commune transporte seulement des zones certifiables, leurs contraintes
et leur provenance. P64 ne découpe pas une cavité ; P45 ne déplace pas un corps
monde.

## 4. Entrées minimales

- projet source normalisé et digest ;
- plan global complet et certificat de placement ;
- plan finalisé et politique de finition ;
- enveloppes minimales et finales ;
- cavités, features, jeux, parois, cloisons et fonds ;
- réservations supérieures et coupes localisées ;
- appuis, retrait et axes verrouillés ;
- seuils/caps de détection explicites ;
- version du détecteur.

Une proposition seulement partielle, obsolète ou non finalisée ne produit pas de
carte consommable.

## 5. Sortie minimale

```text
CapacityOpportunityMap
  schema_version
  source_digest
  global_layout_digest
  finalized_plan_digest
  detector_id + detector_version
  budget + telemetry
  internal_zones[]
  box_reserve_bays[]
  rejections[]
  map_digest
```

Chaque zone porte :

- identifiant stable dans la carte ;
- propriétaire conteneur ou boîte ;
- origine et dimensions maximales ;
- repère local ou monde ;
- orientations autorisées ;
- entrée/retrait autorisés ;
- paroi, cloison et fond disponibles ;
- réservations et supports adjacents ;
- classe de capacité ;
- correspondances avec dimensions sources connues ;
- codes de limite ou d'incertitude.

## 6. Détection des zones internes

Pour chaque conteneur, le détecteur part du volume de l'enveloppe finale puis
retranche :

1. cavités et jeux internes ;
2. murs, cloisons et fond minimaux ;
3. features et volumes de manipulation ;
4. coupes de réservations supérieures ;
5. matière contractuellement nécessaire aux appuis ;
6. intervalles interdits par pose ou accès ;
7. marges numériques du validateur.

Les faces restantes engendrent des cellules orthogonales adaptatives. Les AABB
maximales sont dédupliquées par inclusion. Une zone non rectangulaire peut être
représentée par plusieurs composantes ; elle n'est pas arrondie vers une grande
boîte traversant de la matière obligatoire.

Le détecteur reste conservateur. Un faux négatif est acceptable dans un budget ;
un faux positif consommé sans recertification ne l'est pas.

## 7. Détection des baies de boîte

Une baie existe seulement si la politique de finalisation l'a explicitement
préservée. Elle doit :

- être séparée des corps et jeux techniques ;
- rester dans la boîte utile ;
- déclarer son support bas ou ses appuis ;
- respecter plateaux, couvercle et ordre de retrait ;
- posséder une entrée ou direction de manipulation ;
- rester un volume nommé dans le certificat final.

Un EMS résiduel du solveur, une cavité interne ou un vide entre conteneurs ne
devient pas automatiquement une baie.

## 8. Seuils et classement des tailles

Les seuils évitent les micro-volumes et les suggestions absurdes. Ils sont
contractés par :

- dimension minimale sur chaque axe ;
- volume minimal ;
- rapport d'aspect maximal ;
- classe d'accès ;
- épaisseur de paroi/fond disponible ;
- nombre maximal de zones par propriétaire ;
- nombre maximal de correspondances de templates.

Les valeurs numériques ne sont pas fixées dans ce document. P64-C01 doit les
mesurer sur fixtures puis les rendre observables.

Les correspondances utilisent seulement :

- assets existants ;
- presets locaux connus ;
- cavités certifiées ;
- enveloppes minimales de conteneurs existants.

Le classement peut préférer une échelle et un aspect voisins. Il ne propose pas
de multiplier arbitrairement une dimension ni de créer un asset fantôme.

## 9. Mémoire courte et invalidation

La carte peut vivre en mémoire de session ou dans un cache reconstructible. Elle
est consommable uniquement si ses trois digests source/global/final sont encore
courants.

Invalidations :

- toute édition source ;
- nouveau solvage ou autre candidat retenu ;
- nouvelle politique ou autre résultat de finalisation ;
- changement de version du détecteur ;
- modification de valeurs physiques ou contrat géométrique ;
- scène Fusion différente sans plan moteur correspondant.

La carte n'est pas intégrée à `bgig.project.v1`. Une future persistance de
diagnostic exigerait un format cache distinct et jetable.

## 10. Chemin C02 — Ajouter un asset localement

L'action utilisateur choisit :

- un asset ou preset réel ;
- sa quantité et ses dimensions résolues ;
- sa pose autorisée ;
- le conteneur et la zone ;
- le jeu de cavité ;
- la politique de cloison permise par P45.

La tentative :

1. clone la source sans la committer dans l'état courant ;
2. produit les variantes locales compatibles avec la zone ;
3. refuse toute modification d'enveloppe finale ou de placement monde ;
4. reconstruit le certificat local ;
5. recompose le plan avec placements existants identiques ;
6. rejoue le certificat global et la finalisation ;
7. accepte atomiquement la nouvelle source seulement si tous les certificats
   passent ;
8. marque CAD IR et scène obsolètes jusqu'à matérialisation explicite.

Une réussite porte `placement_reused: true`, jamais `no_recalculation: true`.

Un échec laisse le projet inchangé et propose :

- choisir une autre zone ;
- modifier explicitement les contraintes ;
- ajouter l'asset au projet puis `Calculer l'agencement`.

## 11. Chemin séparateur

Ajouter un séparateur peut subdiviser une cavité ou organiser une nouvelle
cavité dans une zone. Cette action dépend d'un contrat P45 définissant :

- fonction du séparateur ;
- épaisseur minimale et héritage ;
- liaison ou caractère amovible ;
- impact sur accès et nettoyage ;
- représentation CAD IR ;
- validation physique attendue.

P64-C01 peut indiquer qu'une zone est géométriquement compatible avec une
subdivision. Il ne crée pas le séparateur.

## 12. Chemin C03 — Ajouter un conteneur autonome

Préconditions :

- baie courante et certifiée ;
- nouveau groupe explicitement créé ;
- au moins une variante locale certifiée ;
- enveloppe et orientation tenant dans la baie ;
- jeux globaux préservés ;
- support et retrait valides ;
- aucun placement existant déplacé.

Le moteur peut exécuter une petite recherche limitée à la baie. Ce n'est pas le
solveur global complet, mais cela reste une recherche bornée et certifiée.

Si aucune variante ne passe, la baie n'est pas agrandie et aucun voisin ne
rétrécit silencieusement. Le projet global devient à recalculer seulement si la
personne confirme l'ajout hors baie.

## 13. Finalisation et régénération de la carte

Après une insertion réussie :

- la finalisation est rejouée sur la topologie inchangée ;
- les zones consommées disparaissent ;
- les zones restantes sont redétectées ;
- le nouveau map digest remplace l'ancien ;
- aucun volume ne peut être consommé deux fois.

Si la nouvelle cavité transforme du surplus solide, les métriques de matière et
résistance restent inconnues tant qu'elles ne sont pas implémentées et validées.

## 14. UX progressive

### Dans un conteneur

Résumé fermé par défaut :

```text
Capacité disponible : 2 zones
Plus grande zone : 42 × 28 × 18 mm
```

Actions possibles selon contrat :

- `Ajouter un élément ici` ;
- `Tester un preset` ;
- `Ajouter une séparation` ;
- `Voir les limites`.

### Dans le résultat global

Une baie certifiée affiche :

```text
Réserve pour futur conteneur : 55 × 40 × 20 mm
```

Action : `Ajouter un conteneur dans cette réserve`.

### États

- `Capacité calculée` ;
- `Carte obsolète` ;
- `Insertion locale en cours` ;
- `Placement conservé et recertifié` ;
- `Recalcul global requis` ;
- `Zone incompatible` avec raisons.

Le diagnostic expert expose AABB, digests, caps et rejets. Le parcours normal ne
montre ni EMS, ni voxels, ni données de certificat brutes.

## 15. Budgets et télémétrie

Budgets minimaux :

- `max_internal_zones_per_container` ;
- `max_box_reserve_bays` ;
- `max_candidate_cells` ;
- `max_template_matches_per_zone` ;
- `max_local_insertion_variants` ;
- `max_bay_placement_trials` ;
- `max_recertification_attempts`.

Télémétrie :

- faces/cellules/zones générées, fusionnées, dominées et retenues ;
- zones rejetées par taille, paroi, fond, accès, support ou réservation ;
- correspondances évaluées ;
- tentative locale, certificats et fallback ;
- placements monde comparés avant/après ;
- temps observé et limites atteintes ;
- stale/annulation.

Atteindre un cap signifie carte ou insertion incomplète dans le budget, jamais
absence prouvée de capacité.

## 16. Certificats

### Certificat de carte

Vérifie que chaque zone :

- appartient au plan final courant ;
- reste dans son propriétaire ;
- ne recouvre aucun volume interdit connu ;
- porte les dépendances et limites exactes ;
- ne se présente pas comme objet imprimable.

### Certificat d'insertion locale

Vérifie :

- nouvelle source complète ;
- couverture des assets ;
- certificat local P45 ;
- enveloppe et placement monde inchangés ;
- certificat global commun ;
- finalisation valide ;
- zéro corps automatique ;
- scène non modifiée.

### Certificat d'insertion en baie

Ajoute :

- exactement un nouveau corps explicitement demandé ;
- placement contenu dans la baie ;
- jeux, support, retrait et réservations ;
- autres placements bit-à-bit inchangés.

## 17. Fixtures déterministes

1. grande zone interne simple, asset ajouté sans changer l'enveloppe ;
2. zone visuellement grande mais rejetée par fond minimal ;
3. deux composantes séparées non fusionnées en faux grand AABB ;
4. feature ou accès protégeant une région ;
5. coupe de plateau rendant la compatibilité conditionnelle ;
6. ajout dépassant la zone et fallback global explicite ;
7. certificat local échoué, source inchangée ;
8. placements monde identiques après insertion réussie ;
9. ancienne carte rejetée après modification source ;
10. baie certifiée recevant un nouveau conteneur ;
11. EMS accidentel non promu en baie ;
12. support ou retrait refusant le conteneur en baie ;
13. insertion consommant une zone et carte régénérée sans double usage ;
14. projet dense : détection bornée sans promesse de capacité ;
15. annulation/stale et scène inchangée.

## 18. Découpage de livraison

### P64-C01 — Carte read-only

- Dépendances : plan finalisé contracté, P64-F02, frontières P45 stables.
- Livrables : types, détecteur, digests, caps, zones internes, baies déjà
  déclarées, diagnostics et fixtures 1 à 5, 9, 11, 14.
- Interdit : aucune mutation projet ou géométrique.

### P64-C02 — Insertion locale et recertification

- Dépendances : C01 et producteur/certificat P45 autorisant la nouvelle cavité.
- Livrables : transaction atomique, réutilisation des placements, certificats,
  fallback et fixtures 6 à 8, 13, 15.
- Interdit : nouveau corps autonome ou déplacement d'un voisin.

### P64-C03 — Baie et conteneur autonome

- Dépendances : C01, politique de réserve P64-F03 et retours physiques requis.
- Livrables : insertion limitée à une baie, nouveau corps explicite, support,
  retrait et fixtures 10 à 12.
- Interdit : transformer un résiduel accidentel en réserve.

### P64-CV — Gate Fusion

Observer :

- carte cachée par défaut ;
- insertion locale réussie avec placement conservé ;
- échec nécessitant le solveur global ;
- baie explicite ;
- aucun objet Fusion avant matérialisation ;
- régénération sans doublon après action explicite.

La gate Fusion ne valide ni résistance, ni ergonomie, ni impression.

## 19. Vérifications futures

- tests purs du détecteur et des certificats ;
- déterminisme des AABB et digests ;
- tests transactionnels source inchangée sur échec ;
- tests de parité placements monde ;
- budgets, annulation et stale ;
- tests bridge/DOM ;
- suite complète et `compileall` ;
- absence d'`adsk` dans le cœur ;
- `git diff --check` ;
- gate Fusion ;
- coupons et impression avant toute revendication physique.

## 20. Hors scope absolu

- création automatique d'assets, cavités, séparateurs, cales ou conteneurs ;
- persistance de la carte comme vérité projet ;
- formes libres, maillage, voxelisation dense ou IA générative géométrique ;
- réduction automatique d'une paroi ou d'un fond ;
- déplacement silencieux de placements existants ;
- assimilation d'une zone interne à un corps autonome ;
- promotion d'un vide technique ou EMS en baie ;
- promesse de zéro recalcul ou de solubilité ;
- changement de valeur physique, default ou tolérance ;
- preuve Fusion ou impression sans observation correspondante.


## 21. Distinction avec P64-L04A (2026-07-22)

P64-L04A est désormais implémenté, mais ne constitue pas une implémentation de
C01 ou C02. Il intervient sur un `minimal_layout` avant finalisation, utilise
les cavités et variantes locales déjà certifiées et exige l’enveloppe exacte
déjà placée. Il ne dérive aucune `CapacityOpportunityMap` et ne convertit aucun
surplus finalisé.

C01/C02 restent donc `planned-locked` avec leurs dépendances F01/F02. Toute
preuve, action ou statut L04A doit rester séparé des cartes de capacité
post-finalisation.
