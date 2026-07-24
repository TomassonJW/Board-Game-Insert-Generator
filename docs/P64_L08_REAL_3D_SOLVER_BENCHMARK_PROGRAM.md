# P64-L08 — benchmark réel de solvage 3D des cas limites BGIG

Statut : `architecture-accepted`, `ready-for-execution` après P64-L08A.
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
| P64-L08G | intégration mesurée et gate Fusion humaine | aucune régression et observation humaine ciblée |

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
