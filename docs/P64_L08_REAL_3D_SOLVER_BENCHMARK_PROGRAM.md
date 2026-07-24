# P64-L08 — benchmark réel de solvage 3D des cas limites BGIG

Statut : `executed-through-L08H`, `benchmark-winner-scip`, `abi-pass`, `negative-package-redistribution-incomplete`, `no-fusion-gate`.
Autorité : ADR-0083, ADR-0068, ADR-0079.
Capability : `C-SOLVER`, `C-LAYOUT`, `C-GRID-3D`, `C-LAYERS`, `C-STACKING`,
`C-QUALITY`.

## 1. But produit non négociable

Trouver, mesurer puis intégrer seulement le ou les algorithmes qui améliorent
réellement BGIG sur ses cas limites : beaucoup de conteneurs, beaucoup de
contenus par conteneur, variantes locales P45, remplissage serré, étages,
empilement, appuis, réservations et ordre de retrait.

Le but n'est pas de gagner une micro-épreuve 2D. Le but est d'augmenter le taux
de plans mondes complets et certifiés, sans rendre le parcours courant plus lent
ni moins fiable.

## 2. Portée en deux gates explicites

### Gate A — T0/T1 rectangulaire 3D complète, obligatoire

Chaque candidat global doit représenter sans perte :

- placements X/Y/Z, étages et empilement ;
- collisions, marges, boîtes, réservations basses et supérieures ;
- couverture d'appui et support multi-conteneurs ;
- rotations autorisées par le contrat courant ;
- ordre de retrait, accès top-down et contraintes de visibilité utiles ;
- une à plusieurs variantes locales P45 certifiées par conteneur ;
- projets froids et incrémentaux lorsque la famille le revendique.

Une implémentation qui omet l'une de ces règles ne participe pas au classement de
la famille concernée. Elle peut être mesurée comme lane spécialisée seulement.

### Gate B — T2 à T4 et formes non rectangulaires

Elle commence après que P45 expose une géométrie, une discrétisation ou une
décomposition et un certificat fidèles. Elle ne sera jamais simulée par des
boîtes sans le dire. Son absence n'empêche pas Gate A, mais interdit toute
allégation « toutes formes BGIG ».

## 3. Corpus adversarial obligatoire

Le corpus est organisé en familles, chacune avec cas ouverts, témoins certifiés,
bornes négatives et difficultés croissantes :

| Famille | Ce qu'elle force | Échec interdit |
| --- | --- | --- |
| `layers` | 2 à 5 niveaux réels, hauteurs hétérogènes et croisements Z | projection au sol |
| `support` | appuis complets et multi-supports, ponts admissibles ou refusés | simple collision sans portance |
| `reservations` | plateaux, livrets, zones hautes et volumes interdits | retrait silencieux de réservation |
| `access` | ordre de retrait et accès top-down | solution physiquement bloquée |
| `fragmentation` | vides disjoints, dimensions adversariales et quasi-saturation | score volumique seul |
| `variants` | fronts P45 de 1, 2, 4 et 8 variantes par conteneur | produit cartésien non borné |
| `many-containers` | au moins 32 groupes, puis palier XL 64 groupes | succès sur un seul 11 × 34 |
| `many-assets` | au moins 256 contenus répartis et variantes locales dérivées | réduction à une boîte par contenu sans preuve |
| `mixed-extreme` | forte cardinalité, plusieurs niveaux, réservations et accès réunis | retrait d'une contrainte active |
| `real-anonymized` | cas issus des journaux ou projets BGIG revus | benchmark artificiel seul |

Le palier XL ne vaut que s'il conserve les mêmes règles que le cas source. Les
tests faciles servent au débogage, jamais au classement principal. Chaque cas
faisable possède un témoin indépendant ; les cas impossibles possèdent une borne
formelle de portée annoncée.

## 4. Candidats et modèles à tester

L'audit repart des sources officielles actuelles ; aucune version ou victoire L07
ne sera réutilisée sans vérification. Il doit inclure au minimum :

1. un solveur spécialisé de packing 3D natif ;
2. une famille constructive 3D par niveaux ou points extrêmes ;
3. une famille contraintes/CP capable d'exprimer le contrat complet ;
4. une famille MIP/CIP capable d'exprimer le contrat complet ;
5. le portefeuille interne BGIG comme baseline.

PackingSolver, LAFF, OR-Tools, SCIP et HiGHS sont des candidats à réauditer,
pas des gagnants acquis. Les moteurs spécialisés doivent être appelés dans leur
vrai mode 3D. Les moteurs génériques doivent recevoir une formulation complète,
pas la projection `floor_problem` L07.

