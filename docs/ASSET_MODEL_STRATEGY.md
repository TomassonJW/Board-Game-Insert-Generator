# Asset Model Strategy

## Objectif

Le produit cible est asset-first : l'utilisateur doit pouvoir decrire le materiel
reel a ranger avant ou a la place de modules manuels. Le moteur pourra ensuite
proposer des modules, cavites et reservations.

## Etat actuel

- Le JSON V0 accepte maintenant `assets` comme donnees passives chargees et validees.
- `functional_type` distingue cartes, cartes sleevees, tokens, meeples, des,
  free et other cote modules/cavites.
- Les cavites peuvent representer des receptacles simples.
- Les assets P9-M002 sont reportes et transportes en CAD IR metadata, sans deriver de module.
- P10-M004 produit une synthese `module_candidates` deterministe depuis les assets, sans muter `modules`.
- P10-M008 produit un `executable_asset_plan` abstrait depuis la variante recommandee et le place dans la grille 3D si elle existe.

## Concepts cibles

- `Asset` : element ou groupe a ranger, avec dimensions exactes ou approximees.
- `AssetQuantity` : quantite, pile, deck, sac, set ou groupe.
- `ContainmentIntent` : ranger, caler, separer, rendre accessible, exposer.
- `ReservationAsset` : board, livret, regle, plateau ou composant non imprime.
- `DerivedModuleRequest` : module propose depuis des assets, distinct d'un module manuel.

## Invariants

- Un asset n'est pas un module imprimable.
- Un module est une proposition de contenant ou de support pour un ou plusieurs assets.
- Les dimensions approximatives doivent rester signalees dans les rapports.
- Les assets ne doivent pas introduire de dependance SaaS ou IA obligatoire.

## Prochaines missions possibles

1. `P9-M001 - Specifier le schema asset-first` : docs + exemples non executes.
2. `P9-M002 - Charger des assets JSON sans generation de modules` : moteur pur.
3. `P9-M003 - Generer des demandes de cavites depuis assets simples` : gate si schema public change.

## Gates

- Gate architecture si le schema JSON public devient incompatible.
- Gate ergonomique humaine avant de declarer les assets faciles pour non-experts.

## Contrat cible P9-M001

P9-M001 specifie le schema asset-first cible. P9-M002 active son chargement strict dans le loader V0 sans generation de modules. Le
bloc futur `assets` restera distinct de `modules` : il decrit le materiel reel,
pas un corps imprimable ni une demande de module.

Champs cibles d'un asset :

- `id` : identifiant stable ;
- `name` : nom humain ;
- `kind` : `cards`, `sleeved_cards`, `tokens`, `dice`, `meeples`, `board`,
  `rulebook`, `tray`, `miniature`, `other` ;
- `quantity.count` et `quantity.grouping` : quantite et mode de groupe ;
- `dimensions_mm.x/y/z` : dimensions mesurees ou estimees ;
- `dimension_confidence` : `exact`, `approximate` ou `unknown_z` ;
- `containment_intent` : `store`, `separate`, `protect`, `display`, `reserve`,
  `access_first` ;
- `reservation_ref` : id de reservation volumetrique optionnel ;
- `module_hint` : indication optionnelle vers un module manuel ou futur module derive ;
- `comment` : note humaine.

Les reservations plates comme boards, livrets et regles doivent d'abord pointer
vers `volumetric_grid.zones[]`, puis pourront etre reliees par `reservation_ref`.
Cela evite de transformer trop tot un asset en module imprimable.

Exemple non executable P9-M001 :

```json
{
  "assets": [
    {
      "id": "main-board",
      "name": "Main folded board",
      "kind": "board",
      "quantity": { "count": 1, "grouping": "single" },
      "dimensions_mm": { "x": 280, "y": 210, "z": 8 },
      "dimension_confidence": "approximate",
      "containment_intent": "reserve",
      "reservation_ref": "board-and-rules-reservation",
      "comment": "Target schema only; loader support starts in P9-M002."
    }
  ]
}
```

## Regles P9-M001

