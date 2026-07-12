# UX Product Vision

## Principe

La future UX guide un utilisateur de la boite reelle vers un layout choisi, puis vers l'export. Elle masque les details CAD par defaut et revele les controles experts dans un panneau contextuel. Les rapports restent auditables mais ne sont plus l'interface principale.

## Ecran 1 - Box setup

Dimensions internes, hauteur utile, marge couvercle, orientation et unites. L'utilisateur peut partir d'un preset de jeu/import; la vue montre immediatement le volume utile et les reservations deja declarees.

## Ecran 2 - Assets inventory

Liste visuelle d'assets avec type (cards, tokens, dice, meeples, boards, rulebook, trays), quantite, dimensions, confiance de mesure, groupe/couleur et priorite d'acces. `Add asset`, duplication et presets reduisent la saisie; les fields texte restent un mode expert/import seulement.

## Ecran 3 - Storage intentions

L'utilisateur exprime ce qui doit etre rapidement visible, les modules separables, les assets a garder ensemble, le rangement vertical/horizontal, les reservations boards/livrets et l'ordre de retrait. Ces intentions sont des contraintes lisibles, pas des parametres Fusion.

## Ecran 4 - Generate layouts

`Generate proposals` retourne 3 a 5 variantes deterministes, chacune avec une vue de boite complete et des scores de compacite, accessibilite, imprimabilite, nombre de modules, temps d'impression estime et simplicite. Chaque score doit expliquer ses contributions et ses warnings.

## Ecran 5 - Layout editor

Vue complete de la boite, modules selectionnables, zones libres et reservations visibles. Un clic ouvre les proprietes; l'utilisateur peut deplacer, verrouiller/deverrouiller, changer une intention et demander une regeneration locale. Les collisions, retraits impossibles et volumes non assignes restent visibles avant export.

## Ecran 6 - Export and preprint

Checklist de proposition choisie, blockers printability, fichiers STL V0, manifestes, protocole de calibration et statut `print_validated`. 3MF est futur; aucune UI ne doit declarer une impression garantie sans validation physique.

## Surfaces d'implementation

| Surface | Role | Limite |
| --- | --- | --- |
| Commande Fusion classique | Smoke tests, dev, compatibilite et actions CAD | Pas une UX finale |
| Palette Fusion persistante | MVP interactif dans Fusion, edition et feedback de scene | A gated before implementation |
| App locale/web | UX premium, inventaire, variantes et edition de layout | Peut devenir UI principale a moyen terme |
| Moteur Python | Validation, contraintes, variantes et plans reproductibles | Aucun `adsk`, aucune logique d'affichage |

## Regles UX

- Le novice voit d'abord boite, assets, intentions et propositions.
- Les dimensions, tolerances, grille et profils restent accessibles, jamais imposes comme vocabulaire primaire.
- Toute proposition explique ce qu'elle contient, ce qu'elle reserve, ce qui reste libre et pourquoi elle gagne/perd.
- Toute action destructive ou exportable preserve le registry BGIG et les objets utilisateur.

## Cible proposee apres revue P60

La surface MVP reste exclusivement la palette Fusion. Le parcours recommande
est Boite, Plateaux et livrets, Elements du jeu, Conteneurs, Reglages, Apercu.
Le mode avance global disparait au profit de details locaux, de listes Compact/
Detaille et d aides contextuelles.

Un inspect sain est silencieux. Un diagnostic technique est tronque dans un
tiroir `Voir plus`, jamais affiche comme message principal. Une edition garde
les sources modifiables, recalcule les derives et marque l ancien plan obsolete
sans regenerer Fusion. Les codes moteur, digests et milestones restent hors du
premier niveau. Cette cible depend d ADR-0056 et ADR-0060.
