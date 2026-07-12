# P54 - Architecture UX de l editeur premium

## Statut

Reference UX executable pour P55-P60. Ce document decrit le produit a construire,
pas l interface P38 actuelle.

Prototype visuel : `docs/prototypes/p54_premium_editor_wireframe.html`.

## Promesse de l ecran

Une personne ouvre BGIG, mesure sa boite, ajoute ses assets et plateaux, choisit
quels assets partagent un bac, ajuste les jeux utiles puis construit un insert
complet sans rencontrer un terme moteur ou un fichier CAD.

L editeur montre peu de decisions a la fois mais ne retire aucun pouvoir : les
reglages avances s ouvrent dans le contexte de la boite, d un asset ou d un bac.

## Structure generale

Sur grand ecran, l application utilise trois zones stables :

| Zone | Largeur cible | Role |
| --- | ---: | --- |
| Rail projet | 216 px | Navigation, progression, statut de sauvegarde |
| Espace de travail | fluide, min 640 px | Formulaires et tableaux dynamiques |
| Apercu | 360 px | Plan live, hauteur, alertes, resume du projet |

Le rail et l apercu restent visibles pendant la saisie. Sous 1100 px, le rail
devient une barre horizontale compacte et l apercu passe sous l espace actif.
Sous 720 px, chaque ligne de tableau devient une carte verticale avec actions
toujours accessibles.

## Navigation produit

Le parcours est une seule application, pas une serie de modales :

1. `Boite`
2. `Assets`
3. `Plateaux et livrets`
4. `Bacs`
5. `Fabrication`
6. `Resultat`

Chaque etape est accessible a tout moment. Le rail indique `A completer`, `Pret`
ou `Calcule`. Aucun verrou artificiel n empeche de revenir corriger une mesure.

Le bouton primaire global change avec l etat :

- projet incomplet : `Voir les points a corriger` ;
- projet valide : `Construire mon insert` ;
- resultat existant et saisie modifiee : `Recalculer` ;
- resultat accepte : `Ouvrir dans Fusion`.

## Ecran Boite

### Visible par defaut

- nom du projet ;
- largeur, profondeur et hauteur interieures ;
- jeu contre la boite ;
- jeu entre les bacs ;
- schema de mesure simple ;
- volume utilisable calcule en direct.

### Avance

- marge sous couvercle de la boite du jeu ;
- orientation de reference ;
- valeurs verrouillees ;
- profil d impression selectionne, sans promesse de validation physique.

Les erreurs sont attachees au champ : `La largeur doit etre superieure a 0 mm`,
jamais `INVALID_DIMENSION`.

## Ecran Assets

Le tableau est le coeur du MVP. Une ligne represente une famille d assets.

| Colonne | Controle | Comportement |
| --- | --- | --- |
| Asset | nom libre | preselectionne a la creation |
| Forme | rond, carre, rectangle, cartes, cube/de, pion, sur mesure | adapte les libelles de mesures |
| Mesures | 1 a 3 champs selon forme | millimetres visibles dans chaque champ |
| Quantite | entier positif | modifie l arrangement de cavite |
| Bac | liste des bacs + `Nouveau bac` | regroupe explicitement les familles |
| Jeu | herite ou surcharge | replie dans la ligne par defaut |
| Actions | dupliquer, supprimer, details | jamais cachees au survol uniquement |

Le bouton `Ajouter un asset` ajoute une ligne visible et place le focus dans son
nom. `Dupliquer` conserve forme et mesures mais cree un identifiant stable neuf.

### Details avances de ligne

- confiance de mesure ;
- orientation autorisee ;
- jeu propre a l asset ;
- notes ;
- verrou de pile ou d arrangement, uniquement si le moteur le supporte.

## Ecran Plateaux et livrets

Tableau separe obligatoire :

- nom ;
- type `Plateau`, `Livret`, `Aide de jeu`, `Autre` ;
- largeur, profondeur, epaisseur ;
- quantite ;
- ordre automatique ou indice manuel ;
- orientation autorisee.

Une coupe de hauteur montre immediatement la pile reservee et la hauteur restante
pour les bacs. Une ligne qui depasse la boite est marquee avant construction.

## Ecran Bacs

Les bacs sont derives des choix `Bac` du tableau Assets. La personne ne dessine
pas de module technique.

Chaque carte de bac montre :

- nom humain et couleur stable ;
- assets contenus ;
- nombre de cavites ;
- enveloppe minimale calculee ;
- paroi et fond minimaux ;
- statut `Peut grandir pour remplir la boite` ;
- preview locale des cavites.

### Reglages avances par bac

- paroi minimale ;
- fond minimal ;
- axes autorises pour l expansion X/Y/Z ;
- dimension exterieure verrouillee sur un axe ;
- preference `plus de paroi` / `plus de fond` ;
- alignement souhaite avec un autre bac ;
- priorite de surface sous les plateaux.

La copie explique l invariant : `Les cavites gardent leurs mesures. Le surplus
de place epaissit ce bac autour et sous son contenu.`

## Complements explicites

