# P67 - Rapport de priorisation post-MVP et revue UX structurelle

Date : 2026-07-14
Statut : `draft-human-review`, `p67-in-review`, `no-runtime-change`,
`p44-m001-blocked`, `print-validated: false`.

## 1. Contexte et preuves

La revue part du MVP Fusion-only accepte par Thomas avec le retour :

```text
P66 Fusion OK 0.1.20 - commit 6e351bb
```

Le commit complet observe pour P66 est
`6e351bbd652ebdf496e7e53060d0d18dda7c6b57`. Le pilotage P66 a ensuite ete
clos sur `main` par `e55fe5a223912e3cc096a1cda275cac1b794de25`.

La source humaine de ce rapport est une revue commentee de la palette 0.1.20,
ecran par ecran, fournie le 2026-07-14. Elle est completee par un audit en
lecture seule de la palette HTML, du bridge Python pur, du schema projet, des
reservations superieures, du solveur volumetrique et des tests existants.

Cette mission est `P67-M000 - Capture et cadrage de la revue UX`. Elle ne code
rien, ne modifie aucun runtime, ne qualifie aucune impression et ne vaut pas
acceptation de P67. Les choix marques `a arbitrer` restent humains.

## 2. Verdict executif

L intuition produit est juste : ajouter maintenant de nombreux champs de formes,
rayons, fonds, encoches et couvercles sur l architecture d interface actuelle
creerait une dette immediate. Les cartes sont trop hautes, des controles
essentiels sont caches, la navigation disperse des objets fortement lies et le
rendu reconstruit des portions de DOM pendant la saisie.

La recommandation est donc une **fondation UX structurelle bornee avant les
geometries P45**, sans transformer cette passe en refonte esthetique exhaustive.
Elle doit stabiliser :

1. le rendu, le focus, le scroll et l etat ouvert des sections ;
2. la densite et la hierarchie visuelle des champs ;
3. quatre espaces metier au lieu de six onglets disperses ;
4. la representation Conteneur parent -> Elements enfants ;
5. le cycle de document projet et la distinction utilisateur/diagnostic ;
6. les termes, aides et etats automatiques avant ajout de nouveaux parametres.

P69 reste necessaire apres P50 : elle evaluera un produit enrichi par les vraies
formes et les couvercles, plusieurs profils utilisateurs, l accessibilite et les
retours d impression. La passe anticipee proposee ici est une correction de
fondation, pas la revue finale.

Cette recommandation reoriente le debut de V0.2 par rapport a ADR-0061. Elle est
donc portee par l ADR-0062 proposee et ne devient executable qu apres arbitrage
humain P67-V.

## 3. Observations classees

| ID | Observation | Severite | Profils | Cause ou risque principal |
| --- | --- | --- | --- | --- |
| UX-001 | Une edition ferme `Placement et ordre` et fait perdre le contexte. | bloquant | tous | Les cartes sont reconstruites par `renderAll()` apres chaque `change`. |
| UX-002 | Cartes et champs prennent trop de hauteur et de largeur utile. | important | tous | Grilles egalitaires, controle 100 %, marges cumulees et essentiels caches par densite. |
| UX-003 | Les six onglets separent boite/plateaux et elements/conteneurs. | important | novice, intermediaire | Architecture orientee tables techniques plutot que taches et relations. |
| UX-004 | Les onglets manquent de presence ; Precedent/Suivant dupliquent leur role. | amelioration forte | tous | Deux mecanismes concurrents de navigation. |
| UX-005 | Le conteneur cible est une relation abstraite loin du conteneur. | important | novice | Vue plate avec cle etrangere visible au lieu d une composition parent/enfant. |
| UX-006 | `Retrait calcule`, `prise right`, `Preference solveur` et plusieurs labels sont opaques. | important | novice, intermediaire | Codes ou concepts moteur insuffisamment traduits. |
| UX-007 | `Forme` promet plus que la geometrie reelle. | important | tous | Forme de l asset, gabarit de mesure et profil de cavite sont confondus. |
| UX-008 | `Hauteur utilisable` est une deuxieme saisie source fragile. | important | tous | Z interieur, hauteur utilisable et jeu haut peuvent se contredire. |
| UX-009 | Verifier, Recalculer, Estimer et Sauvegarder ne revelent pas leur cycle reel. | important | tous | Etat reactif present mais actions et document courant insuffisamment explicites. |
| UX-010 | Inspecter et les details scene prennent de la place dans le parcours normal. | amelioration | novice | Outils support/dev melanges aux actions produit. |
| UX-011 | L Apercu commence par les metriques avant les vues qui donnent confiance. | amelioration forte | tous | Priorite visuelle inverse de la valeur percue. |
| UX-012 | Presets personnels utilisables mais gestion fragmentee et prompts natifs pauvres. | amelioration | intermediaire, expert | Absence de panneau d edition dedie dans la palette. |
| UX-013 | Les complements proposes dans la vision de toolbar sont encore sans contrat accepte. | question structurante | tous | Ils sont volontairement en quarantaine depuis P66/ADR-0061. |
| UX-014 | Couleurs libres, conteneurs imbriques et profils dessines ouvrent des modeles futurs. | hors scope immediat | expert | Etat, accessibilite, solveur et schema a concevoir separement. |

