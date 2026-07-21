# ADR-0074 — Agencement minimal multi-graines et matérialisation avant finition

## Statut

Acceptée le 2026-07-21 après revue humaine du cycle P64-L03 dans Fusion 360.
Cette ADR supersède uniquement les clauses d'ADR-0071 qui imposaient une
fermeture géométrique pendant le solve global et réservaient la matérialisation
au seul plan finalisé. Les états incrémentaux, le solve explicite, le stale
fail-closed et la séparation de la finition restent acquis.

## Date

2026-07-21

## Cartes liées

- `P64-L03V — Gate Fusion du cycle explicite`, clôturée en KO contextuel ;
- `P64-L03R-A — Contrat correctif minimal/final` ;
- `P64-L03R-B — Solveur minimal multi-graines` ;
- `P64-L03R-C — Matérialisation minimale et remplacement de scène` ;
- `P64-L03R-V — Gate Fusion corrective` ;
- `P64-F01A02` et `P64-F02A02` pour les transformations de finition.

## Contexte

P64-L03 a correctement supprimé le solve global automatique et séparé les
actions `Calculer`, `Finaliser` et `Matérialiser`. La revue Fusion 0.1.56 a
toutefois montré que cette séparation restait principalement orchestrale :

- le solveur `stage_stack` appelle d'abord les dispositions XY avec `fill=True` ;
- les surplus X/Y et Z sont distribués aux enveloppes extensibles pendant le
  calcul global ;
- le finaliseur de compatibilité recertifie ensuite cette géométrie sans la
  transformer ;
- la palette interdit de matérialiser le placement minimal ;
- après une première matérialisation, l'UI peut considérer une nouvelle
  proposition comme déjà synchronisée parce qu'elle ne compare pas le digest
  de scène au digest exact de l'artefact courant.

Le résultat saute donc la décision utilisateur recherchée entre placement et
finition. Il empêche également d'imprimer volontairement des conteneurs à leur
volume minimal.

## Options

### Option A — Conserver la géométrie actuelle et seulement renommer les actions

- Avantage : changement faible.
- Inconvénient : la finalisation reste factice et la boîte paraît déjà remplie.
- Risque : l'UX continue à promettre une séparation que les artefacts ne portent
  pas réellement.

### Option B — Remplacer le portefeuille par un unique greedy « gros d'abord »

- Avantage : comportement facile à expliquer.
- Inconvénient : un ordre unique, un coin obligatoire ou des couches uniformes
  ferment prématurément des solutions valides.
- Risque : régressions sur les cas où l'empreinte, la rigidité ou une réservation
  est plus contraignante que la hauteur.

### Option C — Plan minimal certifié, portfolio de graines et finition optionnelle

- Avantage : séparation géométrique réelle, recherche diversifiée et possibilité
  de matérialiser avant finition.
- Inconvénient : nouvel artefact public dérivé, objectifs de score supplémentaires
  et gate Fusion corrective.
- Risque : explosion combinatoire sans budgets, symétries et dominance bornés.

## Décision

Retenir l'option C.

### Pipeline normatif

```text
édition
  -> analyses locales et variantes minimales
  -> Calculer l'agencement minimal global
  -> minimal_layout certifié + résiduel classifié
       -> Matérialiser / exporter le plan minimal
       -> choisir une politique de finition
  -> Finaliser le volume
  -> finalized_plan certifié
  -> Matérialiser / mettre à jour la scène Fusion
```

`minimal_layout` et `finalized_plan` sont deux artefacts distincts. Le premier
est imprimable au sens logiciel lorsqu'il possède son certificat de placement
et une CAD IR valide ; cela ne constitue jamais une validation d'impression.

### Invariant du plan minimal

Le solve minimal choisit une variante locale certifiée par conteneur et place
exactement son enveloppe minimale. Il ne peut :

- distribuer le résiduel de boîte sur X, Y ou Z ;
- modifier une cavité, un jeu, une paroi, un fond ou une pose locale ;
- ajouter une cale, une réserve utile ou un corps automatique ;
- transformer une cible souple en fermeture implicite ;
- déclarer « optimal » un résultat seulement borné par un budget.

L'interface parle de « meilleure proposition certifiée trouvée dans le budget ».

### Recherche multi-graines

La nouvelle lane minimale utilise un portefeuille déterministe de :

- modules graines parmi les participants les plus difficiles à placer ;
- ancres canoniques : coin, bord aligné, centre et surface basse disponible ;
- propagations : vers l'intérieur, le long d'un axe, radiale compacte et
  `lowest-supported-surface-first` ;
- ordres : rareté de placement, pression d'axe, empreinte, hauteur, volume et
  interleaving des extrêmes.

