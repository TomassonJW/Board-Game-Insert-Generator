# ADR-0019 - Fusion compact grid placement from CAD IR metadata

Date : 2026-07-06

Statut : accepted for implementation, manual Fusion validation required.

## Contexte

P10-M008 ajoute `metadata.executable_asset_plan` dans la CAD IR : modules generes
abstraits, placements grille X/Y/Z, dimensions millimetres couvertes par la
grille et refus eventuels. La gate humaine suivante autorise une premiere
consommation Fusion de ces placements, sans solveur complexe, sans backtracking,
sans modules composites et sans vue eclatee.

## Decision

L'adaptateur Fusion consomme directement `metadata.executable_asset_plan`.

- Fusion ne lit pas la configuration BGIG source.
- Fusion ne recalcule ni grouping, ni layout, ni clearances, ni tolerances.
- Les modules generes places par grille deviennent des bodies rectangulaires
  simples dans le composant racine, comme les blanks P4-M003.
- `placement.origin_mm` devient l'origine scene du body.
- `placement.size_mm` devient la taille du body cree dans Fusion.
- `origin_units` et `size_units` sont valides contre `metadata.volumetric_grid`
  quand cette metadata est presente.
- Les placements sont refuses hors Fusion si les dimensions manquent, si le span
  sort de la grille, si le body sort de la boite de reference ou si une collision
  manifeste avec un blank deja planifie est detectee.
- Les origines Z non nulles sont executees via un plan XY decale en Z.

## Consequences

La vue compacte Fusion peut maintenant afficher les modules asset-first generes a
leur emplacement X/Y/Z decide par le moteur. La sortie reste `manual validation
required` tant que le smoke test Fusion P11-M001 n'a pas ete realise.

La decision conserve la compatibilite Part Design : pas de composants enfants
Fusion, pas de vue eclatee, pas de modules composites et pas d'export STL/3MF.

## Alternatives refusees

- Recalculer les positions depuis la config BGIG dans Fusion : refuse, car Fusion
  doit rester un adaptateur de sortie.
- Creer des composants enfants pour chaque module : reporte, car le chemin root
  component est le seul valide par les smoke tests Part Design precedents.
- Generer une vue eclatee dans la meme mission : refuse, car elle demande une
  intention CAD IR et une validation separees.
