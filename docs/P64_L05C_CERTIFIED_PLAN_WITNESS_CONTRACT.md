# P64-L05C - Contrat temoin certifie persistant

## Statut

Contrat implemente et valide automatiquement le 2026-07-22.
ADR normative : ADR-0078.

fusion-validated: false. print-validated: false.

## But

Conserver localement un plan minimal deja certifie et le proposer comme incumbent
lors d'une reconstruction compatible depuis zero, sans transformer cette preuve
en source projet, cache hit, lane supplementaire ou raccourci de certification.

## Producteur pur

Identite :

- schema : `bgig.certified_plan_witness.v1` ;
- producteur : `certified_minimal_plan_witness_v1`, version `1` ;
- fonctions : `certified_plan_witness_identity`,
  `build_certified_plan_witness`, `validate_certified_plan_witness`.

A projet normalise, frontieres P45 et partition identiques, le witness et son
digest sont identiques. Le producteur refuse toute partition qui ne porte pas le
resultat `solution_found`, le statut construit et les certificats minimal/global
attendus.

## Identite et coexistence

La compatibilite requiert simultanement :

- le digest exact du projet normalise ;
- tous les couples `(container_group_id, frontier_digest)` P45, tries et uniques ;
- le digest du jeu de frontieres exact.

Effort et methode ne sont pas des cles directes. Un changement de methode qui
conserve les memes dependances peut donc reutiliser le witness apres
recertification. Des efforts produisant des frontieres differentes possedent des
sidecars differents et coexistent sans ecrasement.

Une modification du projet, d'un groupe, d'une variante ou d'un digest P45 rend
le fichier incompatible. Aucun fuzzy matching n'est permis.

## Persistance

Le bridge ecrit atomiquement :

`<BGIG_USER_DATA_DIR>/certified-witnesses/witness-<compatibility_digest>.bgig.json`

ou, par defaut, le repertoire equivalent adjacent au projet BGIG local courant.

Le fichier conserve :

- identite, schema, producteur, version et witness_digest ;
- partition minimale complete ;
- plan_digest et digest des placements ;
- axes lexicographiques de classement ;
- famille/version solveur et effort source ;
- invariants de recertification et d'absence d'effet.

Un fichier illisible, tronque, modifie ou incompatible est rejete. Apres un solve
certifie, il est remplace atomiquement. Une geometrie identique conserve le
witness deja stocke. Pour deux geometries distinctes, le witness existant est
conserve s'il est au moins aussi bon selon les axes de classement communs.

## Warm start et certificat

Le bridge ne transmet la partition que si la validation de sidecar est acceptee.
Le solveur :

1. reconstruit les placements typiques et les espaces libres ;
2. rejoue le certificat commun sur le probleme et les frontieres courants ;
3. rejette fail-closed toute geometrie invalide ;
4. ajoute le candidat recertifie a la liste des propositions comme incumbent ;
5. execute toutes les lanes planifiees ;
6. reclasse tous les candidats et rejoue le certificat final commun.

Le witness n'ajoute aucune lane et ne modifie aucun cap. Sa pseudo-identite
`certified_witness_incumbent` sert uniquement a la provenance du candidat.

## Approfondi anytime

Pour `deep` :

- les six lanes Normal exactes s'executent d'abord sans witness ;
- seules les trois lanes d'extension Deep recoivent l'incumbent recertifie ;
- la deadline partagee de 30 000 ms reste inchangee ;
- un witness valide peut fournir le premier incumbent Deep si Normal echoue ;
- la selection finale conserve ou ameliore l'incumbent selon le classement
  historique.

## Observabilite

Le producteur staged, le bridge et la palette exposent :

- statut de chargement et de stockage ;
- raisons d'absence, rejet, acceptation ou conservation ;
- digests de compatibilite, witness, plan et placements ;
- nombre de recertifications ;
- `search_continued`, `lane_count_added` et `cache_hit_claimed` ;
- source du resultat `fresh_search_with_certified_witness` ;
- phase Normal/Deep, lanes, budgets, temps, provenance et raison d'arret existants.

Les details restent replies par defaut. Aucun pourcentage ni ETA n'est invente.

## Invariants d'absence d'effet

- aucun solve global automatique lors d'une edition ;
- aucune finalisation, CAD IR ou materialisation Fusion automatique ;
- aucune nouvelle lane, aucun nouveau budget, aucune deadline modifiee ;
- aucune modification des geometries, schemas projet, defaults ou tolerances ;
- aucune assimilation a un cache hit ou a une annulation utilisateur ;
- aucune auto-modification du solveur ;
- aucune nouvelle revendication sur le cas dense 11 x 34.

## Validation minimale

- producteur pur : determinisme, identite exacte, corruption et rejet fail-closed ;
- solveur : recertification, lanes toujours executees et conservation si elles
  echouent ;
- Deep : prefixe Normal sans witness puis extension avec witness ;
- staged : transmission et source de resultat observable ;
- bridge : ecriture atomique, coexistence des efforts, rechargement apres remise
  a zero des sessions et remplacement d'un fichier corrompu ;
- DOM : details replies et messages honnetes ;
- suite complete, Ruff cible, py_compile, compileall, syntaxe JavaScript,
  frontiere adsk et `git diff --check`.

## Hors scope

- replay des SolverCaseBundle et corpus versionne L05D ;
- modification ou optimisation des lanes ;
- apprentissage automatique ou auto-edition de code ;
- import automatique de `Mon insert.bgig.json` ;
- nettoyage automatique des sidecars ;
- nouvelle gate Fusion ou impression.