- Un asset n'est pas imprime directement.
- Un asset peut etre reserve, contenu par une cavite ou suggerer un module futur.
- Une dimension approximative doit rester visible dans les rapports futurs.
- Le loader V0 accepte `assets` a la racine depuis P9-M002, mais ne derive encore
  aucun module, layout ou cavity depuis ces assets.

## Synthese module candidates P10-M004

P10-M004 ajoute une sortie derivee et non executable : `module_candidates`.

Un candidat de module est une proposition explicable issue d'un asset charge :

- `status: candidate_only` pour un contenant imprimable possible ;
- `status: reservation_only` pour un board, rulebook, tray ou asset avec intention `reserve` ;
- `status: blocked` si une dimension critique, notamment Z, ne permet pas une
  hauteur de candidat fiable.

Les dimensions proposees additionnent l'enveloppe asset, le clearance du profil
actif et les defaults de paroi/plancher. Elles restent indicatives : elles ne
creent pas de `ModuleRequest`, ne modifient pas le layout, ne creent pas de
cavite et ne declenchent aucune generation Fusion.

Depuis P10-M005, une variante `asset-candidates:row_fill` peut recommander un
agencement simple de ces candidats. Cette recommandation reste report-only et ne
remplace pas les modules manuels.


## Grouping deterministe P10-M006

P10-M006 groupe uniquement des assets compatibles quand ils partagent `kind`,
`containment_intent` et `dimension_confidence`, sans `reservation_ref` ni
`module_hint`.

Le candidat groupe utilise la plus grande enveloppe source et la quantite totale
des assets. Ce grouping reste reversible et report-only : il ne fusionne pas les
assets sources, ne cree pas de module manuel et ne lance aucun placement complexe.


## Exemple de rejet P10-M007

`examples/simple_asset_rejected_variant.json` documente le cas ou un asset produit
un candidat trop grand. Le layout manuel existant reste valide, mais la variante
asset-candidate est rejetee avec raison structuree et sans variante recommandee.

## Plan concret asset-first P10-M008

Depuis P10-M008, un asset candidat peut devenir un module genere abstrait dans
`executable_asset_plan`. Cette sortie ne modifie pas `modules` et ne cree pas de
geometrie Fusion. Elle relie :

- `generated_modules` : modules derives de candidats, avec `source_asset_ids` ;
- `placements` : positions X/Y/Z en unites de grille, dimensions imprimables du
  module genere et metadata separee de span grille ;
- `rejected_modules` : refus actionnables, par exemple absence de grille ou span
  libre introuvable.

`examples/simple_asset_product_scene.json` montre le flux produit lisible : deux assets tokens groupes puis places comme un seul module abstrait dans une cellule libre, sans module manuel ni blank legacy. `examples/simple_asset_executable_plan.json` reste une fixture technique : elle declare volontairement un module manuel pour occuper une cellule et tester que le placement greedy evite les collisions.

Depuis P11-M003, le plan distingue explicitement les dimensions suivantes pour les
modules asset-first generes :

- `theoretical_grid_origin_mm` et `theoretical_grid_extent_mm` : reservation dans
  la grille discrete X/Y/Z ;
- `asset_fit_size_mm` : enveloppe utile de l'asset avec clearance interne ;
- `printable_body_origin_mm` et `printable_body_size_mm` : corps rectangulaire
  reel que l'adaptateur Fusion doit creer ;
- `size_mm` reste un alias de `printable_body_size_mm` dans les placements du
  plan executable ;
- `grid_slack_mm` rend visible la marge entre span de grille et corps imprimable.

Les exemples `simple_asset_product_scene`, `simple_asset_executable_plan` et `simple_multilayer_grid_scene`
ne doivent donc plus etre lus comme des scenes dont les corps imprimables font
necessairement toute la cellule. Le span `90 x 90 x 10 mm` de la scene
multi-layer reste une occupation de grille ; le body imprimable correspondant est
`61.6 x 61.6 x 7.8 mm`.

## P13-M001 - quick_asset_box UI V0

`quick_asset_box` est un mode de commande Fusion classique, pas une palette persistante. Le champ `Assets (quick_asset_box)` accepte une saisie compacte :

`asset_id,type,count,x_mm,y_mm,z_mm,fit`

