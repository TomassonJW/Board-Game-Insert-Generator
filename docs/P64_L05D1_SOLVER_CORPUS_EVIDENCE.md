# P64-L05D1 - Preuve corpus solveur et gate A/B

## Resultat

Statut : implemented-core, automated-validated.

fusion-validated: false. print-validated: false.

P64-L05D1 livre un corpus anonymise, un replay borne et une comparaison A/B
fonctionnelle prioritaire. Le solveur et ses lanes restent inchanges dans ce
sous-lot.

## Corpus initial

Manifest :
`tests/fixtures/p64_l05d_solver_case_corpus.v1.json`.

- 7 cas : 5 CI et 2 extended ;
- 2 baselines `solution_found` certifiees ;
- 5 baselines `no_solution_within_budget`, sans revendication
  d'impossibilite ;
- digest du corpus :
  `409c75095c47c4ca85a6dda469e986d36d67d460bf308ac9a96e1d3898ac26cf` ;
- aucun chemin personnel, `Mon insert`, `AppData` ou checkout utilisateur.

Le tiers CI rejoue cinq cas et produit :

- 2 solutions certifiees ;
- 3 limites de budget honnetes ;
- 0 expectation violee ;
- digest fonctionnel :
  `3aacd2eb29edf4414190bd0622c3b5539b6579430d5800bfbe52cd2419250338`.

Les deux cas extended comprennent une fermeture continue et le cas dense
11 x 34. Leur presence ne change aucun statut produit et n'ajoute aucune
revendication sur le cas dense.

## Producteur pur et validation fail-closed

Les tests demontrent :

- manifest identique a entrees identiques ;
- tri canonique et unicite des identifiants ;
- rejet d'un manifest modifie sans recalcul du digest ;
- validation du digest global et de chaque composant d'un SolverCaseBundle ;
- rejet d'un composant de bundle modifie ;
- exclusion de la trace et du contexte client du cas importe ;
- temps mur absent du digest fonctionnel ;
- rejet d'une perte fonctionnelle meme si le candidat est dix fois plus rapide.

## Scripts de developpement

- `scripts/solver/replay_solver_case_corpus.py` rejoue le manifest ou un bundle
  ephemere et peut ecrire atomiquement un rapport ;
- `scripts/solver/compare_solver_case_replays.py` compare baseline et candidat
  et retourne un code non nul si le candidat est refuse.

Le replay CLI CI et sa self-comparison passent. La self-comparison sert de
controle de plomberie ; une future optimisation doit en plus montrer son gain.

## Observation en lecture seule du cas humain

Le projet personnel indique par Thomas a ete retrouve et rejoue sans ecriture.
Son SHA-256 est reste identique avant et apres l'observation :
`4613C7BB3EA01FA4678640BA4C52C82D46D440FB26313E4239E55D56DD687E15`.

Faits observes :

- 13 groupes conteneurs et 22 contenus dans une boite 200 x 150 x 60 mm ;
- projet normalise :
  `bc2e5d038b0c3b3a72188b35fafa46758e8b65f7325553f6404ec5b77a6d35d0` ;
- Rapide, Normal et Approfondi retournent tous
  `no_solution_within_budget` ;
- Approfondi termine par
  `deep_extension_exhausted_without_incumbent` ;
- aucune des neuf lanes Deep ne produit de completion geometrique ;
- les lanes de variantes atteignent leurs caps d'etats ou d'essais bien avant
  la profondeur 13.

Cette observation confirme une limite reelle de capacite, pas seulement un
message UX. Le fichier personnel et son contenu ne sont ni copies ni committes.
Aucun placement persistant n'etait disponible pour servir d'oracle.

## Validations ciblees

- tests corpus : 5/5 ;
- replay CLI CI : OK ;
- comparaison CLI identique : OK ;
- Ruff cible : OK ;
- format Ruff cible : OK ;
- py_compile cible : OK.

## Validation finale

- suite complete finale : 679/679 en 150,835 s ;
- controle documentaire canonique : OK ;
- frontiere adsk du coeur pur : OK ;
- git diff --check et staged diff-check : OK avant commit.

## Limites honnetes

- corpus initial petit et surtout mecanique ;
- temps mur dependant de la machine, non seuil produit ;
- aucun bundle personnel promu dans le corpus ;
- aucune optimisation du solveur dans L05D1 ;
- aucune observation Fusion de ce lot ;
- manifest Fusion inchange a 0.1.58.

P64-L05D2 porte la premiere optimisation interne, conservee uniquement apres
comparaison A/B sans regression.