Les complements sont secondaires et replies sous `Ajouter un element sans
asset`. Trois types existent : bac vide, volume plein, separateur.

BGIG n en ajoute jamais. Chaque ajout affiche un badge `Ajoute manuellement` et
demande soit des dimensions, soit des contraintes d expansion explicites.

## Ecran Fabrication

### Reglages essentiels

- jeu autour des assets ;
- paroi minimale ;
- fond minimal ;
- jeu entre bacs ;
- jeu contre la boite.

### Avance

- profil d impression ;
- compensation par axe si deja supportee ;
- priorite de repartition du surplus ;
- bornes de temps du solveur ;
- diagnostic technique exportable.

Les valeurs globales affichent leurs surcharges : `2 bacs utilisent une valeur
personnalisee` avec lien vers les cartes concernees.

## Apercu permanent

Avant calcul complet, l apercu affiche seulement des donnees certaines : contour
de boite, pile plateaux/livrets, bacs demandes et alertes de saisie. Il porte le
badge `Apercu de saisie`.

Apres calcul P57, il porte `Plan calcule` et utilise exclusivement les placements
du moteur. Il montre :

- vue de dessus avec limites reelles des bacs ;
- cavites comme zones interieures distinctes ;
- coupe de hauteur ;
- legende des bacs ;
- total des corps demandes ;
- `0 corps automatique` ;
- volume absorbe par parois/fonds.

Le dessin indicatif P38 en colonnes egales est interdit dans l etat resultat.

## Ecran Resultat

Le resultat remplace le formulaire principal sans perdre la saisie, accessible
par `Modifier le projet`.

En tete :

- `Insert construit`, `Partiel` ou `Impossible` ;
- nombre de bacs demandes et materialises ;
- nombre de complements explicites ;
- confirmation `Aucun corps automatique` ;
- hauteur totale et pile superieure.

Pour chaque bac : contenu, cavites calibrees, enveloppe minimale, enveloppe
finale, matiere ajoutee dans parois et fond, position et avertissements.

Actions : `Modifier`, `Recalculer`, `Accepter ce plan`, puis `Ouvrir dans Fusion`.
Fusion ne peut etre lance avant acceptation explicite du plan courant.

## Etats obligatoires

| Etat | Message principal | Action |
| --- | --- | --- |
| Chargement court | `Ouverture de ton projet` | indicateur anime avec timeout |
| API absente | `Le Studio local ne repond pas` | `Reessayer` + aide de lancement |
| Projet vide | `Commence par mesurer ta boite` | focus premiere mesure |
| Saisie invalide | `3 points a corriger` | liens vers les champs |
| Pret | `Tout est pret pour construire` | bouton construire |
| Calcul | `BGIG cherche une partition simple` | progression et annulation si supportee |
| Impossible | cause en langage courant | suggestions concretes |
| Resultat obsolete | `Le projet a change` | recalculer |
| Resultat accepte | `Plan pret pour Fusion` | ouvrir Fusion |

Aucun ecran ne reste sur `Chargement...` sans timeout, cause ou action.

## Langage visuel

Direction : atelier de precision contemporain, calme et premium.

- fond gris chaud tres clair ;
- surfaces blanches opaques, bordures fines, ombres courtes ;
- texte principal bleu nuit, texte secondaire ardoise ;
- accent principal corail cuivre pour les actions ;
- accent secondaire bleu petrol pour les statuts et le plan ;
- couleurs de bacs douces mais nettement distinctes ;
- rayon principal 14 px, rayon de panneau 20 px ;
- densite moyenne : 44 px minimum pour les controles, tables compactes mais
  respirantes ;
- typographie systeme sobre, echelle 12/14/16/20/28/36 ;
- aucune grande hero marketing dans l editeur de travail.

## Composants a construire en P56

- `AppShell`, `ProjectRail`, `ProjectHeader` ;
- `StepStatus`, `Field`, `NumberField`, `InlineError` ;
- `EditableTable`, `AssetRow`, `FlatItemRow` ;
- `ContainerCard`, `AdvancedDrawer`, `ExplicitFillRow` ;
- `LivePreview`, `HeightSection`, `ProjectSummary` ;
- `BuildBar`, `ResultWorkspace`, `ContainerResultCard` ;
- `EmptyState`, `LoadingState`, `ErrorState`, `Toast`.

## Accessibilite

- navigation clavier complete et ordre logique ;
- focus visible 2 px minimum ;
- labels accessibles independants des placeholders ;
- suppression avec nom de l element dans l aria-label ;
- couleurs jamais seules porteuses de statut ;
- contraste WCAG AA pour textes et controles ;
- zones tactiles 44 x 44 px ;
- tableaux transformes en cartes lisibles sur mobile.

## Hors scope P54

- implementation React ;
- nouveau schema moteur ;
- solveur ;
- CAD/Fusion ;
- esthetique V0.2 des corps imprimes ;
- couvercles V0.3.

P54 fixe la reference. P55 implemente le contrat metier necessaire ; P56 traduit
ensuite cette architecture dans le frontend reel.
