# P64-L08D — corpus adversarial 3D et holdout neuf

Date : 2026-07-24
Statut : `done`, `automated-validated`, `no-solver-run`.

## 1. Résultat

P64-L08D livre un corpus exécutable pour la Gate A rectangulaire 3D. Il ne
mesure encore aucun moteur et ne revendique aucun gain produit.

- 41 cas ouverts : une matrice de 40 cas (10 familles, 3 paliers
  faisables et 1 négatif par famille) plus le projet BGIG revu intact ;
- 40 cas de holdout privés : 10 familles, les paliers `small`, `large` et `xl`,
  puis 1 cas négatif par famille ;
- 30 témoins ouverts construits sans solveur puis vérifiés en X/Y/Z ;
- 10 bornes négatives ouvertes, avec 7 formes de preuve ;
- 1 régression BGIG intacte, honnêtement `bounded_unknown` ;
- 0 appel de solveur et 0 ouverture du holdout.

Manifest public :
`tests/fixtures/p64_l08d_real_3d_corpus.v1.json`.

Digest du manifest :
`d4324eebbc0412b02b7ed6bdbd16eacf1b90146a9a45ed8ad6bff542e19fc0f9`.

## 2. Couverture Gate A

| Famille | Charge ouverte | Contrainte réellement portée par la recette et le témoin |
| --- | --- | --- |
| `layers` | 8 / 32 / 64 conteneurs | 3 à 5 niveaux, hauteurs 4/5/6 mm, croisements X/Y entre niveaux |
| `support` | 8 / 32 / 64 | charge pontée sur deux appuis et couverture surfacique totale |
| `reservations` | 8 / 32 / 64 | volumes réservés distincts bas et haut |
| `access` | 8 / 32 / 64 | empilement et ordre de retrait top-down |
| `fragmentation` | 8 / 32 / 64 | régions disjointes de 10 mm séparées par 2 mm |
| `variants` | 8 / 32 / 64 | fronts P45 de 1, 2, 4 et 8 variantes, rotations certifiées |
| `many-containers` | 32 / 32 / 64 | seuil 32 puis palier XL 64 |
| `many-assets` | 8 / 32 / 64 | 256 contenus distribués sans perte |
| `mixed-extreme` | 32 / 64 / 158 | 5 niveaux XL, 31 piles utiles, appuis multiples, accès, réservations, fragmentation, 8 variantes et jusqu'à 632 contenus |
| `real-anonymized` | régression intacte 18/20, puis 18 / 36 / 72 | projet BGIG revu conservé `bounded_unknown`, plus dérivés annoncés ×1/×2/×4 |

Chaque recette reconstruit un problème sans témoin, avec les variantes et
dimensions candidates de chaque conteneur. Un digest engage ce problème.
Chaque placement témoin contient ensuite une orientation autorisée, une
variante du front certifié, son nombre de contenus affectés, ses appuis et
son rang de retrait.
Le validateur rejette les collisions, sorties du monde, appuis absents ou
insuffisants, réservations traversées, ordre top-down invalide, région
fragmentée franchie, variante inconnue et affectation de contenus incomplète.

## 3. Témoins et bornes négatives

Les témoins ne sont pas des résultats préfabriqués d'un candidat : ils sont
construits par une routine indépendante, engagés par digest, puis recertifiés
au chargement du corpus.

Les cas impossibles utilisent selon la famille :

- dépassement de hauteur empilée ;
- aire d'appui disponible insuffisante ;
- volume requis supérieur au volume non réservé ;
- cycle formel d'ordre de retrait ;
- dimension supérieure à chaque région fragmentée ;
- aucune variante certifiée compatible ;
- volume requis supérieur à la capacité.

## 4. Holdout scellé

Le sidecar privé est conservé localement dans
`.codex-work/p64-l08d/sealed_holdout.private.json`. Il est ignoré par Git et
n'est pas inclus dans le manifest public.

Digest scellé :
`c5c23831d30396f56c265b5e6f79dad81fafd53600cd2e2f7e310e8e8cb8d0f8`.

Le reçu public expose seulement le digest, 40 cas, les trois paliers, 10
familles, `opened=false` et `solver_invocation_count=0`. Les recettes et le
nonce privés ne sont pas publiés. Les holdouts L06 et L07 ne sont pas réutilisés.

## 5. Limites honnêtes

- Neuf familles sont adversariales et synthétiques. `real-anonymized`
  conserve aussi le projet BGIG revu sans réduction et sans lui inventer de
  solution ; les paliers 18/36/72 sont des dérivés annoncés, pas trois
  nouveaux projets humains.
- Le corpus couvre T0/T1 rectangulaire. Il ne simule pas T2 à T4.
- Les témoins prouvent que les cas faisables ont une solution valide ; ils ne
  prouvent ni la difficulté d'un moteur ni une amélioration de BGIG.
- Aucun solveur externe n'a été téléchargé, construit, exécuté ou choisi.
- `fusion-validated=false` et `print-validated=false`.

## 6. Vérifications

- compilation Python des nouveaux producteur, script et tests ;
- 9/9 tests ciblés du corpus et de son scellement ;
- garde documentaire 2/2 et alignement Fusion-only 6/6 ;
- suite automatisée complète : 774/774 en 232,669 s ;
- `git diff --check` et contrôle du diff indexé.

## 7. Suite autorisée

P64-L08E peut maintenant construire les adaptateurs fidèles et les petits
contrôles exacts. Un candidat qui ne représente pas une contrainte active doit
retourner `unsupported` pour la famille concernée. Il est interdit de projeter
ce corpus au sol, de retirer une réservation ou un appui, ou d'ouvrir le
holdout pendant L08E.
