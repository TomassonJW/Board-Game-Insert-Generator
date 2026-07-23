# P64-L06B — Preuve du corpus T0/T1 généré

## Résultat

P64-L06B livre un benchmark reproductible et autonome : huit cas historiques de
régression et 192 cas générés. Le solveur, les budgets et le runtime Fusion ne
sont pas modifiés.

Digest du manifest :
`53db786793dee3a26128f4db28cc830f68dde394262cd7ffbfad27cb895a85ee`.

## Corpus livré

| Split | Cas | Faisables construits | Impossibles prouvés | Répartition des familles |
| --- | ---: | ---: | ---: | --- |
| regression | 8 | historique | historique | 7 cas L05D1 + 1 cas réel L06A |
| discovery | 64 | 47 | 17 | 13 / 13 / 13 / 13 / 12 |
| tuning | 64 | 46 | 18 | 13 / 13 / 13 / 13 / 12 |
| holdout | 64 | 47 | 17 | 13 / 13 / 13 / 13 / 12 |

L'ordre des cinq nombres est : nombreux/un, peu/nombreux, nombreux/nombreux,
mixte, incrémental puis froid.

Chaque split généré couvre les groupes `2, 4, 8, 12, 18, 30, 50`, les contenus
par conteneur `1, 2, 4, 8, 16, 32`, un à trois étages, les trois densités, les
trois profils de dimensions, les réservations, les deux politiques de rotation
et les quatre ordres d'entrée.

## Validité des oracles

Tous les cas faisables de `discovery` et `tuning` sont rematérialisés et validés :

- chaque contenu tient dans sa cavité avec murs et plancher ;
- chaque conteneur possède au moins une variante locale P45 certifiée ;
- les placements globaux restent dans la boîte et ne se chevauchent pas ;
- les réservations, appuis d'étage et ordres de retrait sont vérifiés ;
- le témoin n'est pas envoyé au solveur testé.

Audit P45 complet des deux splits ouverts :

- `discovery` : 666 frontières, 0 frontière vide sur les cas faisables ;
- `tuning` : 710 frontières, 0 frontière vide sur les cas faisables ;
- comptes certifiés réellement observés : `1, 2, 3, 4, 6, 8`, donc la matrice
  requise `1, 2, 4, 8` est couverte ;
- les frontières vides restantes appartiennent exclusivement aux cas négatifs,
  dont la preuve indépendante reste vérifiée.

Les impossibilités sont recalculées depuis les dimensions du projet. Le
validateur refuse un volume qui ne dépasse pas strictement la boîte, une hauteur
qui ne dépasse pas strictement la hauteur disponible ou un digest altéré.

## Séquences incrémentales

Chaque split contient douze cas E, groupés en six paires. Pour chaque paire :

- les digests du projet précédent sont identiques ;
- les digests du projet courant sont identiques ;
- un membre demande le parcours incrémental, l'autre une reconstruction froide ;
- le projet précédent et le projet courant sont toujours différents.

## Holdout fermé

Le manifest enregistre un engagement SHA-256 sur les 64 recettes du holdout. Les
API refusent son accès sans trace d'un candidat unique sélectionné auparavant.
Le test vérifie le refus implicite et le rejet d'une sélection altérée. Aucun cas
du holdout n'a été exécuté par le solveur pendant L06B.

## Contrôle de bout en bout

Le cas construit `discovery-e-005`, deux conteneurs, est rejoué en effort Rapide.
Le solveur courant retourne `solution_found` et le certificat global BGIG est
`certified: true`.

Observation exploratoire distincte, à confirmer formellement dans L06D : le cas
faisable `discovery-a-001`, huit conteneurs et forte marge, reste
`no_solution_within_budget` en Rapide puis Normal. Il atteint seulement une
profondeur partielle sous les caps courants. Ce fait suggère une lacune de
profondeur ; il ne constitue encore ni une statistique de campagne ni une
hypothèse sélectionnée.

## Reconstruction et confidentialité

Le constructeur produit la fixture dans un fichier séparé et sa vérification
`--check-existing` confirme l'identité exacte. Les deux corpus sources gardent
leurs digests historiques. La fixture ne contient ni chemin `C:\Users`, ni nom
personnel, ni `client_context`.

## Validation automatisée

- tests ciblés L06B : 9/9 OK ;
- reconstruction octet pour octet : OK ;
- audit P45 discovery/tuning : OK ;
- petit replay certifié : OK ;
- garde documentaire : 2/2 OK ;
- alignement Fusion-only : 6/6 OK ;
- suite complète : 698/698 OK en 171,783 s ;
- Ruff ciblé : OK ;
- `py_compile` ciblé : OK ;
- `git diff --check` : OK avant staging.

La première invocation des deux gardes par nom de module a échoué parce que le
répertoire `tests` n'est pas un package Python. Les deux relances canoniques par
`unittest discover` sont vertes ; aucun test produit n'a échoué.

## Limites

- le nombre cible de variantes n'est pas présenté comme le nombre exact de
  chaque cas ; l'audit réel fournit la preuve de couverture ;
- l'interdiction de rotation est une contrainte du benchmark, car le schéma
  projet courant n'expose pas ce contrôle ;
- le holdout reste fermé ; aucun résultat fonctionnel n'est connu ;
- le petit oracle exact exhaustif et les adapters arrivent en L06C ;
- aucune capacité générale n'est revendiquée depuis le petit replay positif ;
- `fusion-validated: false` ;
- `print-validated: false`.

## Suite

Intégrer L06B dans `main`, puis ouvrir P64-L06C : interface commune offline,
petit oracle exact interne sans dépendance et recertification de toute sortie par
BGIG.
