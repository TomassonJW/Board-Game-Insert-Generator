# P64-L09U-R8 — hand-off : éléments plats strictement soustractifs

Date : 2026-07-28.

Statut historique : R8 terminé, candidate 0.1.79
`human-positive-partial`. La géométrie est conforme ; la performance est KO.

Ne pas relancer ce handoff. La suite canonique est :
`docs/P64_L09U_R9_PERFORMANCE_RECOVERY_HANDOFF.md`.

Statut d'entrée historique : `ready`, GO direct acquis.

## Verdict de départ

La candidate Fusion 0.1.78 est `human-KO`, `do-not-run`.
`fusion-validated=false`, `print-validated=false`.

Le verdict complet et les captures sont dans
`docs/P64_L09U_R7_V_0178_HUMAN_KO_EVIDENCE.md`.

Le prochain agent ne doit pas redécouvrir cette gate ni demander un nouveau GO.
Il doit d'abord diagnostiquer et formaliser, puis mener les missions atomiques
jusqu'à une nouvelle candidate automatisée, intégrée et installée. La nouvelle
gate finale restera humaine.

## Problème réel à résoudre

Le système mélange encore trois responsabilités :

- trouver un assemblage minimal ;
- remplir la boîte avec des conteneurs imprimables ;
- représenter les plateaux et livrets.

Cette confusion autorise de la matière positive — plaques, rails, ponts ou
appuis — à apparaître lors du traitement des éléments plats. Elle alourdit aussi
le calcul minimal avec une géométrie qui ne devrait exister qu'après la
finalisation.

Le changement doit porter sur le contrat amont, pas seulement sur le rendu
Fusion.

## Contrat produit proposé par Thomas

### Étape 1 — enveloppes minimales

Chaque objet possède une enveloppe minimale déjà calculée :

- conteneur imprimable ;
- plateau ;
- livret.

Les dimensions physiques, jeux et parois restent inchangés. Toutes les
coordonnées et dimensions produit restent sur la grille `0,1 mm`.

### Étape 2 — calcul minimal

`Calculer` assemble uniquement les enveloppes minimales dans le volume utile de
la boîte.

Il peut choisir la position XY et l'ordre Z des éléments plats, mais il ne
fabrique aucune géométrie de support. Il publie :

- les poses minimales des conteneurs ;
- les empreintes orientées des éléments plats ;
- leurs intervalles Z et leur ordre automatique ;
- la relation `couvre` entre chaque empreinte et les conteneurs concernés ;
- une frontière suffisante pour que la finalisation ne rende pas la pose
  impossible.

### Étape 3 — finalisation des conteneurs

`Finaliser` étend les conteneurs pour remplir le volume disponible.

La hauteur finale d'un conteneur tient compte de l'épaisseur locale des éléments
plats qui seront encastrés au-dessus. Les cavités, fonds, parois et accès sont
recertifiés. À ce stade :

- les corps imprimables sont complets ;
- les plateaux et livrets ne sont toujours pas des corps imprimables ;
- aucune plaque de fermeture ou matière de support n'existe.

### Étape 4 — encastrements strictement soustractifs

Une passe distincte construit, par cellule XY atomique, la profondeur locale à
retirer :

`profondeur_encastrement = somme des épaisseurs des éléments plats couvrant la cellule`

Exemple :

- plateau seul : `4 mm` retirés ;
- livret seul : `2 mm` retirés ;
- recouvrement : `6 mm` retirés.

La passe applique uniquement des différences booléennes aux corps finalisés.
Elle ne fait aucune union et ne crée aucun corps imprimable.

### Identité mathématique attendue

Pour chaque conteneur finalisé `C` :

`C_avec_encastrements = C_sans_elements_plats - union(encastrements_locaux)`

Il doit être possible de tester automatiquement :

- volume positif ajouté par les éléments plats : exactement `0 mm³` ;
- nombre d'unions attribuées aux éléments plats : `0` ;
- nombre de nouveaux corps imprimables attribués aux éléments plats : `0` ;
- chaque opération liée à un élément plat est une coupe ou une référence
  non imprimable ;
- aucune coupe ne rebouche une cavité ou ne crée un surplomb.

## Arguments et contre-arguments à conserver

### « Il faut bien une matière pour supporter le plateau »

Non, pas une matière créée par le plateau. Le support est la matière déjà
présente dans les conteneurs finalisés. L'encastrement enlève localement la
matière nécessaire et laisse les surfaces existantes porter l'élément.

Si une position ne laisse aucun appui mécanique ou viole une paroi minimale,
elle doit être rejetée ou déplacée pendant le placement. Elle ne doit jamais
être réparée par une plaque ajoutée.

### « La réservation est un volume »

Oui, mais c'est un volume vide réservé, pas un volume imprimable positif. Dans
la CAD IR et le plan Fusion, sa nature doit rester `cut/reference`, jamais
`body/join/support`.

### « La finalisation doit connaître les plateaux »

Oui, pour réserver leur hauteur et certifier les parois, les fonds et les accès.
Cela n'autorise pas la finalisation à matérialiser un plateau, une fermeture ou
un support. Connaître une contrainte n'est pas créer de la matière.

### « Une pile exige des paliers »

Oui. Les paliers sont des profondeurs de coupe locales, définies par les
empreintes exactes et les intervalles Z. Ils ne sont pas des plaques ajoutées.

### « Le rendu Fusion pourrait simplement masquer la plaque »

Non. Une plaque cachée resterait un corps imprimable faux. Aperçu, CAD IR, plan
Fusion et BRep doivent porter le même contrat soustractif.

### « Le calcul approfondi prouve seulement que le cas est difficile »