## 5. Équité de comparaison

Les candidats ne reçoivent pas nécessairement le même fichier technique ; ils
reçoivent la même sémantique BGIG. Chaque adapter fournit une matrice déclarée :

- règle BGIG représentée, méthode de traduction, preuve de fidélité ;
- règle non représentée, statut `unsupported` ;
- ressources : CPU, mémoire, threads, temps total et temps de préparation ;
- déterminisme, seed, warm start éventuel et arrêt ;
- sortie reconstruite puis certifiée par BGIG.

Interdits : projection 2D cachée, retrait d'étage, retrait de réservation,
supposition d'appui, changement de rotation ou amélioration par données du
holdout.

## 6. Mesures et sélection

Le classement suit cet ordre :

1. couverture sémantique complète de chaque famille ;
2. nombre de plans mondes complets certifiés ;
3. respect des appuis, retraits, réservations et variantes ;
4. qualité mesurée : pression de remplissage, fragmentation, accès et nombre de
   conteneurs satisfaits ;
5. temps au premier plan certifié puis distributions P50/P95 ;
6. mémoire, timeouts et stabilité de reprise.

Un gain de vitesse ne compense jamais un plan perdu, invalide ou simplifié. Un
gain de qualité sur cinq cas simples ne compense jamais l'absence de couverture
des familles limites.

Un portefeuille est admis seulement si chaque composant gagne au moins une
famille distincte et si l'ensemble bat le meilleur moteur seul sous ressources
équivalentes. Sinon le meilleur moteur unique est retenu. Si aucun candidat ne
franchit la gate, le résultat négatif est la décision correcte.

## 7. Nouveau holdout et montée en charge

Après discovery et tuning, la sélection est scellée : code, modèles, versions,
caps, adaptateurs et critères. Un nouveau holdout est alors généré, séparé de
L06 et L07, avec les mêmes familles et au moins un cas de chaque palier de charge.

Le rapport publie une courbe par famille et par taille : solution certifiée,
temps au premier résultat, temps terminal, mémoire et motif d'arrêt. Un seul cas
nommé, y compris 11 × 34, ne peut jamais résumer la capacité.

## 8. Découpage de missions

| Mission | Livrable | Critère de sortie |
| --- | --- | --- |
| P64-L08A | correction L07, ADR-0083 et ce programme | pilotage sans fausse clôture |
| P64-L08B | diagnostic de régression et quarantaine HiGHS 2D | mesure avant/après sur corpus 3D existant |
| P64-L08C | audit officiel des moteurs réellement 3D | shortlist avec matrice de fidélité complète |
| P64-L08D | corpus adversarial, témoins et nouveau holdout | chaque famille Gate A couverte |
| P64-L08E | adapters 3D fidèles et petits contrôles exacts | aucun `unsupported` caché |
| P64-L08F | discovery, tuning, sélection scellée et holdout | vainqueur ou résultat négatif honnête |
| P64-L08G | audit du paquet gagnant | refus fail-closed si ABI ou redistribution échoue |
| P64-L08H | remédiation du paquet `cp314` | probe technique puis audit complet des avis natifs |
| P64-L08I | ADR et audit pré-build minimal | modèle, sources, toolchain, licences et options verrouillés |
| P64-L08J | build et équivalence publique | DLL inventoriées, probe hors ligne, holdout scellé |

Une mission est committée et intégrée avant la suivante. Aucun run lourd ne
démarre avant L08C/D : l'audit et le corpus doivent empêcher de brûler du temps
sur un moteur incapable de représenter le besoin.

## 9. Invariants

- cœur Python pur ; Fusion reste un adaptateur et ne pilote aucun solveur ;
- aucune modification silencieuse des dimensions, tolérances, certificats,
  schéma, géométrie, finalisation, CAD ou scène ;
- aucun SaaS, compte, secret, télémétrie ni installation globale ;
- un résultat heuristique épuisé reste `no_solution_within_budget` ;
- le holdout n'est ouvert qu'une fois ;
- validation Fusion et impression restent des preuves distinctes ;
- la vitesse est mesurée sur les cas réels et adversariaux, pas inférée d'une
  moyenne de cas faciles.

## 10. Définition de réussite

La gate réelle est passée seulement lorsqu'un rapport montre, sur un corpus 3D
à forte cardinalité, un gain fonctionnel et de performance reproductible contre
la baseline BGIG, sans perte de certificat ni couverture perdue. À défaut, le
projet conserve le portefeuille interne et publie honnêtement l'échec.

## 11. État exécuté après P64-L08F

