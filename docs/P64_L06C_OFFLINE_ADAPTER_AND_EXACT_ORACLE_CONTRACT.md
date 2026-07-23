# P64-L06C — contrat des comparateurs offline et du petit oracle exact

## 1. Statut et objectif

Statut : `implemented-core`, `automated-validated`.

L06C fournit une seule forme de résultat pour comparer, hors Fusion, au plus
deux candidats : le solveur BGIG courant et un petit oracle exact interne. Ce
lot ne choisit pas de nouveau solveur produit et ne modifie aucun routage.

`fusion-validated: false`. `print-validated: false`.

## 2. Deux candidats, pas davantage

Le protocole `bgig.solver_benchmark_adapter_protocol.v1` expose exactement :

1. `current_bgig_minimal_layout`, enveloppe du solveur produit courant ;
2. `internal_exact_floor`, référence exacte interne en bibliothèque standard.

Aucun exécutable, package, service ou solveur externe n'est installé. Les futurs
PackingSolver, LAFF ou CP-SAT devront adopter le même protocole, mais exigent
leurs décisions et autorisations propres.

## 3. Entrée commune

Un adapter reçoit un cas de benchmark avec :

- un `case_id` ;
- un projet `bgig.project.v1` normalisé ;
- son digest exact ;
- le profil d'effort ;
- le split et la famille lorsqu'ils existent ;
- les contraintes de benchmark utiles.

Le projet est renormalisé et son digest revérifié avant tout calcul. Le témoin ou
la preuve oracle du corpus n'est jamais transmis au candidat et n'est pas lu par
l'algorithme de l'adapter.

## 4. Sortie commune

Chaque résultat `bgig.solver_benchmark_adapter_result.v1` contient :

- identité et version de l'adapter ;
- identité du cas sans recopier le projet ;
- statut et raison d'arrêt ;
- contraintes non prises en charge ;
- portée exacte éventuelle et caps ;
- compteurs déterministes ;
- résultat de la recertification BGIG ;
- résumé compact de la solution ;
- digest déterministe du rapport.

Les statuts supplémentaires du benchmark sont :

- `proven_impossible` : espace déclaré entièrement épuisé ou borne stricte ;
- `bounded_unknown` : plafond atteint ou certification insuffisante ;
- `unsupported` : contrainte hors du modèle déclaré ;
- `certificate_rejected` : proposition refusée par la nouvelle recertification.

Ils ne changent pas les statuts publics du solveur produit.

## 5. Recertification obligatoire

Une solution n'est publiée dans le rapport que si le certificat
`bgig.minimal_layout_certificate.v1` vient d'être recalculé depuis :

- les placements ;
- les dimensions monde et locales ;
- les rotations ;
- le digest certifiable ;
- les invariants de cavités, parois, fonds, réservations, support, retrait,
  conservation, corps demandés seulement et résiduel non distribué.

Le certificat embarqué par un plan n'est donc jamais cru seul. Une recertification
négative devient `certificate_rejected` et aucune solution n'est exposée.

## 6. Modèle exact interne

Le modèle `canonical_minimum_envelopes_single_floor_v1` est exact seulement dans
le périmètre suivant :

- cas généré T0 ;
- deux à quatre conteneurs ;
- un seul niveau, tous les conteneurs sur le fond ;
- aucune réservation supérieure ;
- aucun complément ou corps automatique ;
- une seule variante locale P45 retenue par conteneur ;
- rotation Z autorisée ou interdite selon la contrainte du benchmark ;
- enveloppes minimales canoniques, marges BGIG et boîte utile courantes.

Les plafonds par défaut sont 4 participants, 250 000 états et 1 000 000 essais
de placement. Il n'existe aucune limite temporelle cachée.

## 7. Exhaustivité du petit modèle

La recherche énumère de façon déterministe :

- l'ordre des conteneurs ;
- les orientations autorisées ;
- les positions stables à gauche et en bas, formées par la limite de boîte ou la
  face d'un conteneur déjà posé plus la marge commune ;
- tous les états distincts jusqu'à solution certifiée ou épuisement.

Tout placement rectangulaire continu sur un seul niveau peut être tassé vers la
gauche et le bas sans perdre sa faisabilité. Une solution stable possède donc
ces coordonnées de contact. L'énumération couvre ce modèle continu sans grille
arbitraire.

Des bornes généreuses indépendantes prouvent aussi certains rejets fixes :
hauteur individuelle, empreinte individuelle, volume total ou aire totale du
niveau. Elles ignorent volontairement les marges lorsqu'une boîte plus grande
suffit déjà à prouver l'impossibilité.

## 8. Refus honnêtes

L'oracle exact répond `unsupported` pour plusieurs niveaux, réservations,
plusieurs variantes locales, plus de quatre conteneurs ou compléments.

L'adapter du solveur courant répond `unsupported` lorsque le benchmark interdit
la rotation, car `bgig.project.v1` n'expose pas ce contrôle. Un cas incrémental
exige un incumbent explicite ; il n'est jamais transformé silencieusement en cas
froid.

Atteindre un cap donne `bounded_unknown`, jamais `proven_impossible`.

## 9. Séparation des splits

L06C valide le protocole sur les régressions et sur le split discovery. Le
holdout reste fermé. L'adapter n'ouvre aucun split lui-même et ne contourne pas
la sélection unique exigée par L06B.

## 10. Frontières absolues

Ce lot ne modifie ni solveur, lane, ordre produit, budget public, deadline,
schéma projet, géométrie, tolérance, ownership P45/P64, finalisation, CAD, scène,
manifest Fusion ou valeur physique. Il ne revendique rien de nouveau sur le cas
dense 11 × 34.
