# P44-M008 - Contrat propose de jeux hérités et overrides par objet

## Statut

Contrat documentaire accepté le 2026-07-16 : Thomas accepte l’option B (trois
rôles, héritage par axe et vecteurs additifs). P44-M009 est autorisée ; aucun
default n’est recalibré.

## But et roles

Chaque asset, plateau, livret et conteneur doit partir d un jeu physique
pertinent, puis pouvoir surcharger seulement X, Y ou Z. Trois roles restent
distincts :

| Role | Objet | Contact | Sémantique a preserver |
| --- | --- | --- | --- |
| Asset-cavité | contents | Objet range dans sa cavité | X/Y par côté, Z au-dessus |
| Plat-encastrement | flat_items | Plateau ou livret dans un logement haut | X/Y par côté, Z sous le plat |
| Conteneur externe | container_groups | Corps entre eux et contre la boîte | Boite X/Y par côté ; voisins X/Y/Z total |

Une reservation superieure n est ni un asset, ni une cavité, ni un corps
imprimable. Les trois jeux ne sont jamais additionnes entre eux.

## Cascade et provenance

Pour un role R, un objet O et un axe A :

~~~
effective(R, O, A) = override(R, O, A) si present, y compris 0
                      default(R, A)      sinon
~~~

Champ absent ou null signifie Hérite du projet. Zero est explicite et ne
signifie jamais héritage. Chaque valeur resolue publie valeur, source, role,
axe et semantique. Sources permises : project_default, object_override et
legacy_scalar.

La palette peut rester compacte avec un choix unique Hérite / Personnaliser,
mais le detail doit permettre le X/Y/Z utile et afficher la source effective.

## Formules proposées

### Asset-cavité

Pour un asset resolu A = (ax, ay, az), une pile de hauteur H et C = (cx, cy, cz) :

~~~
cavity_x = ax + 2 * cx
cavity_y = ay + 2 * cy
cavity_z = H + cz
~~~

X/Y sont par côté. Z est un jeu unidirectionnel au-dessus de l asset ou de sa
pile. Entre piles, le pas interne ajoute le jeu de l axe une seule fois. Cette
formule conserve le scalaire historique content_clearance_mm.

### Plat-encastrement

Pour un plat oriente F = (fx, fy, fz) de quantite Q et I = (ix, iy, iz) :

~~~
cut_x = fx + 2 * ix
cut_y = fy + 2 * iy
local_depth = Q * fz + iz
~~~

X/Y sont par côté. Z est sous le plat, entre le plat et son support. Pour des
empreintes superposees, la profondeur est la profondeur propre plus la
profondeur maximale des elements au-dessus qui recouvrent cette empreinte.
Deux plats côté a côté ne s additionnent pas en Z.

box.lid_clearance_mm reste une marge de fermeture distincte. Elle ne devient
ni un jeu d encastrement ni une seconde addition a iz.

### Conteneurs externes

Les interfaces boîte et voisin sont differentes :

~~~
marge contre boîte X/Y = jeu boîte du conteneur, par côté
gap entre deux conteneurs X/Y = max(jeu voisin gauche, jeu voisin droit), total
gap entre deux etages Z = max(jeu voisin bas, jeu voisin haut), total
~~~

La regle max respecte la demande la plus contraignante sans doubler un jeu deja
historique comme total. Si les deux objets heritent, le resultat est identique
au projet actuel. Le fond de boîte reste a zéro hors epaisseur propre et le jeu
sous couvercle reste séparé.

## Schéma additif accepté pour P44-M009

P44-M008 reste documentaire ; P44-M009 implémente ces champs de manière additive.

~~~
layout.clearance_defaults_v1:
  asset_cavity_mm: {x, y, z}
  flat_inset_mm: {x, y, z}
  container_between_mm: {x, y, z}
  container_box_per_side_xy_mm: {x, y}

