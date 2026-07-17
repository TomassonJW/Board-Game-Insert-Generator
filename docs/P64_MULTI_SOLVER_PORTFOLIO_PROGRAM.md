# P64 — Programme portefeuille multi-solveurs et finition volumique

Statut : architecture et trajectoire acceptées le 2026-07-17 ; aucun runtime
Prochaine mission exécutable : `P64-H05`.

Capability principale : `C-SOLVER`. Capabilities associées : `C-LAYOUT`,
`C-GRID-3D`, `C-STACKING`, `C-USABILITY`, `C-QUALITY`.

ADR : [ADR-0068](DECISIONS/ADR-0068-multi-solver-portfolio-and-truthful-results.md)
et [ADR-0069](DECISIONS/ADR-0069-continuous-and-modular-volume-finishing.md).

## 1. Résultat produit attendu

BGIG doit pouvoir résoudre des projets simples rapidement et des projets denses
avec une recherche plus robuste, sans confondre épuisement d'une heuristique et
impossibilité mathématique. L'utilisateur choisit, explicitement ou via `Auto
intelligent`, la famille de calcul, l'effort consenti, le critère de classement
et la finition du volume.

Le programme doit aboutir à :

- un chemin rapide conservant les qualités du solveur actuel par étages ;
- un placement 3D libre capable d'exploiter des espaces résiduels locaux ;
- un portefeuille qui compare plusieurs familles sous un budget commun ;
- des résultats, métriques et motifs d'arrêt honnêtes ;
- une finition continue puis modulaire, appliquée seulement après faisabilité ;
- une interface simple par défaut et des réglages avancés optionnels ;
- aucun recalcul métier dans Fusion et aucune matérialisation automatique.

## 2. Faits de départ et décision de rupture

P64-H01 est `fusion-validated` dans le package 0.1.42. P64-H02 est
`implemented` et `automated-validated` dans le package 0.1.44, mais son retour
Fusion est un KO contextuel : d'autres ajouts légers peuvent encore épuiser la
recherche malgré un volume manifestement disponible.

P64-H03R réintègre la diversité d'ordres et de structures H03 au-dessus de H04,
car elle résout des cas supplémentaires. Un autre cas réel reste en échec : H03R
reste `automated-validated`, sans preuve Fusion, et H06/H07 doivent aller plus loin.
`fusion-validated`, ni la base canonique de la suite.

Conclusion : ajouter indéfiniment des seeds à la même famille de recherche ne
constitue plus une stratégie suffisante. Le solveur actuel devient la famille
rapide de référence ; une famille 3D libre et une orchestration commune sont
ajoutées par missions séparées.

## 3. Frontières non négociables

- cœur Python pur, sans import `adsk` ; Fusion reste un adaptateur ;
- aucune dépendance d'optimisation lourde sans ADR et GO distincts ;
- aucune modification implicite des dimensions d'assets, cavités, jeux,
  tolérances, defaults, réservations ou règles physiques ;
- conteneurs droits ; rotations globales limitées à 0/90 degrés dans X/Y tant
  qu'un contrat ultérieur ne l'élargit pas ;
- une solution proposée est revalidée par le validateur exact commun avant
  affichage comme constructible ;
- aucune scène ne change avant `Matérialiser dans Fusion` ;
- aucun corps de remplissage automatique ; les cales restent explicites et
  hors du chemin critique ;
- aucune revendication `fusion-validated` sans observation humaine, ni
  `print-validated` sans impression réelle ;
- aucun seuil de quantité (2, 8, 32 ou autre) ne force un niveau Z : le nombre
  de niveaux résulte des dimensions réelles, contraintes, budget et score ;
- une seule mission active à la fois.

## 4. Quatre réglages produit orthogonaux

| Réglage | Valeurs cibles | Rôle |
| --- | --- | --- |
| Méthode de calcul | `Auto intelligent`, `Étages et piles`, `Placement 3D libre`, puis éventuellement `Comparer` en avancé | choisit les familles autorisées |
| Effort | `Rapide`, `Normal`, `Approfondi`, `Personnalisé` | fixe temps, largeur de recherche et nombre de candidats |
| Critère de classement | `Équilibré`, `Compact`, puis critères réellement mesurés | classe seulement les solutions validées |
| Finition du volume | `Auto`, `Libre`, `Alignement continu`, `Harmonisation modulaire`, puis `Vide regroupé` et `Cales explicites` | transforme une solution faisable sans participer à la preuve de faisabilité |

Les réglages ne doivent jamais être fusionnés dans un enum opaque. En
particulier, l'ancien `Priorité de la proposition` ne doit pas continuer à
sur-promettre des propriétés non mesurées : `accessible`, `impression simple`
ou `matière réduite` ne seront proposés que lorsque leur score possède une
sémantique testée.

## 5. Portefeuille algorithmique conservé

| Famille | Usage | Forces | Limites | Horizon |
| --- | --- | --- | --- | --- |
| `stage_stack` — Étages et piles | chemin rapide, compositions régulières | déterministe, explicable, peu coûteux | espaces libres fragmentés et franchissements de limites d'étage | conserver et encapsuler |
| `free_3d_greedy` — Points extrêmes / espaces maximaux | solution 3D rapide | exploite les vides locaux, peu de mémoire | sensible à l'ordre et aux choix précoces | P64-H06 |
| `free_3d_beam` — Recherche 3D robuste | projets denses | conserve plusieurs états prometteurs | coût CPU/mémoire supérieur | P64-H07 |
| `portfolio_auto` — Orchestrateur | valeur par défaut | compare plusieurs familles et retient le meilleur candidat validé | exige budgets, métriques et contrat commun | P64-H07/H08 |
| `exact_proof` — Preuve bornée | petits projets ou diagnostic expert | peut prouver une impossibilité dans un périmètre explicite | dépendance et explosion combinatoire possibles | P64-X01, futur sous gate |

Les grilles uniformes ou anisotropes restent des outils de laboratoire, des
seeds ou des diagnostics. Elles ne sont pas le solveur principal : une division
de chaque axe par 20 produit déjà 8 000 cellules, par 40 en produit 64 000 et
par 100 un million. Les coupes adaptatives issues des faces utiles sont
préférées à une voxelisation globale.

## 6. Contrat commun de stratégie

P64-H05 doit introduire une frontière interne stable, sans modifier le schéma de
projet utilisateur.

### Entrée minimale

- enveloppes minimales de conteneurs déjà dérivées ;
- variantes autorisées et rotations ;
- volume utile de boîte ;
- réservations supérieures et contraintes de support/retrait ;
- modes `Auto/Cible/Fixe` et valeurs sources ;
- profil d'effort et budget monotone ;
- identifiant de requête/révision pour la gestion des réponses obsolètes.

### Sortie minimale

- identifiant de famille et version ;
- statut de résultat ;
- zéro, une ou plusieurs propositions immuables ;
- certificat de validation commun pour chaque proposition complète ;
- score décomposé, sans propriété non calculée ;
- télémétrie et motif d'arrêt ;
- diagnostics structurés et localisés ;
- digest déterministe des entrées, paramètres et placements.

### Autorité

Les solveurs proposent. Le validateur commun certifie collisions, enveloppes,
cavités, fonds, parois, réservations, appuis, retrait, conservation et nombre de
corps automatiques nul. Une famille ne peut ni relaxer ni dupliquer ces règles.

## 7. Sémantique honnête des résultats

| Statut interne | Libellé utilisateur | Condition |
| --- | --- | --- |
| `solution_found` | `Solution trouvée` | au moins une proposition complète certifiée |
| `no_solution_within_budget` | `Aucune solution trouvée dans le budget` | recherche heuristique épuisée, tronquée ou sans candidat certifié |
| `proven_impossible` | `Impossible prouvé` | contradiction formelle ou moteur exact ayant couvert son domaine annoncé |
| `invalid_input` | `Projet à corriger` | entrée invalide avant recherche |
| `stale_or_cancelled` | non peint comme résultat courant | requête obsolète ou annulée |

Une proposition partielle peut être diagnostiquée, mais reste non
matérialisable. Le texte générique `Calcul impossible` est interdit quand seule
une heuristique a échoué.

## 8. Télémétrie minimale

Chaque run doit pouvoir exposer, sans données sensibles :

- famille, version, profil d'effort, request id et révision ;
- courant, obsolète ou annulé ;
- temps total et temps par phase ;
- variantes générées, dédupliquées et conservées ;
- états développés, coupés et raison agrégée de coupe ;
- placements et rotations essayés ;
- largeur de beam et profondeur maximale si applicables ;
- solutions complètes et certifiées ;
- score décomposé du candidat retenu ;
- budget consommé et motif d'arrêt.

La vue développeur sera secondaire, repliable ou détachable. Elle ne doit ni
voler le focus, ni reconstruire le DOM éditable, ni déclencher un calcul.

## 9. Variantes internes de conteneur

La recherche globale ne doit pas construire le produit cartésien de toutes les
dispositions internes. Le contrat futur est une petite frontière de Pareto par
conteneur : dimensions X/Y/Z, orientation, organisation des assets, coût local
et contraintes. Les symétries sont dédupliquées et les caps dépendent de
l'effort.

P64-H06/H07 utilisent d'abord une enveloppe canonique par conteneur. P45-M001
reste propriétaire de la sémantique `standard/auto`, `rangée` et `colonne
verticale`, puis livrera les variantes internes au contrat commun. Aucun contrôle
de disposition non-carte n'est ajouté en avance dans P64.

Le volume total minimal est une borne nécessaire, jamais une preuve : les bornes
par axe, sections, réservations, supports, retrait et fragmentation restent
obligatoires.

## 10. Placement 3D libre cible

Le moteur libre maintient des espaces maximaux vides et des points extrêmes issus
des faces déjà placées. Il choisit d'abord les participants les plus contraints,
pas seulement les plus volumineux. Un état de recherche contient placements,
espaces résiduels, surfaces d'appui, coupes X/Y/Z, score partiel et bornes.

Un conteneur supérieur peut chevaucher plusieurs conteneurs inférieurs si la
couverture d'appui et l'ordre de retrait passent la validation. Aucune règle dure
n'impose une dimension identique entre voisins ou zéro espace vide ; alignement,
contact et fragmentation sont des critères de score.

Le registre de slots reste léger : espaces maximaux vides, plans de coupe,
intervalles d'alignement, hypothèses de trame et composantes résiduelles. Il ne
devient ni une matrice 3D dense, ni une grille verrouillée tôt.

## 11. Finition après faisabilité

La finition reçoit une solution déjà certifiée. Elle peut augmenter seulement
les enveloppes extérieures des conteneurs dans leurs degrés de liberté ; elle ne
modifie jamais assets, cavités, parois minimales, fonds, jeux ou réservations.

1. `Alignement continu` propage le volume libre sur un graphe d'adjacence à
   topologie fixe, en favorisant faces alignées et vide regroupé.
2. `Harmonisation modulaire` infère une trame vectorielle `(u_x, u_y, u_z)` à
   partir des dimensions de boîte, faces observées, minima et réservations. Les
   enveloppes sont arrondies vers des multiples entiers compatibles.
3. Les cellules résiduelles sont affectées par dalles de face entières. Ajouter
   une unité Y à un conteneur `3 × 5 × 2` consomme `3 × 1 × 2 = 6` cellules.
   Le score peut privilégier une grande face compatible lorsque la déformation
   relative devient plus discrète, sans en faire une règle dure.
4. Chaque transformation est revalidée. Un échec de finition conserve la
   solution de base et ne devient jamais une impossibilité.

La trame peut être globale en X/Y et locale par zones en Z. Le mode `Auto`
essaie la finition et ne la conserve que si elle améliore le score sans dégrader
les contraintes ni le coût d'usage. Les résultats distinguent : totalement
harmonisé, partiellement harmonisé avec résiduel intentionnel, ou finition
rejetée avec solution de base conservée.

Alternatives graduées : redistribution continue, trames locales, regroupement du
résiduel en baie utile ou canal d'accès, puis seulement cales explicites. Les
cales et éventuelles nervures creuses nécessitent un contrat géométrique et une
validation physique ultérieurs.

## 12. Séquence d'exécution verrouillée

```text
P64-A01 documentation/ADR (ce document)
  -> P64-H04 vérité des statuts, observabilité, fixtures
  -> P64-H05 contrat commun + adaptation du solveur actuel
  -> P64-H06 placement 3D libre greedy EP/EMS
  -> P64-H07 beam robuste + portefeuille Auto
  -> P64-H08 réglages Fusion + diagnostic secondaire
  -> P64-V2 gate humaine solveur
  -> reprise P44-V
  -> P45/P46 selon leurs contrats existants
  -> P64-F01/F02 finitions continues et modulaires
  -> P47-P50
  -> P64-F03 cales explicites après preuves physiques suffisantes
  -> P64-X01 exact/proof seulement après nouvelle gate
