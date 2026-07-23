# P64-L05B — Preuve SolverCaseBundle et capture DEV

## Resultat

Statut : implemented-core, implemented-fusion-bridge,
implemented-fusion-ui, automated-validated.

fusion-validated: false. print-validated: false.

P64-L05B livre une capture locale explicite et versionnee des cas solveur. Le
bundle conserve les faits utiles a la reproduction et au futur travail
d'amelioration, mais ne modifie pas l'algorithme et ne declenche aucune operation
de domaine.

## Fichiers runtime

- `src/board_game_insert_generator/solver_case_bundle.py` ;
- `src/board_game_insert_generator/staged_calculation.py` ;
- `fusion_addin/BoardGameInsertGenerator/palette_project.py` ;
- `fusion_addin/BoardGameInsertGenerator/palette.html`.

## Preuves fonctionnelles

### Producteur pur

Les tests demontrent :

- determinisme du bundle et de tous ses digests a entrees identiques ;
- normalisation du projet et conservation des reglages solveur ;
- export complet des frontieres P45, variantes, cavites, provenance, couts,
  certificats, budgets, caps et rejets ;
- conservation d'un etat staged positif ou negatif et du dernier partitionnement
  observe ;
- trace semantique limitee aux 256 evenements les plus recents ;
- filtrage des valeurs saisies et chemins clients ;
- refus fail-closed d'une trace mal formee ou d'une cle assimilable a un secret ;
- resume bridge compact distinct du bundle complet.

### Snapshot staged

`solver_case_snapshot()` expose l'etat staged, la partition observee et le plan
minimal courant sans appeler solveur, finaliseur, CAD ou Fusion. Un plan certifie
calcule reste identifiable par le meme digest dans le snapshot.

### Bridge

Un scenario bridge calcule d'abord un petit plan certifie, puis capture le cas
en interdisant par mocks :

- `calculate_layout` ;
- `finalize_volume` ;
- `select_materializable_artifact` ;
- `build_partition_cad`.

La capture reussit, ecrit atomiquement un fichier sous `solver-cases`, restitue
un resume et garde le plan certifie observe. Aucun fichier temporaire ne reste.
Les champs `value`, `password` et les valeurs `C:/private/...` ne survivent pas.

### Palette DOM

Le bouton `DEV · Capturer le cas` est rouge, visible et adjacent a
`Calculer l'agencement minimal`. La palette :

- journalise uniquement action, champ UI, objet, revision, sequence et temps ;
- borne la trace a 256 evenements ;
- bloque uniquement une seconde capture deja en cours ;
- transmet l'identite allowlistee de la scene ;
- n'affiche ni pourcentage, ni ETA, ni apprentissage fictif, ni bouton Annuler.

## Validations ciblees

- producteur pur : 3/3 ;
- producteur d'activite et anti-doublon : 6/6 ;
- orchestration staged : 12/12 ;
- bridge palette : 26/26 ;
- DOM palette : 37/37 ;
- Ruff cible : OK ;
- py_compile cible : OK ;
- syntaxe JavaScript extraite : OK.

## Validations finales

- suite complete : 667/667 en 154,990 s ;
- compileall coeur et add-in : OK ;
- frontiere adsk du coeur pur : OK ;
- `git diff --check` : OK.

## Invariants observes

- global_solver_invocation_count : 0 ;
- finalization_invocation_count : 0 ;
- cad_build_invocation_count : 0 ;
- fusion_materialization_invocation_count : 0 ;
- interaction_values_captured : false ;
- document_paths_captured : false ;
- automatic_solver_modification : false.

## Limites honnetes

- aucune observation Fusion du bouton dans ce lot ;
- aucune capture du projet personnel `Mon insert.bgig.json` n'est commitee ni
  utilisee comme fixture ;
- aucun replay automatique de bundle ;
- aucun plan temoin persistant ni warm start depuis zero ;
- aucune modification du solveur, de ses lanes, budgets ou deadlines ;
- aucune nouvelle revendication sur le cas dense 11 x 34 ;
- manifest Fusion inchange a 0.1.58.

P64-L05C porte le witness certifie persistant et le warm start fail-closed.
P64-L05D portera ensuite le corpus, les mesures et les optimisations de lanes.

## Correctif P64-L05V-R1 (2026-07-23)

La premiere sequence reelle a montre que la requete de capture resynchronisait la session avant de construire le bundle et pouvait remplacer le rapport de transition par `dependencies_unchanged`. Le bridge fige maintenant `solver_case_snapshot` avant cette resynchronisation. Un test reproduit un refus global-void et exige l egalite exacte du rapport stocke. Suite complete : 682/682. Le schema v1 et les invariants d absence d effet restent inchanges.