## 4. Decodage de l interface actuelle

### 4.1 `Retrait calcule`

Ce libelle ne designe pas une dimension retiree. `Numero N` est l **ordre de
retrait**, calcule du haut vers le bas :

- `Numero 1` : premier plateau ou livret a retirer ;
- `Numero 2` : deuxieme ;
- etc.

Le moteur ordonne d abord les valeurs `Position dans la pile` explicites, puis
les elements automatiques par empreinte et identifiant stable. Pour les
empreintes qui se chevauchent, il compose ensuite leurs epaisseurs en Z.

Libelle recommande : `Ordre de retrait` avec la valeur `A retirer en 1er`,
`A retirer en 2e`, ou `Calcule apres mise a jour de l apercu`.

### 4.2 Phrase d encastrement

Exemple actuel :

```text
Origine explicite - encastrement 111.2 x 121.2 x 3 mm - prise right.
```

Elle signifie :

- `Origine explicite` : X et Y ont ete saisis ; sinon BGIG centre l element ;
- `111.2 x 121.2` : empreinte de la decoupe, element plus jeu lateral ;
- `3 mm` : profondeur cumulee creusee depuis le dessus de conception ;
- `prise right` : une reservation rectangulaire de prise est prevue a droite,
  cote choisi parmi les marges disponibles.

Copie recommandee :

```text
Place manuellement a X … / Y …
Encastrement avec jeu : 111,2 x 121,2 mm ; profondeur depuis le dessus : 3 mm.
Zone de prise prevue a droite.
```

Le detail de decoupe peut rester dans une aide ; le premier niveau doit surtout
montrer placement, ordre et statut de prise.

### 4.3 Rotation et bouton X/Y

La rotation actuelle n est pas seulement graphique. Sans choix explicite, le
coeur essaie 0 degre puis 90 degres si l empreinte ne tient pas. Une rotation
explicite est aussi conservee dans les anciens projets et dans le plan resolu.

La proposition UX est compatible a condition de distinguer :

- le bouton `Intervertir X et Y`, qui echange atomiquement les deux mesures ;
- l orientation resolue par le moteur, gardee en lecture seule ;
- `rotation_deg_z`, conserve dans le schema et la compatibilite historique,
  meme s il disparait du parcours normal.

Le bouton devient une regle commune pour les paires de dimensions de boite,
d element, de plateau/livret et de conteneur. Pour un conteneur, il doit
intervertir le contrat complet de chaque axe, mode et valeur, pas seulement deux
nombres. Il ne s applique pas aux coordonnees d origine ou aux positions
resolues.

Le bouton ne doit donc pas deplacer silencieusement l origine X/Y. Pour un
ancien projet avec rotation explicite, un detail technique doit permettre de
revenir a `Automatique` sans migration destructive.

### 4.4 `Hauteur utilisable actuelle`

Aujourd hui, trois valeurs sont stockees : Z interieur, hauteur utilisable et
jeu superieur. La validation exige seulement :

```text
hauteur utilisable <= Z interieur - jeu superieur
```

Le solveur prend ensuite la hauteur utilisable comme plafond. L utilisateur peut
donc saisir une valeur plus petite sans comprendre qu elle limite tous les
conteneurs. Le risque identifie lors de P60 est toujours reel.

Recommandation :

- source novice : `Hauteur interieure Z` ;
- reglage : `Jeu libre sous le couvercle` ;
- derive en lecture seule : `Hauteur de conception` = Z - jeu superieur ;
- valeur `usable_height_mm` conservee pour le schema et les projets legacy ;
- un override legacy ne doit etre exposable que comme exception clairement
  nommee, jamais comme deuxieme mesure normale.

### 4.5 `Preference solveur`

