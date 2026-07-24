# P64-L09C — réservations supérieures fidèles dans SCIP

Date : 2026-07-24
Statut : implemented-product, automated-validated, fusion-validated=false,
print-validated=false.

## Résultat

La lane produit SCIP n'écarte plus les projets qui contiennent des
`top_inset_zones`. Chaque réservation est transmise au worker en coordonnées
entières au millième de millimètre avec son origine XY, sa taille XY, son plan
d'appui, sa profondeur et le sommet de conception. Une valeur qui ne peut pas
être représentée exactement reste refusée avant l'appel natif avec
`product_geometry_not_exactly_representable`.

Dans le MIP, chaque corps et chaque orientation doit satisfaire au moins une
des conditions suivantes : rester à gauche, à droite, devant, derrière ou sous
la réservation ; sinon, atteindre exactement le sommet et chevaucher réellement
l'empreinte. Au moins un corps doit porter chaque réservation. Un corps trop
mince ne peut pas la porter. Une cavité qui croise la réservation doit conserver
sa profondeur augmentée de l'encastrement et le fond minimal ; sinon le modèle
impose que la cavité reste hors de l'empreinte.

Le remplissage hybride des familles répétées est désactivé sur ces problèmes :
il ne pourrait pas ajouter honnêtement des corps après le solve sans réappliquer
les contraintes de réservation. Le budget, le nombre de threads, la limite de
solution, le runtime natif et les tolérances restent inchangés.

## Chaîne de vérité

- le worker SCIP interdit les occupations incompatibles du prisme réservé ;
- les dimensions physiques sont séparées des paddings de jeu du modèle ;
- les profils de support conservent l'épaisseur de fond et les cavités pour
  chaque variante et chaque rotation ;
- le validateur BGIG existant reste l'autorité finale pour les découpes, la
  prise, les parois, les fonds, la compensation de profondeur et la publication ;
- aucun résultat SCIP non recertifié ne devient matérialisable.

## Preuves

- tests ciblés SCIP : 16 cas sous Python 3.10, dont 1 test natif CPython 3.14
  ignoré hors environnement Fusion ;
- preuve native séparée avec le Python 3.14 de Fusion et le runtime SCIP scellé :
  1/1, `solution_found`, une invocation, corps porteur au sommet ;
- encastrements : 8/8 ;
- placement minimal : 14/14 ;
- suite complète : 847/847 en 242,868 s, avec le test natif CPython 3.14
  ignoré sous Python 3.10 puis exécuté séparément 1/1 ;
- Ruff ciblé : OK ;
- sources worker canonique et embarquée : SHA-256 identiques ;
- artefact worker rescelle :
  `2303d34a20bbe80059178614793f34bec31093560af447239ffa0ad7d1cd8258` ;
- archive native inchangée :
  `0a718ea5884d6326d66777db0ab853a31fa981e6392b89f184342fde27d465c6`.

La preuve native locale n'est pas une gate Fusion produit : elle exécute le vrai
worker SCIP avec le CPython 3.14 de Fusion, sans ouvrir de scène, sans benchmark
et sans lire le holdout. L'observation combinée dans la palette appartient à
P64-L09V.

## Non-objectifs confirmés

Aucun benchmark, tuning, holdout, changement de budget, UI, tolérance, pose,
format projet, CAD ou valeur physique. P64-F01B reste propriétaire de
l'expansion Z couplée, de la réparation locale et du certificat global de
fermeture.
