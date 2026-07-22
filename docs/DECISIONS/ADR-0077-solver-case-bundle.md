# ADR-0077 — Capture locale versionnee des cas solveur

## Statut

Acceptee le 2026-07-22 dans le programme correctif P64-L05 explicitement
valide apres le retour humain P64-L04V. Cette decision ouvre P64-L05B. Elle ne
vaut ni validation Fusion, ni validation d'impression, ni autorisation
d'auto-modifier le solveur.

## Contexte

Un projet peut conserver et materialiser un agencement certifie par retouches
incrementales alors qu'une reconstruction depuis zero ne retrouve plus ce plan.
Pour ameliorer le solveur avec des cas reels, il faut capturer les faits qui
rendent l'ecart reproductible : projet normalise, etat staged positif ou negatif,
frontieres locales P45, reglages, budgets, lanes, chronologie semantique et
identite de scene Fusion.

Un journal brut de l'interface fuit facilement des valeurs, des chemins ou des
secrets et reste difficile a rejouer. Une auto-modification du solveur depuis
Fusion serait non deterministe, non auditable et melangerait acquisition de
preuve, entrainement et livraison runtime.

## Options

### A — Journal technique libre

Faible cout initial, mais format instable, donnees potentiellement sensibles et
reproductibilite insuffisante.

### B — Auto-apprentissage immediat depuis la palette

Spectaculaire en apparence, mais non certifiable : une observation utilisateur
ne prouve ni la generalite de l'heuristique, ni l'absence de regression.

### C — SolverCaseBundle explicite, versionne et local

Un producteur pur assemble uniquement des faits deja observes. Un bouton DEV
visible exporte atomiquement ce bundle, sans lancer de solve, finalisation, CAD
ou materialisation. Les evolutions algorithmiques restent relues, testees et
integrees dans le depot.

## Decision

Retenir l'option C pour P64-L05B.

Le schema public est `bgig.solver_case_bundle.v1`. Le bundle contient :

- le projet BGIG normalise et son digest ;
- la methode et l'effort actifs ;
- le snapshot staged, y compris le dernier partitionnement observe meme stale ou
  negatif et le plan minimal courant lorsqu'il existe ;
- l'analyse locale et les frontieres P45 completes avec variantes, provenance,
  couts, certificats, budgets, caps et digests ;
- un journal semantique borne aux 256 evenements les plus recents ;
- une identite de scene Fusion strictement allowlistee ;
- les digests de chaque composant et du bundle complet.

Le journal ne conserve que type d'evenement, action, champ UI, identite d'objet,
revision, sequence et temps ecoule. Il ne capture aucune valeur saisie. Les
chemins de document, secrets et champs assimilables a des secrets sont exclus ou
refuses fail-closed.

Le bouton `DEV · Capturer le cas`, rouge et adjacent a l'action principale,
est explicite. Deux captures identiques simultanees sont bloquees par identite
d'operation ; les autres operations ne sont pas arbitrairement bloquees.

Par defaut, les fichiers sont ecrits sous le stockage utilisateur BGIG dans
`projects/solver-cases/`. L'ecriture est atomique. Le bundle complet ne transite
pas dans la reponse DOM : le bridge retourne seulement son chemin et un resume.

## Invariants

- global_solver_invocation_count = 0 ;
- finalization_invocation_count = 0 ;
- cad_build_invocation_count = 0 ;
- fusion_materialization_invocation_count = 0 ;
- interaction_values_captured = false ;
- document_paths_captured = false ;
- automatic_solver_modification = false.

`stale_or_cancelled` reste un resultat technique fail-closed et ne devient pas
une annulation utilisateur. La capture ne modifie ni projet, ni solveur, ni
scene, ni cache de solution.

## Consequences

### Positives

- les cas limites humains deviennent des artefacts reproductibles et comparables ;
- un succes incremental et un echec depuis zero peuvent coexister dans la meme
  preuve sans etre reinterpretes ;
- P45 et P64 restent separes ;
- les futures heuristiques peuvent etre developpees ici, relues et benchmarkees
  avant toute integration.

### Limites

- L05B ne sait ni rejouer automatiquement un bundle, ni apprendre une heuristique ;
- le journal semantique commence au chargement courant de la palette ;
- aucune capture personnelle n'est versee automatiquement dans le depot ;
- le plan temoin persistant et le warm start appartiennent a L05C ;
- le corpus et l'optimisation des lanes appartiennent a L05D.

## Alternatives refusees

- enregistrer les valeurs de formulaire, chemins locaux ou secrets ;
- modifier automatiquement le code ou les poids d'heuristique depuis Fusion ;
- declencher un solve, une finalisation, une CAD ou une scene pendant la capture ;
- traiter une materialisation humaine comme une preuve universelle de faisabilite ;
- publier un faux pourcentage, une ETA ou un bouton Annuler decoratif.

## Validation

Le contrat executable est `docs/P64_L05B_SOLVER_CASE_BUNDLE_CONTRACT.md`.
La preuve automatisee est `docs/P64_L05B_SOLVER_CASE_BUNDLE_EVIDENCE.md`.

fusion-validated: false, print-validated: false.