Elle ne change pas les contraintes dures et ne garantit pas un resultat. Elle
change les poids utilises pour classer les propositions deja faisables :

| Choix actuel | Poids dominant | Traduction utilisateur recommandee |
| --- | --- | --- |
| Equilibree | cible 30 %, simplicite 25 %, matiere 25 %, appui 20 % | `Equilibre general` |
| Compacte | simplicite 40 % | `Peu d etages, de rangees et de rotations` |
| Accessible | appui 45 % | `Meilleurs appuis et acces` |
| Impression simple | simplicite 50 % | `Geometrie d arrangement simple` |
| Matiere reduite | distribution de matiere 50 % | `Limiter le surplus de matiere` |

Le mot `Compacte` est trompeur : le sous-score de simplicite penalise surtout
etages, rangees et rotations. Une aide doit dire que le solveur est borne,
heuristique et non globalement optimal.

### 4.6 `Verifier`, `Recalculer` et `Estimer les tailles`

- `Verifier` normalise le projet et recalcule les derives rapides : minima,
  orientations, reservations et diagnostics. Cette operation part deja
  automatiquement 350 ms apres une edition.
- `Recalculer` lance le solveur volumetrique complet et produit une nouvelle
  proposition.
- `Estimer les tailles` appelle exactement le meme solveur que `Recalculer`,
  mais garde l utilisateur dans Conteneurs.
- aucune de ces actions ne modifie automatiquement la scene Fusion.

`Verifier` est donc redondant dans le parcours normal. Le calcul complet reste
plus couteux et peut durer jusqu au timeout actuel de huit secondes.

### 4.7 `Sauvegarder`, importer et exporter

`Sauvegarder` n est pas seulement un tampon memoire. Il ecrit atomiquement le
projet courant dans :

```text
Documents/BGIG/projects/bgig_project_v1.json
```

`Exporter le projet` ecrit un fichier nomme `<nom>.bgig.json` dans le meme
dossier. `Importer` lit un JSON choisi puis remplace aussi le projet courant
sauvegarde. Le manque porte donc sur le **cycle de document** : nom de fichier
courant, Nouveau, Ouvrir, Enregistrer sous, projets recents et recuperation.

L API Fusion fournit un `FileDialog` natif pour ouvrir ou enregistrer et permet
de definir `initialDirectory`. Il est donc possible d ouvrir par defaut le
dossier projets. Le champ HTML `<input type=file>` actuel ne porte pas ce
contrat ; le futur flux doit passer par l adaptateur Fusion, tandis que le coeur
Python reste sans `adsk`.

### 4.8 `Inspecter` et `Effacer la scene BGIG`

Inspecter sert au diagnostic de synchronisation : racine BGIG unique, entites
taguees, incoherences et preservation des objets non-BGIG. Une inspection saine
peut rester automatique et silencieuse.

Recommandation :

- statut scene discret dans la barre ;
- `Inspecter`, rapport brut et `Effacer la scene BGIG` dans `Outils de
  diagnostic` ;
- confirmation avant effacement ;
- pas de retour a un mode avance global melangeant options metier et support.

### 4.9 Case `Cartes sleevees`

Oui, elle indique que les cartes sont sous sleeves. Dans l implementation
0.1.20 :

- un format catalogue passe de la taille de carte a une taille de sleeve
  explicite ; Poker passe de 63,5 x 88,9 a 66 x 91 mm ;
- en mode `nombre de cartes`, BGIG ajoute 0,08 mm par carte a l epaisseur
  unitaire saisie ;
- le jeu element/cavite reste ensuite independant, 0,6 mm par defaut dans un
  projet vierge ; pour un paquet unique, la derivation actuelle ajoute 0,6 mm
  sur chaque cote X/Y, soit 1,2 mm au total, et 0,6 mm en Z ;
- en mode `epaisseur du paquet mesuree`, la valeur Z saisie reste prioritaire.

Le marche ne fournit pas une epaisseur universelle : Gamegenic publie par
exemple des sleeves 66 x 91 mm de 100 microns, alors que certaines Dragon
Shield standard sont annoncees a 120 microns par couche. Double sleeving,
texture et compression changent encore le paquet. Il ne faut donc pas remplacer
la mesure reelle par un unique ajout X/Y/Z presente comme vrai.

Recommandation UX : `Cartes sous sleeves`, format de sleeve visible, dimensions
externes resolues visibles et epaisseur de paquet mesuree recommandee. Le
coefficient 0,08 mm reste un point de depart experimental a confronter a P68,
pas une tolerance print-validee.

