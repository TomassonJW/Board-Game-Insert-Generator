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
- `placements` : positions X/Y/Z en unites de grille et dimensions millimetres
  couvertes par la grille ;
- `rejected_modules` : refus actionnables, par exemple absence de grille ou span
  libre introuvable.

`examples/simple_asset_executable_plan.json` montre deux assets tokens groupes
puis places comme un module abstrait dans une cellule libre de la grille.