Une « pression d'axe » est une dimension rapportée à la dimension utilisable de
la boîte. Une longueur absolue n'est pas à elle seule une mesure de contrainte.
Z conserve sa sémantique verticale ; aucune permutation X/Y avec Z n'est créée.

Les coins sont ceux de l'enveloppe compacte en construction, pas nécessairement
les coins physiques de la boîte. Le plan complet est recentré dans le domaine
XY admissible après recherche, sauf si une réservation asymétrique ou une autre
contrainte dure impose une translation différente.

### Couches locales et supports

Le solveur favorise le niveau Z faisable le plus bas, mais ne construit pas des
plaques horizontales uniformes. Un corps haut peut traverser plusieurs intervalles
Z à côté de piles plus fines. Chaque empilement doit repasser par le certificat
commun de support et de collision.

### Recherche bornée et vérité du résultat

Rapide reste un préfixe de Normal, lui-même préfixe d'Approfondi. L'élargissement
porte progressivement sur les graines, ancres, orientations et propagations.
Les symétries sont canoniquement dédupliquées tant que la boîte et les
réservations ne les cassent pas. Le beam conserve des familles diverses et peut
réarranger les placements déjà essayés.

Le portfolio historique reste disponible comme comparaison et fallback après
adaptation à l'invariant minimal. Aucun échec heuristique ne devient une preuve
d'impossibilité.

### Matérialisation et scène Fusion

Une scène BGIG représente exactement un artefact courant : minimal ou finalisé.
Son identité transporte le type, le digest d'artefact, le digest du plan et le
digest CAD IR. Une nouvelle proposition n'est « à jour » que si ces identités
correspondent exactement.

`Mettre à jour la scène` prépare et valide d'abord le nouvel artefact, puis
remplace uniquement la scène possédée par BGIG. Les objets utilisateur non BGIG
restent intouchables. Une scène ancienne demeure visible mais désynchronisée
jusqu'à l'action explicite ; aucune édition ne déclenche sa régénération.

### Frontière de finalisation

La finalisation est optionnelle. Elle seule peut absorber ou qualifier le
résiduel par expansion simple, équilibrée, proportionnelle, hybride, cale ou
réserve utile selon les lots autorisés. Elle conserve le plan minimal si la
transformation échoue et produit un nouveau certificat avant matérialisation.

ADR-0069 reste normative pour les méthodes de finition. P45 reste propriétaire
des formes et dispositions locales ; P64 reste propriétaire du placement monde,
des budgets et du certificat global.

## Conséquences

### Positives

- le bouton `Calculer` produit enfin un artefact géométriquement minimal ;
- le résiduel devient une décision visible plutôt qu'une expansion implicite ;
- un insert minimal peut être matérialisé et exporté sans inventer une finition ;
- plusieurs intuitions de puzzle humain deviennent des graines comparables,
  jamais une règle unique fragile ;
- la synchronisation Fusion devient traçable par digest exact.

### Négatives

- les solveurs historiques doivent être audités pour retirer toute fermeture
  implicite ;
- le lifecycle et l'UX doivent distinguer scène minimale, scène finalisée et
  scène désynchronisée ;
- une nouvelle gate Fusion est nécessaire avant de rouvrir F01.

### Risques et mitigations

- combinatoire : progressive widening, beam borné, déduplication et dominance ;
- biais d'ancre : plusieurs graines et ancres, comparaison par certificat ;
- couches irréalistes : surfaces de support locales, pas de slab globale ;
- faux « optimal » : vocabulaire borné et télémétrie des budgets ;
- perte de scène : préparation préalable et suppression limitée aux objets BGIG ;
- confusion impression : `print-validated: false` tant qu'aucune pièce réelle
  n'est imprimée et mesurée.

## Alternatives refusées

- agrandir pendant `Calculer` puis certifier sans transformation pendant
  `Finaliser` ;
- imposer un coin physique ou un centre comme unique départ ;
- trier seulement par longueur absolue, volume ou hauteur ;
- remplir une couche uniforme avant toute couche suivante ;
- remplacer le portfolio par un greedy sans retour arrière ;
- considérer une scène courante sur la seule présence d'un ancien digest ;
- modifier automatiquement la scène après une édition.

## Suivi

- Contrat exécutable :
  `docs/P64_L03R_MINIMAL_LAYOUT_AND_MATERIALIZATION_CONTRACT.md`.
- ADR-0071 reste historique et normative pour l'incrémentalité, le solve
  explicite et la séparation des coûts ; ses clauses de matérialisation
  exclusivement post-finition sont supersédées.
- P64-L03V est un KO contextuel 0.1.56, pas une validation Fusion.
- P64-L03R-B est la prochaine mission runtime, après intégration de L03R-A.
- `fusion-validated: false`, `print-validated: false` pour cette correction.