Pas encore. Le journal montre que Normal et l'effort intermédiaire échouent
avant qu'Approfondi maximal trouve une solution déjà connue comme logeable.
Il faut profiler la première explosion de candidats et vérifier si le calcul
minimal explore par erreur la géométrie de finalisation ou des placements plats
redondants. Aucun gain ne sera promis sans mesure causale.

## Invariants d'acceptation

1. aucun élément plat ne produit de matière positive ;
2. aucune plaque, rail, pont, fermeture ou support supplémentaire ;
3. les conteneurs finalisés remplissent la boîte avant les coupes d'encastrement ;
4. profondeur locale égale à la somme exacte des épaisseurs couvrantes ;
5. cavités accessibles et jamais rebouchées ;
6. fond minimal et parois minimales conservés après toutes les coupes ;
7. petit élément sous le grand dans l'ordre automatique ;
8. grille produit `0,1 mm` partout, epsilon numérique séparé ;
9. aperçu, certificat, CAD IR, plan Fusion et BRep racontent la même géométrie ;
10. aucun succès publié si l'un de ces étages diverge.

## Pseudo-pilotage R8

### R8-A — preuve et première divergence

- classer 0.1.78 `human-KO`, `do-not-run` ;
- préserver les captures et le journal humain ;
- rejouer `CasLimite02+` et `CasLimite02++` en lecture seule ;
- tracer séparément enveloppes minimales, poses, finalisation, cellules XY,
  profondeurs de coupe, cavités, CAD IR, plan Fusion et BRep ;
- localiser la première apparition d'un volume positif lié à un élément plat ;
- profiler le calcul : phases, candidats, rejets, solveurs, temps et mémoire ;
- ne coder aucun correctif avant cette localisation.

### R8-B — décision d'architecture

- écrire une ADR sur le pipeline en quatre étapes et l'invariant soustractif ;
- comparer une correction locale, une séparation de modèle et une reconstruction
  bornée de la passe d'encastrement selon simplicité, robustesse, maintenance,
  testabilité et coût de recherche ;
- définir les contrats de migration sans écrire les projets sources ;
- décider où vit l'ordre automatique et où les épaisseurs cumulées sont figées.

### R8-C — séparation du calcul minimal

- retirer du calcul minimal toute fabrication de support ou fermeture liée aux
  éléments plats ;
- conserver seulement leurs enveloppes, contraintes, poses et relations de
  couverture ;
- ajouter des compteurs et une gate de performance causale ;
- tests ciblés et replay après chaque incrément.

### R8-D — finalisation des conteneurs

- finaliser les conteneurs indépendamment de toute matière de plateau ;
- réserver la hauteur locale nécessaire ;
- recertifier fonds, parois, cavités et accès ;
- refuser toute finalisation qui exige de la matière positive liée à un élément
  plat.

### R8-E — passe d'encastrement soustractive

- construire les cellules XY atomiques ;
- calculer les profondeurs locales exactes ;
- émettre uniquement des coupes ;
- propager les mêmes identités et intervalles jusqu'au plan Fusion ;
- rendre impossible par type ou certificat toute union issue d'un élément plat.

### R8-F — régressions et fidélité de bout en bout

Ajouter au minimum :

- un plateau unique au-dessus d'un conteneur avec cavité ;
- deux empreintes disjointes ;
- deux empreintes partiellement superposées `4/2/6 mm` ;
- une cavité sous, hors et à cheval sur une empreinte ;
- rejet d'un appui ou d'une paroi finale insuffisante ;
- absence de plaque, rail, pont, fermeture et surplomb ;
- volume additif `0 mm³`, union liée aux plats `0` ;
- conservation des profondeurs R6 et de la grille `0,1 mm` ;
- propagation identique aperçu → CAD IR → plan Fusion ;
- temps et nombres de candidats publiés sans benchmark interdit.

### R8-G — candidate et gate humaine

- tests ciblés puis suite autorisée complète ;
- diff relu, projets personnels SHA inchangés ;
- intégration directe dans `main` ;
- installation automatique d'une nouvelle candidate Fusion ;
- fournir à Thomas uniquement la nouvelle recette humaine.

## Données personnelles en lecture seule

`C:\Users\janko\Documents\BGIG\projects\CasLimite02+.bgig.json`

SHA-256 :
`5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC`

`C:\Users\janko\Documents\BGIG\projects\CasLimite02++.bgig.json`

SHA-256 :
`83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743`

Ne jamais modifier, sauvegarder, normaliser en place ou versionner ces fichiers.
Toute variante temporaire vit dans `<worktree>/.codex-work`, puis est supprimée.

## Interdits

- aucun correctif de rendu seul ;
- aucune nouvelle valeur physique ;
- aucune UI manuelle prématurée ;
- aucun benchmark, holdout, corpus ou tournoi solveur ;
- aucun changement ADR-0095 à ADR-0097 ;
- aucun déplacement silencieux pendant la finalisation ;
- aucun corps positif créé pour un plateau ou un livret ;
- aucune modification d'un worktree étranger.

## Lectures de reprise

1. `AGENTS.md` ;
2. `docs/PILOTAGE_CURRENT.md` ;
3. `docs/NEXT_ACTIONS.md` ;
4. `docs/HUMAN_GATES.md` ;
5. `docs/P64_L09U_R7_V_0178_HUMAN_KO_EVIDENCE.md` ;
6. ce hand-off ;
7. ADR-0099 à ADR-0104 ;
8. sources et tests du calcul minimal, de la finalisation composite, des
   réservations supérieures, de la CAD IR, du plan Fusion et des BRep.

## État Git de référence

Ce hand-off doit être repris depuis le commit qui le contient sur
`origin/main`. Le nouvel agent vérifie son chemin réel, sa branche, son HEAD,
`origin/main`, la propreté et les worktrees étrangers avant toute mutation.