Les entrees sont separees par `;` ou par saut de ligne. Les types UI V0 sont `tokens`, `dice`, `meeples`, `cards`, `sleeved_cards`, `generic`; `generic` est mappe vers le kind coeur `other`. Le champ `fit` accepte `exact`, `loose` ou `approximate`; `loose` est transporte comme `dimension_confidence = approximate`.

La commande genere une config temporaire BGIG stricte depuis les champs boite/grille/parois/clearances/profil et `assets[]`, puis reutilise le pipeline existant : assets charges, `module_candidates`, variante recommandee, `executable_asset_plan`, CAD IR et generation Fusion. Les assets invalides sont refuses dans le rapport sans bloquer si au moins un asset valide reste.

Limites : pas de tableau avance, pas de palette HTML, pas de solveur complexe, pas de nouvelle geometrie Fusion, pas de validation d'impression.

## P13-ASSET-M002 - Count-aware storage sizing V0

Pour `tokens`, `dice`, `meeples` et `generic`, le sizing V0 traite chaque asset comme un item rectangulaire `x_mm x y_mm x z_mm`. `count` est maintenant utilise pour calculer une capacite deterministe : capacite par pile selon la hauteur utile, nombre de piles necessaires, empilement uniforme par pile, puis packing XY simple des piles sans backtracking.

La sortie reste une enveloppe de rangement, pas une cavite physique : `declared_capacity_guarantee = heuristic_envelope_only_not_physical_cavity`. Les vrais items Fusion ne sont pas generes et les logements ne sont pas coupes.

Pour `cards` et `sleeved_cards`, `z_mm` reste interprete comme hauteur totale fournie du paquet/deck. `count` est reporte mais non multiplie, avec warning explicite. Cela evite de melanger silencieusement epaisseur unitaire et epaisseur totale.

## P13-ASSET-M003 - Asset-fit cavity V0

Le premier logement asset-first reel reste volontairement simple : pour chaque module asset candidate place, BGIG cree une seule cavite rectangulaire globale issue de l'enveloppe `asset_fit`. La politique est `single_asset_fit_rectangular_cavity_v0`.

Regle V0 : origine locale `wall_thickness_mm x wall_thickness_mm x floor_thickness_mm`, taille `asset_fit_size_mm`, fond conserve egal a `floor_thickness_mm` et murs attendus au moins egaux a `wall_thickness_mm`. Cette cavite n'est pas un solveur de rangement : elle ne cree pas de logements par pile, ne visualise pas les assets individuels et ne garantit pas physiquement la capacite declaree.

Types supportes pour la cavite V0 : `tokens`, `dice`, `meeples`, `generic`. Les cartes et cartes sleevees gardent une semantique de paquet total et refusent la cavite asset-fit M003 tant qu'un logement carte dedie n'est pas specifie.

## P13-ASSET-M004 - Compartiments par asset source

Le flux `quick_asset_box` peut maintenant transformer un module count-aware en compartiments rectangulaires top-open par asset source. La policy active est `per_source_asset_rectangular_compartments_v0`.

Chaque compartiment reste une approximation V0 : il represente l'enveloppe de stockage de l'asset source, pas les items individuels ni les piles detaillees. Le payload reporte l'asset id, les dimensions lues, le count, la capacite heuristique, l'origine locale, la taille de cavite, le fond conserve et les murs attendus.

## P13-ASSET-M005 - Encoche d'acces par compartiment V0

P13-ASSET-M005 ajoute une premiere ergonomie d'acces pour les compartiments asset-specific. La policy est `per_compartment_top_open_rectangular_notch_v0`.

Regle V0 : au plus une encoche rectangulaire top-open par compartiment, sur le mur avant du module (`-Y`), centree dans la largeur utile du compartiment. Le moteur planifie l'encoche uniquement si le compartiment touche le mur avant externe, si la largeur restante apres marges laterales atteint 6.0 mm et si la profondeur verticale utile atteint 4.0 mm. La cible nominale est 18.0 mm de largeur et 10.0 mm de profondeur depuis le haut, bornee par la taille du compartiment.

