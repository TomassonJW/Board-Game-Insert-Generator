# P60 - Realignement produit apres revue dans Fusion

## Statut

`product-review-ko`, `technical-baseline-useful`, `docs-only`,
`implementation-not-authorized-by-this-mission`, `print-validated: false`.

## Objet du document

Ce document transforme la revue humaine du 2026-07-12 en plan produit et
technique exploitable. Il ne modifie aucun runtime. Il distingue :

- ce qui est une dette de presentation ;
- ce qui est une dette de modele produit ;
- ce qui est une limite du solveur P57 ;
- ce qui appartient toujours aux formes et a l ergonomie V0.2 ;
- les decisions structurantes a prendre avant de reprendre le code.

La surface produit reste exclusivement l add-in Fusion et sa palette embarquee
selon ADR-0055. Le coeur reste Python pur et sans adsk.

## Verdict executif

La base P56-P59 est utile : edition embarquee, projet persistant, calcul pur,
preview reelle et materialisation Fusion fonctionnent. Elle ne constitue pas
encore un produit V0.1 acceptable.

Le probleme principal n est pas la taille des cartes UI. Le modele actif reste
un solveur de rangees XY dont tous les corps prennent la hauteur de stockage
complete. Les plateaux sont une pile globale retiree au-dessus de tous les bacs.
Cette architecture explique directement :

- les erreurs des que plusieurs etages deviennent necessaires ;
- les axes non extensibles qui rendent le calcul impossible ;
- les fonds et parois enormes ;
- le manque d adaptation apres modification de la boite ;
- la semantique confuse des hauteurs ;
- l impossibilite de produire l encastrement de plateau souhaite.

Recommandation : ne pas reprendre P61 comme simple champ `nombre de bacs en
hauteur`. Reouvrir la convergence V0.1 autour de cinq contrats separes : etat
reactif, catalogue d elements, reservations superieures encastrees, solveur
volumetrique et architecture d interface progressive.

## Comprendre les termes actuels

### Hauteur utilisable

Aujourd hui, `box.inner_dimensions_mm.z`, `box.usable_height_mm` et
`box.lid_clearance_mm` sont trois saisies independantes. Le moteur prend le
minimum entre Z interieur et hauteur utilisable. La marge sous couvercle est
supposee deja integree dans la hauteur utilisable et n est pas soustraite une
seconde fois.

Cette double saisie est fragile. Deux valeurs peuvent se contredire sans que
l utilisateur sache laquelle pilote le resultat.

Recommandation :

- conserver `Hauteur interieure Z` comme mesure source ;
- placer `Jeu superieur` dans Reglages ;
- afficher `Hauteur de conception = Z interieur - jeu superieur` en lecture
  seule ;
- migrer `usable_height_mm` comme valeur derivee ou override legacy explicite,
  jamais comme deuxieme mesure novice.

### Hauteur reservee des plateaux

P40 additionne actuellement epaisseur x quantite pour tous les plateaux et
livrets, ajoute le jeu de layout, puis soustrait cette valeur a toute la hauteur
des bacs. `Hauteur reservee 0 mm` signifie soit qu aucun element plat valide
n est present, soit qu aucun rapport recalcule n est disponible apres edition.

Ce concept est coherent avec une pile uniforme posee au-dessus de tous les bacs,
mais il ne correspond pas a la cible produit de cette revue.

### Ordre optionnel

`stack_order` definit actuellement l ordre vertical de la pile plateaux/livrets.
Les valeurs renseignees passent avant les valeurs automatiques. Ce champ est trop
technique et son effet n est pas visible.

Recommandation : ordre automatique par defaut, puis reordonnancement visuel par
glisser-deposer ou boutons haut/bas seulement quand plusieurs elements se
chevauchent. Aucun entier brut dans le parcours principal.

### Confiance de mesure

`measurement_confidence` vient du modele asset-first historique. Il distingue
`exact` et `approximate`, mais le parcours actuel ne change ni le solveur ni la
geometrie en fonction de cette valeur.

Recommandation : retirer ce champ de l interface normale. Le conserver dans le
schema pour migration et audit. Une future option locale `Mesure approximative`
pourra seulement produire un avertissement ou une marge proposee explicite.

### Pile et supports

`supported_by_requested_bodies` signifie seulement que des corps demandes
intersectent la projection de la reservation et atteignent son niveau Z. Le
libelle est un code moteur et ne doit jamais etre affiche.