Les quatre moteurs externes ont été exécutés sur les dix familles et le holdout
indépendant a été ouvert exactement une fois. Une récupération conforme aux
règles préenregistrées invalide 10 preuves baseline obtenues par lecture d'une
borne de corpus, sans réexécuter de worker ni rouvrir le privé.

Le portefeuille SCIP + OR-Tools + LAFF est rejeté, car il perd 3 vérités face à
SCIP seul. SCIP est retenu avec 18 gains et 0 perte face au comportement BGIG
corrigé : la gate benchmark est passée. La gate produit reste fermée tant que la
redistribution Windows native n'est pas entièrement auditée et versionnée.

P64-L08G possède cette gate. Il peut intégrer SCIP seul et préparer Fusion
uniquement si la redistribution et les non-régressions passent ; sinon il doit
clore sans moteur produit.

## 12. État exécuté après P64-L08G

Le runtime SCIP/PySCIPOpt Windows acquis est entièrement inventorié : deux
wheels, 61 194 406 octets compressés, 187 848 352 octets décompressés et dix
DLL verrouillées par SHA-256. La gate produit échoue fermée pour quatre raisons :

- ABI PySCIPOpt `cp310` incompatible avec le Python `cp314` observé dans Fusion
  2704.1.36 ;
- versions exactes incomplètes pour plusieurs dépendances natives ;
- avis tiers absents du wheel PySCIPOpt ;
- autorité de redistribution des binaires précis non entièrement liée.

SCIP reste le gagnant benchmark à +18/−0 face à BGIG corrigé. Aucun autre moteur
ne le remplace après lecture du holdout. Aucun runtime produit, package Fusion,
cap, certificat, schéma, tolérance ou comportement BGIG ne change. La gate
Fusion L08 n'est ni préparée ni installée.

Décision : `negative_no_product_integrable_winner`. Le programme L08 est terminé
honnêtement ; `fusion-validated=false` et `print-validated=false`.

## 13. État exécuté après P64-L08H

Le candidat officiel PyPI PySCIPOpt 6.2.1 `cp314` est retenu pour l'audit afin
de conserver la route SCIP 10.0.2 du tournoi. Avec NumPy 2.5.1, il passe un
probe exact dans Python 3.14 isolé, hors ligne et sans installation globale.
L'ABI produit n'est donc plus le blocage.

Les deux wheels totalisent 61 937 391 octets compressés et 186 127 316 octets
décompressés. Leurs 30 binaires `.pyd` et `.dll`, ainsi que les artefacts de
provenance `scipoptsuite-deploy` v0.12.0 et Ipopt 3.14.19, sont verrouillés par
empreinte. Toutes les versions natives utiles à l'audit sont identifiées.

La gate de redistribution échoue néanmoins : les avis SCIP, Ipopt,
MUMPS/METIS, Intel et Microsoft ne sont pas tous présents dans le candidat et
les autorités Intel/Microsoft ne sont pas entièrement établies. Aucun runtime
n'est intégré et aucune gate Fusion n'est préparée.

Décision : `negative_package_redistribution_incomplete`. La suite P64-L08I doit
cadrer par ADR et auditer une fabrication SCIP minimale `cp314`, sans les
composants non requis Ipopt/MUMPS/Intel. Le holdout reste consommé et interdit
à tout replay ou réglage ; `fusion-validated=false` et
`print-validated=false`.

## 14. État exécuté après P64-L08I

ADR-0084 définit un candidat MIP minimal sans modifier le gagnant : SCIP 10.0.2,
SoPlex 8.0.2, PySCIPOpt 6.2.1 `cp314`, plugins MIP internes, symétrie `snauty`
et LTO. L'audit statique du worker scellé confirme uniquement des variables
binaires ou entières et des expressions linéaires, tout en conservant les
collisions X/Y/Z, étages, appuis, réservations, régions, variantes et retraits.

Les trois archives source officielles, Python 3.14 de build, Cython, setuptools,
wheel, NumPy, MSVC, Windows SDK et CMake sont verrouillés par version, taille et
SHA-256. La cible exclut Ipopt, MUMPS/METIS, les runtimes Intel, PaPILO/TBB,
GCG, ZIMPL, GMP et le mode exact. SoPlex reste obligatoire pour les relaxations
LP.

Décision : `minimal_scip_build_audit_pass`. Seul P64-L08J est autorisé : build
reproductible, inventaire réel des DLL, avis complets, probe hors ligne et
équivalence sur cas publics. Aucun runtime produit ou add-in Fusion n'est
modifié ; le holdout reste consommé et interdit. `fusion-validated=false` et
`print-validated=false`.