```

P64-H04 à H08 forment le chemin critique de reprise : aucune mission P45/P46,
P47-P50, P67, P68 ou P69 n'est ouverte par ce document. P64-F01/F02 ne bloquent
pas la gate V0.2 P46 : elles sont planifiées après P46 et avant d'élargir les
finitions V0.3. P64-F03 dépend de retours d'impression pertinents. P64-X01 reste
hors chemin critique.

## 13. Cartes de mission exécutables

### P64-H04 — Résultats honnêtes, observabilité et corpus de régression

- Statut : `terminé et intégré` le 2026-07-17.
- Agent conseillé : Terra ; revue de contrat senior requise.
- Dépendances : P64-A01 accepté ; état P64-H03 local préservé en lecture seule.
- Objectif : rendre l'échec diagnosable avant tout nouvel algorithme.
- Livrables : statuts du §7, télémétrie du §8, export anonymisé des cas réels,
  fixtures petites/denses, vocabulaire `Niveaux de départ Z` distinct des
  couches visuelles.
- Non-objectifs : nouveau placement, modification des budgets de solution,
  changement de score, schéma projet, géométrie ou scène.
- Acceptation : un épuisement heuristique n'affiche jamais `Impossible prouvé` ;
  les anciens cas restent déterministes ; aucune réponse obsolète n'est peinte ;
  les métriques sont testées et absentes du parcours novice par défaut.
- Vérifications : tests ciblés résultat/bridge/DOM, suite complète,
  `compileall`, frontière `adsk`, `git diff --check`.
- Terminé quand : commit intégré à `main`, sans gate Fusion si les changements
  visibles restent limités aux libellés honnêtes et au diagnostic replié.

### P64-H05 — Contrat commun et baseline Étages et piles

- Statut : `ready`.
- Agent conseillé : Terra avec revue Luna/senior.
- Objectif : introduire l'interface stratégie/candidat/certificat et encapsuler
  la baseline H03R sans retirer ses placements de référence.
- Livrables : types immuables, budgets communs, validateur unique, adaptateur
  `stage_stack`, tests de parité bit-à-bit ou géométrique documentée.
- Non-objectifs : EP/EMS, beam, nouvelle UI, score physique, dépendance externe.
- Acceptation : fixtures H04 identiques sous baseline ; aucune famille ne peut
  contourner validation ; digest et télémétrie déterministes.
- Vérifications : tests de contrat et parité, suite complète et gardes usuelles.

### P64-H06 — Placement 3D libre greedy EP/EMS

- Statut : `blocked-by-P64-H05`.
- Agent conseillé : Luna/frontier ; revue algorithmique obligatoire.
- Objectif : obtenir un second moteur réellement différent avec une enveloppe
  canonique par conteneur.
- Livrables : espaces maximaux vides, points extrêmes, déduplication, choix du
  plus contraint, rotations XY, bornes simples, validation commune.
- Non-objectifs : beam large, variantes internes P45, grille dense, finition,
  exact solver ou nouvelle dépendance.
- Acceptation : corpus H04, franchissement d'un plan Z local, conteneur appuyé
  sur plusieurs supports valides, non-collision, déterminisme et budget dur.
- Performance initiale : benchmarker avant de fixer les budgets produit ; aucun
  seuil arbitraire n'est promu en default dans cette mission.

### P64-H07 — Beam robuste et portefeuille Auto

- Statut : `blocked-by-P64-H06`.
- Agent conseillé : Luna/frontier ; revue performance et produit obligatoire.
- Objectif : conserver plusieurs états 3D et comparer baseline, greedy et beam
  sous un budget monotone.
- Livrables : beam borné, profils Rapide/Normal/Approfondi, orchestrateur,
  déduplication inter-familles, sélection parmi candidats certifiés.
- Non-objectifs : moteur exact, propriétés d'accessibilité ou de matière non
  mesurées, réglages Fusion complets, finition modulaire.
- Acceptation : augmenter l'effort ne réduit jamais le portefeuille autorisé ;
  le mode Auto garde le chemin rapide sur cas simples et trouve au moins les cas
  denses du corpus ; timeout et annulation sont propres.

### P64-H08 — Réglages Fusion, critères honnêtes et diagnostic secondaire

- Statut : `blocked-by-P64-H07`.
- Agent conseillé : Terra ; revue UX humaine à la gate.
- Objectif : exposer méthode, effort et classement sans surcharger le parcours.
- Livrables : `Auto intelligent` par défaut, choix avancés, temps réel du dernier
  run, compteurs lisibles, persistance additive et gestion des projets anciens.
- Non-objectifs : autosave en effort approfondi illimité, fenêtre modale,
  reconstruction du DOM éditable, matérialisation automatique ou finition HMA.
- Acceptation : Rapide/Normal/Approfondi ont des budgets distincts et testés ;
  autosave reste borné ; focus/sélection survivent aux mises à jour ; options
  indisponibles ne sont pas affichées comme actives.
- Sortie : préparer `P64-V2`, puis ne demander à Thomas que les observations
  Fusion restantes.

### P64-F01 — Fermeture continue par graphe d'adjacence

- Statut : `planned-after-P46`.
- Agent conseillé : Luna/frontier.
- Objectif : redistribuer le résiduel sans changer la topologie ni créer de
  corps, puis revalider.
- Acceptation : conservation, contraintes inchangées, amélioration mesurée,
  fallback exact vers la solution de base.

### P64-F02 — Harmonisation modulaire adaptative

- Statut : `blocked-by-P64-F01`.
- Agent conseillé : Luna/frontier.
- Objectif : inférer des trames candidates globales/locales, arrondir les seules
  enveloppes extensibles et répartir les cellules résiduelles.
- Acceptation : topologie des cellules explicitée, aucun GCD/median magique,
  coût borné, résultat total/partiel/rejeté, solution de base préservée.

### P64-F03 — Résiduel utile et cales explicites

- Statut : `blocked-by-P64-F02-and-physical-feedback`.
- Agent conseillé : Terra pour le contrat, Luna pour la géométrie éventuelle.
- Objectif : regrouper le vide en baie/canal utile, puis proposer des cales
  seulement sur confirmation.
- Interdit : corps automatique, allégation de tenue ou d'impression sans preuve.

### P64-X01 — Mode exact / preuve pour petits projets

- Statut : `future-gated`.
- Agent conseillé : Luna/frontier.
- Préconditions : benchmark du portefeuille, besoin produit démontré, ADR de
  dépendance, GO explicite et limites de taille affichées.
- Objectif : prouver faisabilité ou impossibilité dans un domaine annoncé ; ne
  jamais devenir la dépendance silencieuse du parcours normal.

## 14. Contrat de reprise pour agents Terra ou Luna

Avant toute mission de ce programme, l'agent doit :

1. vérifier Git, `origin/main` et les modifications étrangères ;
2. lire `PILOTAGE_CURRENT`, `NEXT_ACTIONS`, `HUMAN_GATES`, ce programme, les ADR
   0068/0069 et le contrat spécifique de la mission ;
3. reproduire ou geler les fixtures exigées avant de modifier l'algorithme ;
4. annoncer les invariants qui ne changent pas ;
5. implémenter une seule carte, sans anticiper la suivante ;
6. tester déterminisme, budget, validation commune et réponses obsolètes ;
7. mettre à jour pilotage et preuves, relire le diff, committer puis intégrer
   selon `AGENTS.md` ;
8. ne préparer une gate Fusion que si la carte la demande explicitement.

Un agent Terra ne doit pas improviser H06/H07/F01/F02 à partir de ce seul résumé :
il suit le contrat de mission, les fixtures et les invariants. Un agent Luna ne
doit pas élargir le schéma, les règles physiques ou les dépendances sous prétexte
d'optimisation.

## 15. Definition of Done du programme critique

Le chemin P64-H04 à P64-H08 est terminé seulement si :

- les trois familles non exactes partagent un contrat et un validateur ;
- les cas réels anonymisés restent dans la suite de régression ;
- un échec heuristique est distingué d'une impossibilité prouvée ;
- le mode Auto choisit parmi des solutions certifiées et explique son arrêt ;
- les budgets sont monotones, bornés et observables ;
- l'UI conserve focus, sélection, autosave et matérialisation explicite ;
- la gate P64-V2 est positive dans Fusion ;
- `print-validated: false` reste explicite.