### 4.10 Champ `Forme`

La critique est fondee. Aujourd hui :

- `Cartes` active un vrai contrat specifique de paquet et orientation ;
- `Rond` et `Carre` rendent X/Y egaux dans l enveloppe ;
- `Cube` rend X/Y/Z egaux ;
- `Rectangle`, `Pion` et `Sur mesure` gardent l enveloppe saisie ;
- les cavites materialisees restent des enveloppes prismatiques ; un rond n est
  pas encore une cavite cylindrique acceptee V0.2.

Il ne faut pas supprimer brutalement ces valeurs, car elles ont un effet de
normalisation et appartiennent au schema historique. Il faut separer deux
concepts :

1. `Gabarit de mesure de l element` : rond, carre, cube, cartes, libre ;
2. `Profil de cavite` : rectangulaire aujourd hui, puis cylindrique, arrondi,
   pente, fond arrondi, etc. en V0.2.

`Pion` doit plutot devenir un preset de mesure qu une promesse de forme CAD.
Un parcours simplifie peut proposer `Objet libre` et `Cartes` au premier niveau,
avec les autres gabarits via presets, sans retirer les enums du schema.

## 5. Architecture d information proposee

### 5.1 Quatre onglets

Proposition recommandee :

1. `Boite & elements plats` ;
2. `Conteneurs & contenu` ;
3. `Reglages` ;
4. `Apercu`.

Pour garder des onglets courts, le label visible peut etre `Boite`,
`Conteneurs`, `Reglages`, `Apercu`, avec un titre de page explicite :
`Boite, plateaux et livrets` et `Conteneurs et elements du jeu`.

Les onglets deviennent la navigation primaire : contraste plus fort, indicateur
actif, etat complete/a corriger et navigation clavier. `Precedent` et `Suivant`
disparaissent.

### 5.2 Boite, plateaux et livrets

Ordre recommande :

1. dimensions de boite sur une ligne compacte ;
2. derive `Hauteur de conception` ;
3. liste des plateaux et livrets ;
4. action locale d ajout.

La largeur globale des cartes est conservee. Les types recoivent une couleur
semantique subtile et accessible : liseret ou badge, pas un fond fortement
colore. Une personnalisation libre des couleurs est reportee : elle ajoute
persistance, contraste et etats sans valeur fonctionnelle immediate.

`Placement et ordre` devient une zone compacte toujours visible : ordre de
retrait, position de pile, origine X/Y et resultat de placement. Les details de
decoupe restent secondaires.

### 5.3 Conteneurs parents, elements enfants

Le schema actuel convient deja a cette presentation : `container_groups` et
`contents` restent deux collections stables, reliees par
`container_group_id`. L interface peut construire une arborescence sans migration
du fichier et sans logique metier JavaScript.

Structure d une carte :

```text
Conteneur : Bac joueurs                    [etat] [dupliquer] [supprimer]
Taille : min. ... | reglage ... | calculee ...
X [Auto v] [ ... ]   Y [Auto v] [ ... ]   Z [Auto v] [ ... ]

  Elements contenus
  ├─ Cubes rouges    [gabarit] [X] [⇄] [Y] [Z] [qte] [prise/jeu]
  └─ Cartes joueurs  [format] [orientation] [mode de paquet] [...]

  [+ Ajouter un element ici]
```

Le nom editable devient le titre principal. Un badge court `C-003` ou `A-012`
peut aider au support, mais il ne doit pas etre la cle canonique : l identifiant
interne stable reste opaque. Le numero d affichage est un repere, pas une donnee
metier.

Le champ permanent `Conteneur cible` disparait des cartes enfants. Il faut
toutefois conserver une action accessible `Deplacer vers...` dans le menu de
l element ; la composition visuelle ne doit pas rendre la reaffectation
impossible ni dependre uniquement du glisser-deposer.

### 5.4 Barre de creation persistante

Option recommandee, sous les onglets et au-dessus de la liste :

```text
Element : [preset........................ v] [dans Bac joueurs / nouveau... v] [Ajouter]
Conteneur : [Conteneur standard v] [Creer]
```

Elle peut passer sur deux lignes dans une palette etroite. Chaque conteneur
garde aussi un petit raccourci `Ajouter un element ici`.

Quand un preset personnel est selectionne, `Modifier` et `Supprimer` deviennent
disponibles. `Modifier` ouvre de preference un panneau lateral dans la palette,
avec focus piege, Echap/Annuler et Enregistrer. Fusion autorise un HTML riche et
dynamique dans une palette ; il n est pas necessaire de creer une application
externe ou un navigateur.

