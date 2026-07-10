# Box Fill Solver Roadmap

## But

Passer de l'heuristique locale actuelle a des `BoxFillPlan` explicables, sans sauter directement vers un optimiseur opaque.

| Etape | Entrees | Sorties | Tests et gate | Risque |
| --- | --- | --- | --- | --- |
| `box_fill_v0_manual_modules` | Box, reservations, modules manuels, positions | collisions, coverage, `FreeVolume`, warnings | unitaires volume/collision + gate produit P19 | modele trop pauvre |
| `box_fill_v1_greedy_2d` | modules V0 et intentions simples | placement XY deterministe par layer | fixtures reproductibles, refus lisibles | ordre greedy mediocre |
| `box_fill_v2_layers_and_reservations` | boards, rules, lid, removal order | layers et contraintes Z valides | tests collision/retrait + gate physique si support revendique | contraintes contradictoires |
| `box_fill_v3_variant_generation` | contraintes et candidats | 3-5 variantes scorees | scores decomposes, determinisme, gate produit | score trompeur |
| `box_fill_v4_interactive_editor` | variante + locks/deplacements | regeneration locale sans deplacer les locks | contrats UI/moteur + gate UX | etat UI complexe |
| `box_fill_v5_full_assistant` | projet, preferences, historique | propositions expliquees et actions assistees | evaluation explicable + gate IA | automatisation opaque |

## Regles de progression

- Chaque etape conserve un moteur Python pur et une CAD IR sans recalcul Fusion.
- Les contraintes sont versionnees, visibles dans les rapports et associees a une raison de refus ou relaxation.
- Les reservations et le retrait passent avant l'optimisation de compacite.
- Une validation Fusion prouve une materialisation, une impression reelle seule prouve la physique.

## Recommandation immediate

Commencer par `box_fill_v0_manual_modules`. Il est le plus petit increment qui rend la boite complete observable, permet un editeur futur et fournit les fixtures necessaires au greedy puis aux variantes. `box_fill_v1+` restent gates tant que le modele et l'UX n'ont pas ete valides humainement.