Recommandation UI : `Appui des plateaux et livrets`, avec :

- `Surface appuyee` ;
- `Zones sans appui` ;
- `Prise disponible` ;
- un schema ;
- un detail technique replie.

### Score de simplicite

Le score P57 vaut actuellement 1000 moins une penalite de lignes, rotations et
deséquilibre de surplus. Il n a pas de sens utilisateur autonome et n explique
ni accessibilite, ni matiere, ni hauteur, ni temps d impression.

Recommandation : ne plus afficher le nombre brut en premier niveau. Afficher des
sous-criteres nommes :

- peu de conteneurs ;
- peu de rotations ;
- parois equilibrees ;
- accessibilite ;
- hauteur et empilement ;
- matiere estimee ;
- complexite d impression.

Un lien `Comment cette proposition est evaluee ?` ouvre une aide courte puis le
detail complet.

## Parcours cible recommande

1. `Boite`
2. `Plateaux et livrets`
3. `Elements du jeu`
4. `Conteneurs`
5. `Reglages`
6. `Apercu`

`Elements du jeu` est recommande plutot que `Pieces` ou `Assets` : il reste
comprehensible pour un novice et couvre cartes, jetons, des, pions et accessoires.
Le terme interne reste `Asset` dans le coeur.

`Conteneurs` est recommande plutot que `Bacs` : un conteneur peut etre un bac a
cavites, un bac vide, une cale pleine ou un separateur.

`Apercu` est recommande plutot que `Resultat` : la vue precede encore la
materialisation et l export.

## Architecture d information cible

### Pas de mode avance global

Le bouton `Mode avance` doit disparaitre. Il melange des notions sans rapport et
cache des controles utiles. La puissance reste disponible par divulgation
progressive locale :

- chaque ligne a un resume compact ;
- `Developper` ouvre les details de cette ligne ;
- chaque section a une aide contextuelle ;
- les diagnostics techniques vivent dans un tiroir separe ;
- aucun controle non implemente ne doit apparaitre comme actif.

### Deux densites de liste

Les listes Elements et Conteneurs proposent :

- `Compact` par defaut : une ou deux lignes avec nom, type, dimensions,
  quantite, orientation et conteneur ;
- `Detaille` : carte actuelle enrichie, ouverte une ligne a la fois ;
- un changement de densite global a la liste, persiste localement ;
- edition clavier et ordre stable dans les deux modes.

### Barre d actions persistante

Afficher huit gros boutons en permanence recreerait une autre surcharge. La
barre doit avoir trois zones et des priorites :

| Zone | Actions visibles | Actions secondaires |
| --- | --- | --- |
| Gauche | Verifier, Recalculer | diagnostics |
| Centre | Importer, Exporter le projet | Inspecter dans un menu Scene |
| Droite | Etat de sauvegarde, Precedent, Suivant | Exporter les STL dans Apercu |

`Sauvegarder` devient idealement un etat autosauvegarde avec action de secours.
`Materialiser dans Fusion` et `Exporter les imprimables` restent des actions
primaires de l Apercu, pas des commandes banales sur tous les ecrans.

### Hierarchie des messages

Le rapport brut `inspect_bgig_scene` ne doit jamais etre une notification en
haut. Quatre niveaux sont necessaires :

1. erreur utilisateur bloquante en haut de la vue concernee ;
2. avertissement court et actionnable pres du champ ;
3. statut discret dans la barre basse : `Scene BGIG saine - 3 corps` ;
4. tiroir `Details techniques` avec resume tronque et `Voir plus`.

Au demarrage, un inspect sain ne produit aucun message global. Seule une
incoherence produit un avertissement court. Le rapport complet reste copiable.

## Etat reactif et priorite des valeurs

### Probleme actuel

`markDirty()` supprime le dernier rapport et le dernier plan. Aucun calcul
intermediaire n est relance. La scene Fusion existante reste visible sans
distinction assez forte entre projet courant et scene obsolete.

### Modele recommande

Separarer quatre etats :

- `source` : mesures et intentions saisies ;
- `derived` : minima, hauteur derivee, reservations et avertissements rapides ;
- `solved` : proposition volumetrique complete associee a un digest source ;
- `materialized` : scene Fusion associee au digest du plan.

Une edition :

1. modifie toujours la source ;
2. recalcule les derives rapides apres 250-400 ms ;
3. marque le plan `A recalculer` ;
4. conserve l ancien apercu grise avec la mention `Ancienne proposition` ;
5. ne modifie jamais automatiquement la scene Fusion ;
6. propose `Recalculer` ;
7. apres calcul, propose `Mettre a jour Fusion` si le digest a change.