### 5.5 Complements

La liste `Bac vide / Bloc plein / cale / Separateur` ne peut pas etre remise dans
la barre comme un simple preset. Ces objets sont des `fill_elements`, pas des
variantes de `container_group`, et leurs semantiques de dimensionnement,
suggestion, appui et confirmation ont ete refusees pour le MVP.

Trois options restent ouvertes :

| Option | Principe | Evaluation |
| --- | --- | --- |
| A | Garder la quarantaine et creer seulement un conteneur standard. | Recommandee maintenant ; respecte P66 et evite une fausse promesse. |
| B | Reactiver les trois types dans la passe UX. | Refusee sans nouveau contrat ; melange refonte UI et comportement produit. |
| C | Cadrer plus tard des `Corps de support` explicites, suggeres mais confirmes. | Candidate apres retours reels ; ADR et missions propres obligatoires. |

Changer le type d un conteneur vide ne doit pas etre implemente comme une simple
liste : ce serait une migration entre deux types d entites. Si ce besoin est
accepte plus tard, la transformation doit etre explicite, reversible et testee.

## 6. Systeme de densite et de composants

### 6.1 Principe

`Compact` ne doit plus signifier « cacher tous les champs editables ». Le mode
normal montre toujours les donnees necessaires a la tache. Les details
techniques, historiques et rarement modifies peuvent seuls etre replies.

La compacite vient de :

- colonnes adaptees au contenu plutot que deux colonnes 50/50 ;
- lignes X/Y/Z/quantite groupees ;
- labels courts mais explicites au-dessus des valeurs ;
- espaces et bordures reduits ;
- actions secondaires en icones accessibles ;
- resume et edition reunis, sans titre duplique ;
- cartes enfants visuellement plus legeres que leur conteneur parent.

### 6.2 Dimensions indicatives a prototyper

Ces valeurs sont des cibles de prototype, pas encore un contrat accepte :

- nom : `minmax(150px, 2fr)` ;
- type ou preset : `120-160px` ;
- X/Y/Z : `72-92px` chacun ;
- quantite : `64-76px` ;
- actions icones : cible interactive d au moins 40 px ;
- controle : 36-40 px visuels, sans descendre sous la cible d accessibilite de
  40 px definie par le contrat Fusion-only ;
- espace vertical entre groupes : 6-8 px ;
- padding de carte parent : 10-12 px ; enfant : 8-10 px.

Sur palette etroite, les dimensions passent sur une deuxieme ligne coherente au
lieu de devenir chacune pleine largeur.

### 6.3 Labels et aide

Une `title` HTML seule ne suffit pas : elle est peu decouvrable, souvent
indisponible au clavier/tactile et trop courte. Chaque champ doit avoir :

1. un label visible ;
2. une unite ou un exemple pres de la valeur ;
3. une aide courte par bouton `?` accessible au clavier ;
4. si necessaire, une fiche plus longue dans un panneau d aide.

Les icones sont recommandees pour dupliquer, supprimer, deplacer, intervertir
X/Y et ouvrir les details. Une icone ambigue comme `Preset` garde un label ou
une info-bulle accessible. Aucune action ne doit etre disponible uniquement au
survol.

### 6.4 Etat de saisie

Le premier correctif doit supprimer la reconstruction aveugle des listes. Deux
strategies sont acceptables :

- mise a jour incrementale et composants DOM stables, recommandee ;
- preservation explicite avant rendu des details ouverts, focus, selection,
  scroll et identifiant de ligne, puis restauration.

Les tests doivent modifier successivement plusieurs champs d une meme carte et
verifier que le panneau, le focus, la selection de texte et le scroll restent
stables, y compris avec cinquante conteneurs.

## 7. Cartes et presets

### 7.1 Deux modes de paquet

Remplacer la liste actuelle par un controle segmente clair :

- `Paquet mesure` : saisir directement epaisseur totale Z ;
- `Nombre de cartes` : saisir quantite et epaisseur d une carte.

Seuls les champs du mode choisi sont editables. Les dimensions resolues X/Y/Z
restent toujours visibles, ainsi que la provenance `mesure`, `catalogue` ou
`calcul`.

### 7.2 Presets personnels

Conserver import/export et ajout depuis un element existant. Ajouter par lots :

- selection dans la meme liste que les presets integres avec section visuelle ;
- edition dans un panneau lateral ;
- duplication et renommage ;
- suppression confirmee ;
- schema versionne et stockage hors package ;
- aucun compte ou cloud impose.

