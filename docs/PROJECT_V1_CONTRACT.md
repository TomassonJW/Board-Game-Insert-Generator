# Contrat projet V0.1

## Role

`bgig.project.v1` est le contrat de projet utilisateur de BGIG V0.1. Il decrit
une boite, ce qu'elle contient, les bacs que les pieces doivent partager, les
plateaux/livrets poses au-dessus et les volumes de remplissage demandes.

Il ne contient volontairement ni `candidate`, ni `layer`, ni policy de solveur,
ni CAD IR, ni operation Fusion. Ces objets restent des resultats techniques
derives par P39 a P42.

## Racine

```json
{
  "schema_version": "bgig.project.v1",
  "project_name": "Mon insert",
  "box": {},
  "layout": {},
  "contents": [],
  "container_groups": [],
  "flat_items": [],
  "fill_elements": [],
  "solver_preference": "balanced",
  "deferred_features": {"appearance": null, "mechanism": null}
}
```

Les champs inconnus sont refuses. Les dimensions sont toujours en millimetres.
Le schema ne limite pas le nombre de lignes de contenu, de bacs ou d'elements
plats : les limites de calcul seront gerees par P41, pas par une limite arbitraire
du contrat.

## Boite et reglages communs

`box` contient les dimensions interieures, la hauteur exploitable et la marge
sous couvercle. `layout` contient quatre valeurs explicites :

- `layout_clearance_mm` : jeu minimal entre volumes imprimes et contre la boite ;
- `default_wall_thickness_mm` : paroi par defaut ;
- `default_floor_thickness_mm` : fond par defaut ;
- `default_content_clearance_mm` : jeu par defaut autour des pieces.

Le jeu de layout et le jeu autour des pieces ne sont pas confondus. Chaque ligne
de contenu peut surcharger `content_clearance_mm`, et chaque bac peut surcharger
sa paroi ou son fond.

## Pieces et bacs partages

`contents[]` contient une ligne par famille de pieces :

| Champ | Signification |
| --- | --- |
| `shape_kind` | `round`, `square`, `rectangle`, `cards`, `cube`, `meeple` ou `custom` |
| `dimensions_mm` | Enveloppe X/Y/Z normalisee par l'interface |
| `quantity` | Nombre d'exemplaires a ranger |
| `container_group_id` | Le bac choisi par l'utilisateur |
| `content_clearance_mm` | Jeu specifique, ou `null` pour le defaut |

`container_groups[]` porte les bacs eux-memes. Il n'a pas de taille externe :
cette taille sera derivee des pieces et des reglages lors de P39. Deux lignes
ayant le meme `container_group_id` doivent finir dans le meme corps imprimable.

### Cartes et sleeves

Une ligne `shape_kind: cards` peut utiliser les champs suivants :

| Champ | Signification |
| --- | --- |
| `card_format_id` | Format du catalogue, ou `null` pour des dimensions explicites |
| `card_stack_mode` | `thickness` pour une épaisseur totale ou `count` pour épaisseur de carte × quantité |
| `card_stack_declared_thickness_mm` | Z du paquet saisi avant ajout sleeves, additif et utile au mode `thickness` |
| `card_thickness_mm` | Épaisseur d’une carte, active pour `count` |
| `sleeved` | Active la résolution avec sleeves ; `false` par défaut dans le preset `Cartes` |
| `sleeve_extra_xy_mm` | Delta total optionnel, identique sur X et Y |
| `sleeve_extra_z_mm_per_card` | Delta Z optionnel ajouté à chaque carte dans les deux modes |

Les deltas et le Z déclaré doivent être finis ; les deltas sont supérieurs ou
égaux à zéro et le Z déclaré est strictement positif. Leur absence conserve le
comportement catalogue historique : le normaliseur ne les injecte pas dans un
ancien projet et ne recalcule pas implicitement ses dimensions.

Dans la nouvelle UI, activer les sleeves initialise les valeurs communes
éditables à 3,0 mm sur X/Y et 0,19 mm par carte sur Z. En mode `thickness`, le
nombre estimé est `max(1, floor(declared_Z / 0.31 + 0.5))` et le Z résolu vaut
`declared_Z + estimated_count × sleeve_extra_z_mm_per_card`. Le champ déclaré
reste stable au roundtrip afin de ne jamais cumuler la surépaisseur.

En mode `count`, Z vaut
`quantity × (card_thickness_mm + sleeve_extra_z_mm_per_card)`. Décocher les
sleeves exclut les deltas du résultat. Les valeurs de départ 3,0, 0,19 et 0,31 mm
ne sont ni fusion-validated physiquement ni print-validated.

## Plateaux et livrets

`flat_items[]` represente les elements plats a reserver au-dessus des bacs :

- `kind` : `board`, `rulebook` ou `other` ;
- `dimensions_mm.z` : epaisseur d'un exemplaire ;
- `quantity` : nombre d'exemplaires ;
- `stack_order` : ordre explicite optionnel, sinon ordre automatique futur.

P40 transformera ces lignes en pile superieure, support et reservations X/Y/Z.

## Volumes complementaires

`fill_elements[]` represente les volumes non lies a une famille de pieces :

- `hollow` : bac vide ;
- `solid` : remplissage plein ;
- `separator` : cloison ou volume de structuration.

Le `mode` vaut `auto` pour laisser P41 choisir les dimensions, ou `exact` avec
`dimensions_mm` pour demander un volume precis. Un element peut etre associe a
un bac existant ou rester global a la boite.

## Apparence et mecanismes reportes

`deferred_features.appearance` et `deferred_features.mechanism` conservent les
anciens choix P33/P34 sans les rendre actifs. Ils sont hors du parcours V0.1 et
ne changent ni plan, ni dimensions, ni CAD IR.

## Migration depuis le Studio P23

Le normaliseur accepte encore `bgig.local_composer.v0` :

- chaque ancien candidat devient un `container_group` ;
- les assets associes deviennent des lignes `contents` dans ce groupe ;
- un asset non associe recoit son propre bac, sans etre perdu ;
- les reservations `board` et `rulebook` deviennent des `flat_items` ;
- les anciens layers, reservations, modules manuels et candidats restent dans
  `migration.legacy_snapshot` ;
- apparence et mecanisme deviennent des options differees ;
- l'ancien draft n'est jamais mute.

Les routes locales suivantes sont disponibles pour P38 :

- `GET /api/project-v1/starter` : projet vide valide ;
- `POST /api/project-v1/normalize` : validation V1 ou migration V0 vers V1.

Le portfolio P21 et l'export restent encore sur le contrat P23 pendant P37. P39
les reconnectera au contrat V1 lorsque les dimensions des bacs pourront etre
derivees honnêtement.
