# Vision Gap Analysis

## Objet

Ce document compare la North Star BGIG au produit reel apres P17. Il ne remplace pas la North Star et ne change aucune API, tolerance, geometrie ou decision Fusion. Il fixe le vocabulaire qui doit guider P18 puis la prochaine gate P19.

## Vision d'origine

BGIG doit transformer une boite reelle, ses assets et des intentions de rangement en un systeme complet de modules imprimables dans tout le volume X/Y/Z. Le resultat cible est un ensemble de propositions comparables : elles reservent boards, livrets et couvercle, repartissent les assets dans des modules coherents, expliquent les compromis de compacite/accessibilite/imprimabilite et restent editables avant export CAD.

L'utilisateur ne devrait pas avoir a traduire son jeu en une suite de parametres CAD. Il decrit son jeu et ses priorites; le moteur produit puis explique un plan de rangement.

## Etat reel au 2026-07-10

### Fondation deja solide

- Coeur Python pur, determine et teste hors Fusion; aucun `adsk` dans `src/`.
- Modele asset-first, sizing count-aware V0 et packing local `flat_tray_2d_v0` pour assets simples.
- Modules rectangulaires, compartiments par asset source et encoches top-open V0 valides dans Fusion.
- Grille volumetrique declarative X/Y/Z, layers, reservations, ordre de retrait et supports abstraits transportes dans la CAD IR.
- Registry Fusion, ownership racine, inspect/generate/regenerate/clear sans doublon et preservation des objets non-BGIG valides.
- Export STL Fusion-only par module BGIG et manifestes preprint valides dans Fusion.

### Produit actuellement livre

Le produit courant est un atelier de developpement Fusion pour generer un ou plusieurs bacs asset-first rectangulaires. `quick_asset_box` convertit une saisie compacte en configuration temporaire, puis applique des heuristiques locales et un placement greedy borne. Il est utile pour prouver le pipeline, mais ne constitue pas une experience de conception de rangement complet.

## Ecart par dimension

| Dimension cible | Etat actuel | Ecart a combler |
| --- | --- | --- |
| Box complete | Reference, grille et outlines disponibles | Aucun `BoxFillPlan` ne gouverne le volume entier ni ne rend les volumes libres pilotables |
| Assets | Saisie texte, modele et sizing asset-first V0 | Pas d'inventaire visuel, pas de groupes interactifs, pas de mesure/preset produit facile |
| Modules | Bacs derives locaux et modules rectangulaires | Pas de catalogue de modules, de composition manuelle ni de proprietes par module a l'echelle de la boite |
| Reservations | Contrat declaratif layers/zones/supports | Boards, livrets, couvercle et ordre de retrait ne sont pas des contraintes centrales de generation |
| Layout | Greedy de placement et packing local 2D | Pas de remplissage intelligent, de propagation de contraintes ni de variantes comparables |
| UX | Commande Fusion persistante, settings et rapports | Pas de flux novice, pas de vue box complete, pas d'edition directe, pas de feedback spatial premium |
| CAD/export | Fusion inspectable, registry et STL V0 | Le CAD ne peut pas compenser l'absence d'un plan produit global |
| Validation | Fusion et preprint techniques valides | Impression physique, slicer, materiau, capacite et ergonomie reelle restent non valides |

## Dette UX

`quick_asset_box` est une UI de test/developpement, pas une UX finale. Son champ texte assets, ses unites implicites, ses clearances, sa grille et ses politiques de sizing sont acceptables pour prototyper et investiguer, pas pour un utilisateur qui veut organiser un jeu.

Les problemes UX ne se resument pas a de meilleurs labels : il manque un modele d'interaction. L'utilisateur doit pouvoir voir la boite, construire un inventaire, exprimer des intentions, comparer des propositions et corriger localement une decision sans manipuler des champs techniques ou reconstituer mentalement le volume.

## Dette solver

La grille actuelle est une lattice de reservation, pas un solveur volumetrique. Le placement greedy `z/y/x` et le packing 2D local sont deterministes et utiles comme fondation, mais ne cherchent pas une repartition globale de modules, ne reordonnent pas les choix, ne gerent pas les compromis de retrait et ne produisent pas un ensemble de variantes classees pour l'utilisateur.

Le futur solveur ne doit pas etre introduit comme une simple feature suivante. Il doit consommer un plan de produit stable, gerer des contraintes explicites, refuser lisiblement les conflits et garder chaque proposition reproductible et explicable.

## Dette de modele volumetrique

Les concepts `Layer`, `Reservation`, `FreeVolume`, `RemovalOrder` et support existent deja partiellement dans la config/CAD IR, mais ne sont pas un graphe produit unique. Il manque notamment :

- un objet racine representant la boite complete et ses contraintes;
- la distinction explicite entre module physique, zone reservee et volume libre;
- les liens asset -> groupe -> compartiment -> module -> layer;
- une representation des contraintes de couvercle, boards, livrets et retrait;
- un contrat de score et de raisons de refus au niveau d'une variante complete.

## Ce qui doit devenir architecture produit

Les prochains sujets ne doivent plus etre traites comme des micro-features Fusion isolees :

1. Le plan de rangement complet de la boite doit devenir l'objet central du moteur.
2. L'inventaire asset-first et les intentions de rangement doivent devenir les entrees produit primaires.
3. Une variante de layout doit etre un resultat explicite, score, verrouillable et editable.
4. L'UI doit representer ces objets et ne plus etre une collection de champs CAD.
5. Fusion doit continuer a materialiser et exporter une decision deja prise par le moteur.

## Consequence P18

P18 doit produire les contrats UX et produit necessaires avant une nouvelle implementation. La prochaine mission codee ne doit pas etre un solveur global ni une palette HTML par reflexe : elle devra commencer par le plus petit plan de boite editable et verifiable, sous une gate humaine d'architecture/produit.