Si un compartiment n'est pas adjacent au mur avant, est trop etroit ou trop bas, l'encoche est refusee avec `status: refused` et une raison explicite. Les assets individuels, cavites par pile/item, courbes, scoops, fillets et garanties d'impression restent hors scope.

## P14-USABLE-ASSET-TRAY-M001 - Layout multi-assets robuste V0

Le layout de compartiments `per_source_asset_rectangular_compartments_v0` supporte maintenant plusieurs assets compatibles dans un module asset-first unique avec trois strategies deterministes bornees : ligne, colonne, puis shelf multi-rang. Le shelf layout garde l'ordre source des assets, ajoute des parois internes entre compartiments voisins, reporte les roles de murs internes et choisit la plus petite enveloppe XY qui tient dans la boite.

Si aucun layout ne tient dans `box.inner_dimensions_mm` apres murs externes, le moteur refuse explicitement avec `ASSET_COMPARTMENTS_DO_NOT_FIT` et `layout_attempts`. BGIG ne retombe plus silencieusement vers une cavite globale quand les compartiments asset-specific sont requis mais impossibles.

## P14-USABLE-ASSET-TRAY-M002 - Printability report V0

Les modules asset-first generes portent maintenant `printability_report_v0`. Ce rapport inspecte les dimensions moteur deja calculees pour les murs, parois internes, fond, cavites et encoches. Il est strictement informatif : `printability_checked: yes` signifie que les seuils geometriques ont ete reportes, tandis que `printability_validated_by_print: no` reste obligatoire tant qu'aucun prototype physique n'est imprime et mesure.

## P16-M001 - Strategie flat_tray_2d V0

P16 formalise la dette ouverte par P15 : `flat_tray` ne doit pas seulement eviter les tours hautes, il doit aussi eviter les longues barres X quand une organisation 2D raisonnable est possible.

Terminologie retenue :

- `flat_tray_linear_v0` : comportement P15, piles basses mais souvent en ligne unique ;
- `flat_tray_2d_v0` : nouvelle cible, piles basses reparties en colonnes/rangees ;
- `items_per_pile` : capacite verticale d'une pile selon `max_stack_height_mm` ;
- `pile_count` : nombre de piles requises par `count` ;
- `pile_grid_columns` / `pile_grid_rows` : grille locale de piles dans l'enveloppe asset-fit ;
- `target_aspect_ratio` : ratio cible pour eviter les modules trop longs ;
- `max_module_length_mm` : limite souple de longueur module ;
- `max_stack_height_mm` : plafond de hauteur de pile deja expose par P15.

Pour `tokens`, `dice`, `meeples` et `generic`, le defaut cible est `flat_tray_2d_v0`. Les cartes gardent leur semantique de deck/paquet total. Les cavites restent des enveloppes rectangulaires par asset source, pas des logements individuels par pile ou item.

## P16-M002 - Packing 2D moteur

Le moteur implemente maintenant `flat_tray_2d_v0` pour les assets simples en orientation `flat_tray`. La grille locale de piles est calculee apres la capacite verticale : `items_per_pile`, `pile_count`, puis `pile_grid_columns` et `pile_grid_rows`.

Les diagnostics `storage_sizing`, asset et compartiment transportent `tray_packing_policy`, `target_aspect_ratio`, `max_module_length_mm`, `linear_layout_avoided` et les dimensions de footprint. Les cavites restent rectangulaires par source asset et suivent l'enveloppe 2D resultante ; aucune cavite par item ou pile n'est creee.

## P17 - Export/preprint boundary

P17 ne change pas le modele asset-first : les assets, piles, compartiments, encoches et rapports `storage_sizing` restent produits par le coeur Python pur. Le sprint ajoute une boucle export/preprint cote adaptateur Fusion : export STL des `module_body` BGIG, manifeste JSON/Markdown et protocole preprint.

Frontiere maintenue : le coeur `src/board_game_insert_generator` ne produit pas de STL/3MF, n'importe pas `adsk` et ne pretend pas valider l'impression physique. Les champs `printability_report_v0`, `printability_export_allowed` et `printability_validated_by_print: no` servent a documenter l'export technique et les risques avant une future validation mesuree.