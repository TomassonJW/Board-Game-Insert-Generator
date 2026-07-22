# P64-L05C - Preuve temoin certifie persistant

## Resultat

Statut : implemented-core, implemented-fusion-bridge,
implemented-fusion-ui, automated-validated.

fusion-validated: false. print-validated: false.

P64-L05C livre un sidecar local exact et un warm start recertifie. Il permet de
conserver un plan connu apres fermeture de session ou changement temporaire
d'effort, sans supprimer la recherche courante ni abaisser les certificats.

## Fichiers runtime

- `src/board_game_insert_generator/certified_plan_witness.py` ;
- `src/board_game_insert_generator/minimal_layout_solver.py` ;
- `src/board_game_insert_generator/staged_calculation.py` ;
- `fusion_addin/BoardGameInsertGenerator/palette_project.py` ;
- `fusion_addin/BoardGameInsertGenerator/palette.html`.

## Preuves fonctionnelles

### Producteur pur et sidecar

Les tests demontrent :

- witness identique a entrees identiques ;
- identite exacte sur projet normalise et jeu de frontieres P45 ;
- methode et effort absents de la cle directe ;
- rejet d'un projet ou jeu de frontieres different ;
- rejet d'un payload ou digest modifie ;
- presence du plan, du digest de placements et des axes de classement ;
- remplacement d'un fichier corrompu au prochain solve certifie ;
- ecriture atomique sans fichier temporaire residuel.

### Warm start du solveur

Un plan certifie est d'abord produit normalement. Toutes les lanes sont ensuite
forcees a retourner `no_solution_within_budget` :

- sans witness, le resultat reste `no_solution_within_budget` ;
- avec witness, la geometrie est reconstruite et recertifiee ;
- les lanes forcees sont quand meme appelees ;
- `lane_count_added = 0` et `cache_hit_claimed = false` ;
- le resultat reste `solution_found` avec source `certified_witness` ;
- le certificat final commun est present.

### Approfondi

Le test Deep force aussi les neuf lanes a echouer. Il observe :

- six lanes dans le prefixe Normal ;
- `warm_start.status = not_supplied` pour cette phase ;
- trois lanes dans l'extension Deep ;
- `warm_start.status = accepted` uniquement dans l'extension ;
- neuf appels reels au solveur de lane ;
- conservation du witness recertifie comme solution.

Le contrat L04B reste donc intact : prefixe Normal exact, trois lanes Deep et
meme deadline commune de 30 000 ms.

### Staged et bridge

Le staged transmet explicitement l'incumbent et expose
`fresh_search_with_certified_witness` seulement apres recertification acceptee.
Le bridge prouve :

- stockage d'un witness Rapide ;
- vidage des sessions en memoire ;
- stockage d'un witness Normal dans un autre chemin ;
- retour a Rapide et rechargement du premier fichier ;
- recherche fraiche executee avec witness ;
- preservation du digest pour une geometrie identique ;
- rejet puis remplacement atomique apres corruption du fichier.

### Palette DOM

Un detail replie affiche chargement, stockage, warm start, nombre de
recertifications, poursuite de recherche, absence de cache hit et raisons
d'arret. Les actions, focus, autosave et details replies existants restent
inchanges.

## Validations ciblees

- witness pur et warm start : 4/4 ;
- solveur minimal : 14/14 ;
- staged : 13/13 ;
- bridge palette : 27/27 ;
- DOM palette : 38/38 ;
- Ruff cible : OK ;
- py_compile cible : OK ;
- syntaxe JavaScript extraite : OK.

## Validation finale

- suite complete finale : 674/674 en 152,142 s ;
- compileall coeur et add-in : OK ;
- frontiere adsk du coeur pur : OK ;
- `git diff --check` et staged diff-check : OK avant commit.

## Invariants observes

- witness_recertification_count : 1 lorsqu'accepte ;
- search_continued : true ;
- lane_count_added : 0 ;
- cache_hit_claimed : false ;
- finalization_invocation_count : 0 ;
- fusion_materialization_invocation_count : 0 ;
- prefixe Normal Deep : 6 lanes exactes ;
- extension Deep : 3 lanes exactes.

## Limites honnetes

- aucune observation Fusion de ce lot ;
- aucune capture du projet personnel `Mon insert.bgig.json` n'est commitee ;
- aucun SolverCaseBundle reel n'est encore rejoue automatiquement ;
- aucun nettoyage automatique du repertoire de witnesses ;
- aucune lane, aucun budget et aucune deadline ne sont optimises dans L05C ;
- aucune nouvelle revendication sur le cas dense 11 x 34 ;
- manifest Fusion inchange a 0.1.58.

P64-L05D porte le corpus versionne, le replay borne, les comparaisons et les
optimisations relues du portefeuille.
