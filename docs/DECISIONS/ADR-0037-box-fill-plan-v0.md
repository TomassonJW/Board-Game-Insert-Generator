# ADR-0037 - BoxFillPlan V0 contract

## Statut

Accepted for P19 implementation.

## Date

2026-07-10

## Carte liee

- `P19-M001 - Contrat BoxFillPlan V0`

## Contexte

Le moteur dispose d'assets, de modules requests, d'une grille volumetrique declarative et d'une CAD IR, mais aucun objet ne decrit la composition complete d'une boite comme source de verite. La validation strategique P18 autorise une extension additive, versionnee, CAD-agnostic et retrocompatible pour etablir ce contrat avant tout solveur ou UI persistante.

## Decision

Le bloc optionnel racine `box_fill_plan` adopte le schema `box_fill_plan.v0`. Il est charge dans le moteur pur et ne remplace ni `modules`, ni `volumetric_grid`, ni la CAD IR V0. Lorsqu'il est absent, les configurations et pipelines existants conservent exactement leur comportement.

`BoxFillPlan` est le plan manuel de boite : il porte le volume de boite derive de `box`, les assets existants, les reservations, layers, modules, allocations explicites, volumes libres agreges, couverture, validation, warnings et metadata. Fusion ne produit ni ne recalcule ce plan; un adaptateur futur le materialisera seulement apres gate dediee.

## Contrat V0

### Box volume

Le volume de boite est derive de `box.inner_dimensions_mm` et de `box.usable_height_mm`. Son origine est `(0, 0, 0)`, ses unites sont `mm`, son orientation est `x_right_y_back_z_up`, et la zone de couvercle est representee par `lid_clearance_mm`. Une duplication divergente des dimensions de boite dans `box_fill_plan` est interdite.

### Reservation

Une reservation est un volume non imprimable : `id`, `kind`, `origin_mm`, `size_mm`, `layer_id` optionnel, `removal_order` optionnel, `allow_overlap` explicite, `source`, `comment` et `metadata`. Les kinds V0 sont `board`, `rulebook`, `lid_clearance`, `existing_tray`, `non_printable_volume` et `generic`. `printable` est implicitement et invariablement `false`.

### Layer

Un layer a `id`, `origin_z_mm`, `height_mm`, `role`, `removal_order` optionnel, `support_reservation_ids`, `module_ids`, `comment` et `metadata`. Les liens sont declaratifs : P19 ne deduit ni support physique ni ordre ergonomique reel.

### ModulePlan

Un module manuel a `id`, `name`, `origin_mm`, `size_mm`, `orientation`, `locked`, `manual`, `printable`, `layer_id` optionnel, `source`, `compartment_ids`, `access_feature_ids`, `comment` et `metadata`. Son volume abstrait est la source de verite; un body Fusion est une projection future. Les compartiments et access features reutilisent les contrats `Cavity` et `Feature` existants, indexes par id dans le plan au lieu de creer des types concurrents.

### AssetAllocation et coverage

Chaque allocation a `asset_id`, `quantity`, `module_id`, `compartment_id` optionnel, `source`, `intent` et `coverage_status`. Une apparition d'asset dans un module ne couvre jamais une quantite implicitement. La couverture par asset expose au minimum `declared_quantity`, `allocated_quantity`, `unallocated_quantity`, `over_allocated_quantity` et `status` (`covered`, `partial`, `uncovered`, `over_allocated`).

### FreeVolume

P19 calcule un `FreeVolume` aggregate : volume total de la boite moins modules et reservations. Les regions libres ne sont pas encore solvees; le resultat declare donc `qualification=aggregate_only` et une raison explicite. Cette limitation interdit de presenter l'agregat comme une region printable ou directement utilisable.

## Invariants V0

- IDs uniques dans chaque famille et entre modules/reservations/layers.
- Modules et reservations de dimensions strictement positives, entierement dans le volume utile.
- Modules sans intersection; modules sans intersection avec reservations.
- Reservations sans intersection, sauf paire dont les deux membres portent `allow_overlap=true`.
- Chaque allocation reference un asset et un module existants; son compartment, s'il est renseigne, appartient au module.
- La somme d'allocations d'un asset est comparee explicitement a `Asset.quantity.count`; une sur-allocation est visible dans coverage et la validation.
- Tout volume occupe est attribue a un module ou une reservation; le reste est seulement l'agregat `FreeVolume` P19.
- Fusion, CAD IR et UI ne sont jamais source de verite du plan.

## Consequences

### Positives

- Le moteur peut valider une boite complete sans `adsk`.
- UI, solveur et CAD disposent d'un contrat commun et reproductible.
- Les conflits et couvertures deviennent auditables avant toute geometrie.

### Limites P19

- Aucun placement automatique, score de variante, regions libres exactes, support physique, nouvelle geometrie Fusion ou UI persistante.
- Les `Cavity`/`Feature` sont references, non convertis en bodies ou cuts par ce contrat.

## Alternatives refusees

- Etendre implicitement `volumetric_grid` jusqu'a devenir le plan produit : refuse, car la grille est une lattice discrete historique et ne porte pas les allocations explicites.
- Faire de la CAD IR ou de Fusion la source de verite : refuse, car cela inverserait la frontiere moteur/adaptateur.
- Introduire une palette ou un solveur simultanement : refuse, car ils doivent consommer ce contrat stabilise.

## Suivi

- P19-M002 implemente les dataclasses et le loader additif.
- P19-M003 implemente la validation, coverage et FreeVolume aggregate.
- Toute projection Fusion de `BoxFillPlan` exige une mission et une gate distinctes.