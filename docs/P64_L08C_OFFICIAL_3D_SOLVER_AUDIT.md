# P64-L08C — audit officiel des candidats de solvage 3D réel

Date : 2026-07-24

Statut : `done`, `documentation-validated`, `no-winner-selected`.

## 1. Règle de sélection

Cet audit ne choisit pas un gagnant sur une promesse de vitesse. Un candidat ne
peut entrer dans le tournoi global que s'il peut recevoir sans perte le contrat
T0/T1 : coordonnées X/Y/Z, collisions, rotations autorisées, étages, appuis,
réservations hautes, accès, variantes P45 et recertification BGIG.

Un moteur qui n'offre qu'un emballage de boîtes 3D reste mesurable, mais ne
classe pas les familles BGIG qu'il ne sait pas représenter. Aucune construction
ou installation n'est faite pendant cet audit.

## 2. Sources primaires consultées

- [PackingSolver — dépôt et licence MIT](https://github.com/fontanf/packingsolver)
  et sa [documentation `box`](https://fontanf.github.io/packingsolver/).
- [PackingSolver `box-stacks`](https://fontanf.github.io/packingsolver/boxstacks.html).
- [LAFF / 3d-bin-container-packing](https://github.com/skjolber/3d-bin-container-packing).
- [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver).
- [SCIP — site officiel, distribution et licences](https://scipopt.org/).
- [HiGHS — site officiel](https://highs.dev/).
- [Choco Solver — site officiel](https://choco-solver.org/).
- [Cbc — dépôt officiel](https://github.com/coin-or/Cbc) et
  [politique de licence COIN-OR](https://www.coin-or.org/faq/).
- [Gurobi — conditions de licence officielles](https://support.gurobi.com/hc/en-us/articles/12684663118993-How-do-I-obtain-a-Gurobi-license).

Les licences de code consultées directement sont MIT pour PackingSolver et
HiGHS, Apache-2.0 pour SCIP et LAFF, BSD pour Choco, EPL-2.0 pour Cbc. Les
licences des binaires et dépendances restent à verrouiller par hash avant tout
essai produit.

## 3. Matrice d'audit initiale

| Candidat | Famille et 3D réel | Licence / Windows / hors ligne | Fidélité BGIG actuelle | Décision L08C |
| --- | --- | --- | --- | --- |
| PackingSolver `box` | packing 3D natif, rotations 3D, bins et certificat | MIT ; build/binaire Windows à vérifier ; local possible | collisions et X/Y/Z : oui ; appuis, accès, réservations et P45 : à adapter ou à refuser | `shortlist-conditional` |
| PackingSolver `box-stacks` | 3D avec colonnes, poids et contraintes de stack | MIT ; mêmes vérifications de distribution | empilement présent, mais piles limitées à une même empreinte XY : insuffisant seul pour les appuis BGIG généraux | `specialized-only` |
| LAFF / 3d-bin-container-packing | 3D par niveaux, placements, obstacles, contrôles extensibles | Apache-2.0 ; Java/Maven ; exécution Windows possible avec runtime local embarqué à chiffrer | étages et support : prometteurs ; accès, réservations et P45 demandent des contrôles testés | `shortlist-conditional` |
| OR-Tools CP-SAT | CP à formulation complète, variables entières et contraintes reifiées | Apache-2.0 ; paquets/build Windows à verrouiller ; local possible | peut exprimer le contrat complet, mais pas comme primitive 3D prête à l'emploi : modèle pairwise et coût à mesurer | `shortlist-conditional` |
| SCIP | CIP/MIP, formulation complète et contrôle fin | Apache-2.0 ; binaires x64 Windows officiels ; local possible | peut exprimer le contrat complet, avec formulation linéaire/disjonctive à construire | `shortlist-conditional` |
| HiGHS | MIP générique | MIT ; Windows et hors ligne confirmés | peut servir de contrôle MIP, mais aucun adaptateur 3D fidèle n'existe ; lane 2D quarantinée | `control-only` |
| Choco Solver | CP générique | BSD ; Java 17 requis, donc runtime local à emballer | expressif, mais aucune primitive BGIG 3D ni passerelle Python prête | `reserve-conditional` |
| Cbc | MIP générique | EPL-2.0 ; Windows annoncé ; dépendances à auditer | formulation possible mais licence/dépendances ne passent pas le filtre produit actuel | `rejected-license-gate` |
| Gurobi | MIP commercial mature | licence utilisateur ou commerciale obligatoire | techniquement expressif, mais compte/clé/licence incompatible avec le produit hors ligne redistribuable | `rejected-license-gate` |

## 4. Ce que l'audit établit réellement

1. Trois familles réellement distinctes peuvent entrer dans le tournoi : packing
   3D spécialisé (PackingSolver), construction par niveaux (LAFF), et
   contraintes complètes (OR-Tools CP-SAT ou SCIP).
2. LAFF est le candidat le plus direct pour une première solution constructive
   3D, mais sa qualité ne doit pas être confondue avec une preuve d'accès ou de
   support BGIG.
3. OR-Tools et SCIP sont les témoins de fidélité : ils peuvent porter les règles
   qui manquent aux solveurs spécialisés, au prix probable d'un coût élevé sur
   les gros cas.
4. HiGHS n'est pas éliminé comme contrôle de formulation, mais il ne revient pas
   dans Auto et ne compte pas comme concurrent 3D tant qu'un adapter complet ne
   passe pas les contrôles exacts.

## 5. Filtres avant tout build ou téléchargement

P64-L08D/E ne téléchargera ou construira un candidat que si sa fiche verrouille
explicitement : version et commit, licence du code et du binaire, dépendances,
taille, architecture Windows x64, exécution sans réseau, absence de compte,
secret ou télémétrie, et procédure de suppression locale. Les moteurs Java ne
passent que s'ils peuvent utiliser un runtime local au workspace : aucune
installation globale n'est admise.

## 6. Suite imposée

P64-L08D crée le corpus adversarial T0/T1 et son holdout neuf. P64-L08E teste
alors seulement les candidats `shortlist-conditional` avec une matrice de
traduction règle par règle. Toute règle perdue donne `unsupported` ; elle ne
sera jamais simulée par une projection 2D ou par un commentaire d'adapter.