### Priorites de contraintes

| Priorite | Type | Exemple | Comportement |
| ---: | --- | --- | --- |
| 1 | limite physique dure | dimensions de boite | jamais depassee |
| 2 | contenu dur | dimensions et quantites | jamais reduit silencieusement |
| 3 | fabrication dure | paroi/fond minimum | jamais violee |
| 4 | verrou utilisateur dur | X final fixe | respecte ou diagnostic local |
| 5 | cible utilisateur souple | `viser 80 mm` | ajustable si le plan l exige |
| 6 | preference souple | surplus equilibre | contribue au score |
| 7 | derive | taille finale proposee | recalculee a chaque solution |

Chaque dimension de conteneur doit donc accepter trois modes explicites :

- `Auto` ;
- `Cible` : le solveur essaie de s en approcher ;
- `Fixe` : contrainte dure.

Cela resout le conflit entre valeurs proposees et adaptabilite globale.

## Plateaux et livrets : semantique cible

### Interpretation de la vision

Les conteneurs montent jusqu au plan superieur de conception, c est-a-dire le
dessous du couvercle moins le jeu superieur. Un plateau ou livret est ensuite
encastre depuis le dessus : son empreinte retire son epaisseur dans chaque
conteneur intersecte. Hors de cette empreinte, les conteneurs restent a pleine
hauteur.

Le plateau affleure donc le sommet des zones hautes et peut servir de surface de
fermeture locale, sans introduire un contrat de couvercle.

### Geometrie abstraite requise

Pour chaque element plat :

- dimensions repliees X/Y ;
- epaisseur totale ;
- orientation XY autorisee ;
- position XY resolue ;
- niveau dans la pile ;
- profondeur d encastrement ;
- jeu lateral et vertical ;
- zone de prise ;
- ensemble des conteneurs intersectes.

Le moteur produit une `top_inset_reservation` non imprimable. La CAD IR produit
ensuite une operation de retrait par intersection sur chaque conteneur concerne.
Le retrait n est pas une cavite d asset et ne change pas les logements internes.

### Plusieurs plateaux et livrets

Les elements plats peuvent :

- partager la meme empreinte et former une pile ;
- avoir des empreintes differentes ;
- se chevaucher partiellement ;
- etre places cote a cote ;
- imposer un ordre de retrait.

L ordre est automatique quand une seule solution est evidente. Une interaction
explicite est demandee uniquement en cas d ambiguite.

### Aide de prise

Une zone de prise est obligatoire ou explicitement refusee par l utilisateur.
Elle peut etre :

- une encoche sur un bord accessible ;
- deux prises opposees ;
- une zone de debord ;
- une reservation locale dans un conteneur adjacent.

La forme ergonomique finale appartient a V0.2, mais V0.1 doit au minimum
reserver une zone rectangulaire de prise et la montrer dans l Apercu.

### Alternatives challengees

1. Pile globale actuelle : simple, mais retire inutilement la hauteur partout.
2. Couper les bacs apres le solveur : rapide, mais peut percer une cavite ou une
   paroi sans recalcul.
3. Reservation superieure couplee au solveur : plus couteuse, mais seule option
   coherente avec la vision.

Recommandation : option 3. ADR-0050 doit etre remplacee, pas simplement etendue.

## Elements du jeu et catalogue

### Presets integres

Le catalogue integre doit etre versionne, local et testable. Pour les cartes :

- format personnalise largeur x hauteur ;
- formats standards nommes ;
- non sleevees / sleevees ;
- epaisseur totale du paquet ou nombre de cartes + epaisseur unitaire ;
- orientation `a plat`, `debout sur grand cote`, `debout sur petit cote`,
  `automatique` ;
- jeu de prise et profondeur maximale.

Les dimensions reelles saisies par l utilisateur restent prioritaires sur un
preset. Un preset ne doit jamais cacher les valeurs finales resolues.

### Presets personnels

Les presets personnels sont stockes hors du depot et hors du package remplace
lors des mises a jour. Ils sont :

- nommes ;
- exportables/importables ;
- copiables dans un projet ;
- versionnes ;
- sans compte ni cloud pour le MVP.

### Orientation

L orientation est une intention de stockage, pas une simple rotation de rendu.
Elle modifie l enveloppe de cavite, le nombre de piles, l accessibilite et la
hauteur. Elle doit etre resolue dans le coeur avant le placement des conteneurs.