### 7.3 Formes futures

La future V0.2 doit modeliser le profil de cavite separement du gabarit de
mesure. Les candidats sont : rectangle, cylindre, coins internes arrondis, fond
arrondi ou incline, encoche et jeu de prise. Chaque option doit modifier le
volume utile et la CAD, pas seulement l icone.

Le dessin libre d un preset est reporte apres P69 : il demanderait au minimum
un contour 2D ferme, une normalisation d unite, des controles d auto-intersection,
des rayons fabricables, une preview et une strategie de migration. Il ne faut
pas le pre-coder dans le schema V0.2.

## 8. Reglages, calcul et Apercu

### 8.1 Reglages fins

Renommages proposes :

- `Paroi minimale par defaut` -> `Epaisseur minimale de paroi` ;
- `Fond minimal par defaut` -> `Epaisseur minimale de fond` ;
- `Jeu bac / boite Z (haut)` -> `Jeu libre sous le couvercle` ;
- `Jeu element / cavite par defaut` -> `Jeu element-cavite` ;
- `Preference solveur` -> `Priorite de la proposition`.

Les reglages utiles restent visibles dans des sections compactes avec titres,
pas dans un `<details>` referme. Les outils scene et donnees moteur vivent dans
le tiroir diagnostic.

### 8.2 Calcul automatique : options

| Option | Comportement | Avantages | Risques |
| --- | --- | --- | --- |
| A - Explicite actuel | Derives automatiques ; solve sur bouton. | Deterministe, aucune charge surprise. | Friction, boutons mal compris. |
| B - Toujours automatique | Solve apres chaque pause de saisie. | Impression de produit direct. | Calculs repetes, reponses obsoletes, instabilite sur grands projets. |
| C - Hybride adaptatif | Derives 300-400 ms ; solve apres 1-2 s stable si valide, avec annulation logique et fallback manuel. | Fluide sans materialisation automatique ; robuste si bien garde. | Etat asynchrone et tests plus exigeants. |

Recommandation : option C, apres stabilisation du rendu. `Verifier` disparait du
parcours normal. `Recalculer maintenant` peut rester dans le diagnostic ou
apparaitre uniquement quand l auto-calcul est suspendu/echec. Toute
materialisation Fusion reste explicitement humaine.

### 8.3 Apercu

Ordre visuel recommande :

1. statut compact `Pret / A recalculer / Partiel / Impossible` ;
2. vue dessus et coupe ;
3. alertes actionnables ;
4. action primaire `Materialiser dans Fusion` ;
5. details de corps, appuis, retrait, score et residuels.

Les futurs curseurs de coupe X/Z et de plan Z sont des outils de lecture utiles,
mais ne doivent pas bloquer la fondation UX. Ils sont candidats post-geometrie,
quand la preview represente aussi les rayons et couvercles.

## 9. Cycle de document projet recommande

Option recommandee : **document nomme + sauvegarde de recuperation**.

- `Nouveau projet` initialise un document sans ecraser un fichier nomme ;
- `Ouvrir` utilise le FileDialog Fusion dans `Documents/BGIG/projects` ;
- `Enregistrer` ecrit le fichier courant ;
- `Enregistrer sous` demande un nom et un chemin ;
- `Exporter une copie` conserve la semantique actuelle d export ;
- une sauvegarde de recuperation atomique protege les changements non encore
  enregistres ;
- le titre montre nom, chemin court et etat `Modifie` ;
- importer un ancien schema normalise sans ecraser silencieusement l original ;
- une liste de projets recents est locale et sans cloud.

Le coeur continue de normaliser et serialiser. Seul l adaptateur Fusion ouvre
les boites de dialogue natives. Aucun import `adsk` n entre dans `src/`.

## 10. Fonctions futures enregistrees sans engagement de version

### 10.1 Plateaux dessous, dessus ou couvercles

Trois semantiques distinctes doivent rester separees :

- `top inset` actuel : element plat encastre depuis le dessus ;
- reservation inferieure : element plat sous les conteneurs, avec support et
  ordre de montage differents ;
- plateau servant de fermeture : empreinte et appui coordonnes pour couvrir un
  ou plusieurs conteneurs.

Les deux dernieres changent le solveur, les contraintes d acces et la CAD. Le
mode fermeture doit etre arbitre avec P47-P50 pour ne pas inventer un deuxieme
contrat de couvercle. Ils ne sont pas des options UI gratuites.

### 10.2 Conteneurs de conteneurs

