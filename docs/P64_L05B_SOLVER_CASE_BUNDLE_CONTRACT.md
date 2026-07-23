# P64-L05B — Contrat SolverCaseBundle et capture DEV

## Statut

Contrat implemente et valide automatiquement le 2026-07-22.
ADR normative : ADR-0077.

fusion-validated: false. print-validated: false.

## But

Transformer un cas limite observe dans la palette Fusion en artefact local,
versionne, deterministe et exploitable pour le diagnostic puis les futures
ameliorations du solveur, sans presenter la capture comme un entrainement et sans
declencher d'operation de domaine.

## Producteur pur

Identite :

- schema : `bgig.solver_case_bundle.v1` ;
- trace : `bgig.solver_case_event_trace.v1` ;
- producteur : `solver_case_capture_v1`, version `1` ;
- fonction : `build_solver_case_bundle`.

Le producteur accepte uniquement des faits deja calcules : projet, reglages,
snapshot staged, analyse locale, frontieres de variantes, evenements semantiques,
contexte client allowliste et identite de capture. A entree identique, le bundle
et son digest sont identiques.

Il normalise le projet, copie les faits, trie les frontieres et variantes de
facon stable, calcule les digests de composants, rejette les cles assimilables a
des secrets puis calcule le digest du bundle complet.

## Contenu obligatoire

- capture_id, captured_at_ms, source_revision, producteur et version ;
- projet normalise et source de normalisation ;
- methode et effort solveur ;
- staged_calculation ;
- observed_partition, y compris quand il n'est plus courant ;
- current_minimal_partition s'il est encore certifie et courant ;
- analyse contextuelle locale P45 ;
- frontieres P45 completes, variantes, cavites, couts, certificats, provenance,
  budgets, caps, compteurs, digests et rejets ;
- trace semantique bornee ;
- presence et identite allowlistee de la scene ;
- resume positif ou negatif et invariants d'absence d'effet.

## Trace semantique

La palette conserve au plus 256 evenements recents. Les champs autorises sont :

- event_type ;
- action ;
- ui_field ;
- object_id ;
- sequence ;
- source_revision ;
- elapsed_ms.

Les valeurs de formulaire, noms de fichiers selectionnes, chemins de documents,
contenus importes, mots de passe, jetons et secrets ne sont pas captures. Les
champs inconnus sont ignores ; les evenements mal formes sont refuses.

## Lifecycle et anti-double-lancement

Le bouton rouge `DEV · Capturer le cas` est toujours visible a cote de
`Calculer l'agencement minimal`. L'action bridge est `capture_solver_case`.

Une capture en cours bloque uniquement une seconde capture du meme type et
conserve l'identite de la premiere operation. Elle ne bloque pas arbitrairement
un calcul, une sauvegarde ou une autre operation differente.

A succes, la palette annonce `Cas solveur capture` puis le chemin du bundle et
vide le journal deja consomme. Aucun pourcentage, ETA ou controle Annuler n'est
affiche.

## Persistance locale

L'ecriture est atomique dans le repertoire `solver-cases` adjacent au projet
local courant. Le nom contient le slug projet, l'horodatage explicite et les
12 premiers caracteres du digest. Le bridge renvoie un resume compact ; le
bundle complet reste dans le fichier local.

Aucun fichier de projet personnel n'est modifie ou ajoute au depot. La capture
n'est pas un autosave du projet.

## Invariants d'absence d'effet

La capture :

- n'appelle pas le portefeuille ou le solveur global ;
- ne finalise aucun plan ;
- ne construit aucune CAD IR ;
- ne materialise ni ne regenere aucune scene Fusion ;
- ne modifie aucune lane, aucun budget, aucune geometrie et aucun classement ;
- ne modifie pas automatiquement l'algorithme ;
- ne transforme pas stale_or_cancelled en annulation utilisateur.

Les compteurs correspondants valent zero dans le bundle.

## Frontiere P45 / P64

P45 reste proprietaire des variantes et certificats locaux exportes. P64 reste
proprietaire du plan global, de son resultat solveur et de sa provenance. L05B
ne reinterprete ni l'un ni l'autre ; il les fige comme preuves observees.

## Validation minimale

- tests purs : determinisme, contenu, digests, filtrage, bornage et fail-closed ;
- test staged du snapshot sans operation ;
- test bridge d'ecriture atomique avec solve, finalisation et CAD interdits ;
- test DOM du bouton rouge, du journal allowliste et de l'anti-doublon ;
- suite complete ;
- Ruff cible, py_compile, compileall, syntaxe JavaScript, frontiere adsk et
  `git diff --check`.

## Hors scope

- replay automatique d'un bundle ;
- plan temoin persistant ou warm start L05C ;
- corpus versionne, apprentissage de lanes ou optimisation L05D ;
- modification du cas dense 11 x 34 ;
- nouvelle revendication fusion-validated ou print-validated.

## Correctif P64-L05V-R1 - fidelite de transition

Le bridge fige le `solver_case_snapshot` avant la resynchronisation technique de la requete DEV. Le rapport de transition qui a produit le message visible reste donc celui du bundle ; une synchronisation sans changement ne peut pas le remplacer par `dependencies_unchanged`.

Ce correctif ne change ni le schema v1, ni le producteur pur, ni le solveur, ni les budgets. Il rend executable l exigence existante : capturer des faits deja observes sans les recalculer.