### Formes de cavite futures

Le resume compact prepare un emplacement `Prise et forme`, mais les controles
de fonds arrondis, pentes, encoches courbes et rayons ne deviennent actifs qu en
V0.2 quand leur impact volumique et CAD est reel.

## Conteneurs et corps explicites

L ecran Conteneurs devient le lieu unique des corps qui occupent la boite :

- conteneur avec cavites ;
- conteneur vide ;
- cale pleine ;
- separateur.

Chaque carte montre :

- contenus lies avec liens vers Elements ;
- taille minimale ;
- taille cible/fixe ;
- taille calculee de la proposition courante ;
- surplus par face ;
- axes autorises ;
- epaisseurs minimales ;
- contribution a l appui des plateaux ;
- statut de l etage Z.

Un bouton `Estimer` lance seulement les derives rapides et un packing borne. Il
ne materialise rien.

### Cales et separateurs recommandes

Le moteur peut recommander une cale ou un separateur si :

- un surplus produirait une paroi anormalement epaisse ;
- une zone d appui manque ;
- une region residuelle est difficile a repartir ;
- l ajout reduit la matiere ou simplifie l impression.

Il ne l ajoute jamais sans confirmation. La suggestion montre dimensions,
raison, matiere estimee et effet sur les autres conteneurs.

## Reglages et tolerances

Reglages regroupe :

- jeu contre la boite ;
- jeu total entre conteneurs ;
- jeu element/cavite par defaut ;
- jeu superieur ;
- paroi minimale ;
- fond minimal ;
- profil d impression ;
- priorite du solveur ;
- avertissements de calibration.

La valeur 0,1 mm ne doit pas devenir le defaut general sans impression de
calibration. Elle est probablement trop faible comme jeu total entre deux
corps FDM. Le projet distingue deja 0,8 mm contre la boite, 0,6 mm entre modules
et des jeux par type d asset. Ces valeurs restent experimentales.

Recommandation : clarifier `par cote` contre `jeu total`, conserver des defaults
prudents jusqu aux coupons et permettre une surcharge projet. Toute modification
des defaults reste une gate humaine du modele de tolerance.

## Apercu cible

Le premier niveau montre uniquement :

- proposition construite / partielle / impossible ;
- vue dessus et coupe(s) utiles ;
- conteneurs, cavites et reservations superieures ;
- etages Z ;
- alertes et corrections ;
- `Materialiser dans Fusion` comme action primaire ;
- `Exporter les imprimables` apres scene synchronisee.

Sont masques par defaut : digest, P57, codes enum, statut Python, identifiants
techniques et rapport registry.

Traductions recommandees :

| Actuel | Cible |
| --- | --- |
| `supported_by_requested_bodies` | `Plateaux appuyes par les conteneurs` |
| `Pile et supports` | `Appui des plateaux et livrets` |
| `Plan <digest>` | masque, detail technique |
| `sorties calculees par le moteur Python` | supprime |
| `Score de simplicite` | `Qualite de la proposition` + sous-criteres |

## Solveur volumetrique cible

### Limite P57 confirmee

P57 :

- construit des rangees XY ;
- place tous les corps a Z = 0 ;
- impose `world_size.z = storage_height` ;
- exige que chaque rangee absorbe exactement largeur et profondeur ;
- echoue si un axe non extensible laisse un surplus sans autre absorbeur ;
- ne cherche aucun etage Z ;
- ne compare pas matiere ou epaisseur maximale de paroi.

Le message actuel conseillant d agrandir la boite est donc souvent faux pour un
cas qui necessite seulement plusieurs etages.

### Pipeline recommande

1. normaliser boite, elements, orientations et contraintes ;
2. deriver plusieurs cavites candidates par element ;
3. deriver les enveloppes minimales des conteneurs ;
4. resoudre les reservations superieures et leurs zones d appui ;
5. enumerer des arrangements XY par etage ;
6. empiler des etages compatibles en Z avec support et ordre de retrait ;
7. repartir le surplus proportionnellement entre axes autorises ;
8. borner les epaisseurs desirables de paroi/fond comme objectifs souples ;
9. classer les volumes residuels sans les transformer en corps ;
10. proposer, si utile, des cales explicites a confirmer ;
11. produire plusieurs variantes avec sous-scores et raisons ;
12. materialiser seulement la variante choisie.

### Repartition proportionnelle du surplus