La vue parent/enfant proposee ne doit pas etre confondue avec un schema recursif.
Un futur conteneur dans un conteneur exigerait relations de composition,
transformations locales, support, retrait, collisions, hauteur et ordre de
materialisation. Le futur modele devrait privilegier un graphe d identifiants et
de relations explicites plutot qu un JSON imbrique sans limite.

Ce besoin reste candidat P70+ apres P69. Aucune profondeur supplementaire n est
ajoutee maintenant.

### 10.3 Couleurs utilisateur

Des badges semantiques fixes peuvent arriver dans la fondation. Les couleurs
personnalisees par utilisateur sont reportees : il faudra definir persistance,
contraste, themes clair/sombre, export et comportement en cas de couleur
illisible.

### 10.4 Profiles dessines et coupes parametrables

Le dessin de cavite libre et les coupes de preview parametrables sont conserves
comme hypotheses post-P69. Ils devront etre recadres en capabilities et ADR
distinctes, pas ajoutes opportunement a P45.

## 11. Options de sequencement P67

### Option A - Conserver geometrie d abord

- P44 contrat de formes ; P45 geometries ; P46 gate ; UX structurelle apres P50.
- Avantage : respecte la lecture initiale d ADR-0061.
- Risque : ajoute de nombreux champs sur une architecture deja jugee fragile et
  augmente le cout de la future refonte.

### Option B - Correctif de compacite minimal, puis geometrie

- corriger focus/sections et CSS, sans changer les onglets ni la composition ;
- reprendre ensuite P44-P46 initial.
- Avantage : faible cout immediat.
- Risque : ne corrige pas la separation Elements/Conteneurs ni le cycle projet.

### Option C - Fondation UX bornee dans P44, puis geometrie dans P45

- P44 porte la stabilite, la densite, l architecture quatre onglets, la
  composition conteneur/contenu et le cycle document ;
- une gate Fusion UX bornee ferme P44 ;
- P45 ajoute ensuite les formes ergonomiques sur ces composants stabilises ;
- P46 valide preview, Fusion et V0.2 complete.

Avantages : evite de jeter des formulaires geometrie, ameliore vite la prise en
main et garde P69 comme audit final. Inconvenient : reoriente P44 et demande un
amendement accepte.

**Recommandation : option C.**

## 12. Decoupage de missions propose, encore bloque

Les identifiants ci-dessous preservent P44-P50. Seule P67-V peut les autoriser.

### P44-M001 - Stabilite de saisie et contrat d etat UI

- Cause unique : aucune edition ne doit detruire focus, panneau ouvert ou scroll.
- Aucun changement de schema, solveur, tolerance, geometrie ou scene.
- Tests : saisies successives, reponse derivee asynchrone, cinquante cartes,
  navigation clavier et preservation de selection.

### P44-M002 - Densite compacte et composants accessibles

- Grilles adaptees au contenu, titres/labels, X/Y/Z/quantite compacts, icones
  accessibles et sections essentielles toujours visibles.
- Prototype dans plusieurs largeurs de palette ; cible interactive >= 40 px.

### P44-M003 - Quatre onglets et Boite + elements plats

- Onglets renforces, suppression Precedent/Suivant, fusion Boite/plateaux,
  ordre de retrait traduit et bouton X/Y.
- Schema et semantique top-inset conserves.

### P44-M004 - Conteneurs parents et elements enfants

- Projection imbriquee depuis les collections actuelles ; nom unique comme
  titre ; action Deplacer vers ; pas de schema recursif.
- Suppression du champ conteneur cible permanent, sans perdre la reaffectation.

### P44-M005 - Barre de creation et gestion des presets

- Toolbar persistante, preset + destination, raccourci local, panneau d edition
  des presets personnels.
- Complements toujours en quarantaine.

### P44-M006 - Reglages, document projet et diagnostic

- Labels/hints, hauteur derivee, FileDialog natif, Nouveau/Ouvrir/Enregistrer
  sous, recuperation et outils scene dans le diagnostic.
- Migration additive et coeur toujours sans adsk.

### P44-M007 - Calcul adaptatif et Apercu priorise

- Option de calcul retenue par P67, suppression de Verifier normal, gestion de
  requetes obsoletes et vues placees avant les metriques.
- Materialisation toujours explicite et gardee.

### P44-V - Gate humaine de fondation UX

- Parcours novice et expert dans petite/grande palette ; clavier, focus,
  cinquante conteneurs, import ancien projet et scene existante.