contents[].clearance_override_mm: {x: null, y: null, z: null}
flat_items[].clearance_override_mm: {x: null, y: null, z: null}
container_groups[].clearance_overrides_v1:
  between_mm: {x: null, y: null, z: null}
  box_per_side_xy_mm: {x: null, y: null}
~~~

Deux sous-vecteurs de conteneur sont indispensables : un jeu contre boîte est
par côté, un jeu entre corps est total. L UI peut les regrouper sous un seul
bloc Jeu externe ; elle ne doit pas les fusionner dans une valeur ambigue.

## Projection historique et migration

1. Les scalaires existants restent acceptes sans reecriture.
2. Sans nouveau bloc, le normaliseur derive les valeurs effectives et les
   marque legacy_scalar.
3. Le scalaire asset historique se projette sur X/Y/Z pour reproduire les
   formules actuelles ; null reste herite.
4. Le plat historique derive X/Y de layout_clearance_mm et Z de zéro.
5. Le conteneur historique derive son voisinage X/Y de layout_clearance_mm, son
   voisinage Z de container_z_clearance_mm et son perimetre de
   container_box_xy_clearance_mm.
6. Une serialisation ne migre jamais silencieusement un projet ancien.
7. Aucun solveur, CAD IR, materialisation Fusion ou geometrie ne change avant
   P44-M009.

Les valeurs numériques historiques sont conservees par projection ; elles ne
sont pas recalculees ni presentees comme imprimees-validees.

## Matrice de tests obligatoire pour P44-M009

| Cas | Attendu |
| --- | --- |
| Ancien projet sans bloc | Resultat identique, source legacy_scalar |
| Asset herite | X/Y/Z issus du role asset-cavité |
| Asset X seulement | X change ; Y/Z heritent |
| Asset Z a zéro | Zero conserve |
| Roundtrip nouveau et import ancien | Champs et sources stables |
| Plat herite | X/Y historiques, Z zéro |
| Plat Z specifique | Profondeur locale sans toucher au couvercle |
| Plats superposes / côté a côté | Addition seulement si recouvrement |
| Deux conteneurs hérités | Ecarts P65 inchangés |
| Deux overrides conteneur | Max, jamais somme |
| Conteneur contre boîte | Perimetre par côté distinct du voisin total |
| Bridge et materialisation historique | Aucune regression ni recalcul Fusion |

Inclure aussi validation des nombres non negatifs, absence versus zéro, defaults
partiels invalides, source effective dans rapports et palette, charge 50/72/25
et frontiere core sans adsk.

## Gate humaine P44-M008 - clôturée le 2026-07-16

Décision rendue : Thomas a accepté les points suivants :
1. les trois roles ;
2. les trois formules ;
3. max pour une paire de conteneurs ;
4. les sémantiques par côté, total et unidirectionnelle ;
5. la projection historique, notamment plat Z a zéro ;
6. le schema externe a deux sous-vecteurs.

P44-M009 est implémentée ; P44-M007 devient ready-for-explicit-go. P44-V reste bloquée par les missions P44 restantes. print-validated: false.

## Correction UI P44-M009H01

La palette 0.1.32 applique une règle d’édition plus simple que le schéma
interne : chaque objet affiche ses jeux dans un volet replié par défaut et
propose un seul champ X/Y, puis un champ Z lorsque ce rôle possède une
composante verticale.

Une saisie X/Y écrit la même valeur dans les axes x et y. Effacer ce champ
rétablit l’héritage sur les deux axes. Le schéma X/Y/Z reste inchangé pour la
rétrocompatibilité. Un projet importé dont X et Y diffèrent conserve ses deux
valeurs tant que l’utilisateur ne saisit pas un nouveau X/Y commun ; la palette
affiche alors une note explicite.

Cette correction ne change ni les valeurs par défaut, ni les formules, ni la
règle max entre voisins, ni le solveur, ni la CAD IR, ni la géométrie.