Le partage egal actuel entre corps extensibles ne tient pas compte de leur
taille minimale. La cible par defaut est un partage pondere :

- poids de base proportionnel a l empreinte ou au volume minimal ;
- penalite croissante quand une paroi depasse une epaisseur desirable ;
- respect des cibles/fixes utilisateur ;
- alignement des faces utile aux plateaux ;
- option `equilibre`, `compact`, `accessible`, `matiere reduite`.

Le resultat doit montrer minimum, cible, calcule et raison de l ecart.

### Solutions partielles

Une absence de fermeture exacte ne doit plus effacer toute proposition. Le
moteur peut retourner :

- `complete` : pret a materialiser ;
- `proposal_with_residuals` : visible, non materialisable par defaut, avec zones
  libres et suggestions ;
- `impossible` : contenu ou contraintes physiquement incompatibles.

Le plan partiel ne doit jamais etre presente comme termine.

### Strategie algorithmique

Options challengees :

1. etendre encore le shelf solver 2D : dette rapide et cas Z toujours fragiles ;
2. construire un solveur 3D borne par etages avec heuristiques deterministes ;
3. ajouter immediatement un solveur externe CP-SAT/MIP.

Recommandation : option 2 pour le prochain chemin critique. Elle reutilise les
contrats P8/P19/P20, reste testable sans dependance lourde et permet des bornes
claires. Une ADR separee sera requise avant toute dependance d optimisation.

## Nouveau chemin critique recommande

### P60-R - Realignement documentaire

Le present lot. P60 devient une base technique observee mais une acceptance
produit refusee.

### P61 - Etat reactif et architecture de palette

Diagnostics discrets, etats source/derive/solve/materialise, invalidation
explicable, nouveau parcours, densite compacte/detaillee, suppression du mode
avance global et barre d actions.

### P62 - Catalogue d elements et orientations

Formats de cartes, sleeves, orientations de stockage, presets personnels,
mesures resolues et migration additive.

### P63 - Reservations superieures encastrees

Remplacement de la pile globale P40 par top-inset reservations, positions XY,
ordre de retrait, zones de prise et intersections avec conteneurs.

### P64 - Solveur volumetrique multi-etages

Etages Z, support, ordre de retrait, surplus pondere, cibles/fixes, residuels et
suggestions de cales sans ajout automatique.

### P65 - Conteneurs, reglages et apercu integres

Corps explicites dans Conteneurs, taille calculee, estimation, reglages de jeux,
resultat traduit, sous-scores et actions Fusion coherentes.

### P66 - Acceptance V0.1 revisee

Projet reel couvrant plateaux encastres, plusieurs etages, orientations de
cartes, edition/recalcul, regeneration, export et preservation non-BGIG.

P44-P46 V0.2 puis P47-P50 V0.3 restent apres P66.

## Matrice de sortie V0.1 revisee

| Besoin | Preuve automatique | Preuve Fusion |
| --- | --- | --- |
| Edition source reactive | tests de transitions/digests | ancien apercu marque obsolete |
| Diagnostics non intrusifs | tests payload/DOM | aucun rapport brut au demarrage |
| Catalogue/orientation | tests schema/derivation | valeurs lisibles dans Elements |
| Plateaux encastres | tests intersections/coupes | plateau affleurant, prise visible |
| Multi-etages | collisions/support/retrait | corps a plusieurs Z |
| Surplus pondere | tests minima/cibles/fixes | tailles calculees conformes |
| Corps explicites | zero auto, suggestion sans mutation | cale seulement apres confirmation |
| Apercu explicable | projections et sous-scores | aucune fuite de code moteur |
| Scene sure | plan/CAD/registry | regenerate sans doublon, non-BGIG preserve |

## Decisions recommandees

1. Refuser P60 comme acceptance produit, conserver ses preuves techniques.
2. Remplacer la gate de sortie V0.1 par P66.
3. Accepter la semantique de plateau `top inset` couplee au solveur.
4. Accepter le modele reactif source/derive/solve/materialise.
5. Supprimer le mode avance global au profit de details locaux.
6. Ne pas changer les tolerances par defaut sans calibration physique.
7. Implementer un solveur 3D borne interne avant toute dependance externe.

## Non-objectifs de cette mission

- aucun changement de palette ;
- aucun changement de schema ;
- aucun changement de solveur ;
- aucune geometrie Fusion ;
- aucune valeur de tolerance modifiee ;
- aucune qualification d impression.