- Cette gate qualifie la fondation de palette, pas la geometrie V0.2 ni
  l impression.

### P45 et P46

P45 reprend ensuite, mission par mission, le profil de cavite, coins externes,
chanfreins, encoches, fonds faciles a vider et contraintes de resistance. P46
reste la gate Fusion de l ensemble V0.2 avec preview fidele.

## 13. Matrice de priorite

| Sujet | Valeur | Effort | Risque | Dependances | Horizon recommande |
| --- | --- | --- | --- | --- | --- |
| Focus/sections stables | tres haute | faible-moyen | faible | aucune | premier lot |
| Densite et labels | tres haute | moyen | faible | etat stable | fondation P44 |
| Quatre onglets | haute | moyen | moyen | composants stables | fondation P44 |
| Conteneur parent / elements enfants | tres haute | moyen-fort | moyen | IA acceptee | fondation P44 |
| Toolbar creation/presets | haute | moyen | moyen | composition acceptee | fondation P44 |
| Cycle de document complet | haute | moyen-fort | moyen | bridge/adaptateur | fondation P44 |
| Auto-calcul adaptatif | haute | moyen-fort | moyen-fort | etat stable | fin fondation P44 |
| Apercu en premier | haute | faible | faible | aucune | fondation P44 |
| Vraies formes de cavite | haute | fort | fort | fondation UX + contrat resistance | P45 |
| Reactivation complements | incertaine | fort | fort | nouveau contrat | apres preuves |
| Plateaux dessous/fermeture | potentiellement haute | fort | fort | solveur + couvercles | a arbitrer P47+/P70+ |
| Conteneurs imbriques | experte | tres fort | tres fort | nouveau graphe | P70+ |
| Couleurs utilisateur | faible-moyenne | moyen | faible-moyen | accessibilite | P70+ |
| Profil dessine libre | experte | tres fort | tres fort | nouveau modele CAD | P70+ |

## 14. Decisions P67 a rendre

| Decision | Recommandation | Statut |
| --- | --- | --- |
| D67-01 - Fondation UX avant geometrie | Option C | a arbitrer |
| D67-02 - Quatre onglets et suppression Precedent/Suivant | accepter | a arbitrer |
| D67-03 - Conteneur parent / elements enfants sans migration schema | accepter | a arbitrer |
| D67-04 - Toolbar creation proposee | accepter, avec complements exclus | a arbitrer |
| D67-05 - Complements | garder en quarantaine ; futur contrat separe | a arbitrer |
| D67-06 - X/Y | bouton d interversion ; rotation historique conservee | a arbitrer |
| D67-07 - Calcul | hybride adaptatif, jamais de scene auto | a arbitrer |
| D67-08 - Projet | document nomme + recuperation autosauvee | a arbitrer |
| D67-09 - Formes | separer gabarit asset et profil de cavite | a arbitrer |
| D67-10 - Couleurs | accents semantiques fixes maintenant, perso plus tard | a arbitrer |
| D67-11 - P44-M001 | stabilite de saisie uniquement | bloque par P67-V |

## 15. Criteres de sortie P67

P67 pourra etre accepte seulement quand Thomas aura :

1. choisi l option de sequencement ;
2. accepte ou corrige l architecture quatre onglets ;
3. tranche la toolbar et le maintien en quarantaine des complements ;
4. choisi le mode de recalcul ;
5. choisi le cycle de document ;
6. accepte le premier lot P44-M001 et ses exclusions ;
7. accepte ou refuse ADR-0062.

Jusque-la :

- P44-M001 reste `blocked-by-p67-v` ;
- P45/P46 ne commencent pas ;
- P47-P50 restent bloques par P46 ;
- P69 reste bloquee par P50 ;
- `print-validated: false` reste obligatoire.

## 16. Sources techniques externes consultees

- Autodesk Fusion API, palettes et communication HTML :
  <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Palettes_UM.htm>
- Autodesk Fusion API, boite de dialogue ouvrir/enregistrer et dossier initial :
  <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/FileDialog.htm>
- Gamegenic, sleeve standard 66 x 91 mm et epaisseur annoncee de 100 microns :
  <https://www.gamegenic.com/product/standard-card-game-value-pack-200/>
- Dragon Shield, variation de sleeves standard annoncees a 120 microns par
  couche :
  <https://www.dragonshield.com/en-us/card-sleeves/shop-by-size/standard-sized-sleeves>

Ces references confirment des possibilites d interface et des ordres de grandeur.
Elles ne constituent ni une calibration BGIG ni une validation d impression.
