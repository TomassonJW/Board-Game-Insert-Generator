# Backlog

Ce backlog decoupe la roadmap en missions courtes, actionnables et verifiables.
Les statuts autorises sont : `todo`, `ready`, `in_progress`, `blocked`, `done`,
`deferred`.

Une mission doit rester assez petite pour etre terminee, testee, documentee et
commitee sans melanger plusieurs decisions structurantes.

## Phase 0 - Fondation projet

### P0-M001 - Installer le systeme de pilotage projet

- Phase liee : Phase 0 - Fondation projet
- Objectif : creer le protocole Codex, la roadmap, le backlog, le statut, les
  prochaines actions, les index ADR/logs et les templates GitHub.
- Livrable attendu : documents de gouvernance utilisables par un futur agent.
- Fichiers probablement concernes : `AGENTS.md`, `README.md`, `docs/*`,
  `.github/*`.
- Criteres d'acceptation : les documents obligatoires existent ; les prochaines
  missions sont explicites ; les regles de mise a jour sont documentees.
- Tests ou verifications : `python -m unittest discover -s tests`, `git diff
  --check`.
- Dependances : aucune.
- Statut : `done`.

### P0-M002 - Ajouter une verification documentaire de base

- Phase liee : Phase 0 - Fondation projet
- Objectif : automatiser un controle simple des liens, fichiers obligatoires et
  sections critiques.
- Livrable attendu : script local ou test qui echoue si un fichier de pilotage
  obligatoire manque.
- Fichiers probablement concernes : `tests/`, `docs/QUALITY_RULES.md`,
  `pyproject.toml`.
- Criteres d'acceptation : la liste des fichiers critiques est testee ; le test
  documente les manques avec un message lisible.
- Tests ou verifications : test unitaire dedie et suite complete.
- Dependances : P0-M001.
- Statut : `ready`.

### P0-M003 - Stabiliser le format des ADR

- Phase liee : Phase 0 - Fondation projet
- Objectif : definir un template ADR utilisable pour les futures decisions.
- Livrable attendu : modele ADR et index mis a jour.
- Fichiers probablement concernes : `docs/DECISIONS/README.md`,
  `docs/DECISIONS/ADR-*.md`.
- Criteres d'acceptation : le template couvre contexte, options, decision,
  consequences et alternatives refusees.
- Tests ou verifications : relecture documentaire.
- Dependances : P0-M001.
- Statut : `ready`.

### P0-M004 - Definir une nomenclature de versions et releases

- Phase liee : Phase 0 - Fondation projet
- Objectif : clarifier comment passer de V0 experimental a releases utilisables.
- Livrable attendu : convention versioning et criteres de release.
- Fichiers probablement concernes : `README.md`, `docs/STATUS.md`,
  `docs/ROADMAP.md`.
- Criteres d'acceptation : chaque version a une definition minimale ; les
  conditions de release sont testables.
- Tests ou verifications : relecture documentaire.
- Dependances : P0-M001.
- Statut : `todo`.

## Phase 1 - Moteur Python pur

### P1-M001 - Consolider les modeles de donnees de base

- Phase liee : Phase 1 - Moteur Python pur
- Objectif : stabiliser `BoxSpec`, `ModuleRequest`, `ToleranceProfile`,
  `Cell` et `PrintableBody` comme contrat interne.
- Livrable attendu : modeles types, invariants documentes et tests de creation
  valides/invalides.
- Fichiers probablement concernes : `src/board_game_insert_generator/models.py`,
  `tests/`, `docs/GEOMETRY_MODEL.md`.
- Criteres d'acceptation : les unites sont explicitement en millimetres ; les
  invariants non evidents sont testes ; les concepts sont alignes avec les docs.
- Tests ou verifications : suite unitaire complete.
- Dependances : P0-M001.
- Statut : `ready`.

### P1-M002 - Durcir le chargement JSON

- Phase liee : Phase 1 - Moteur Python pur
- Objectif : rendre les erreurs de configuration plus precises et couvrir les
  champs inconnus, types invalides et cas limites.
- Livrable attendu : loader JSON robuste avec tests d'erreurs.
- Fichiers probablement concernes : `config_loader.py`, `tests/`,
  `docs/CONFIG_SCHEMA.md`.
- Criteres d'acceptation : chaque erreur majeure retourne un message actionnable
  ; les exemples existants passent.
- Tests ou verifications : tests unitaires loader et CLI.
- Dependances : P1-M001.
- Statut : `ready`.

### P1-M003 - Produire un rapport de validation structure

- Phase liee : Phase 1 - Moteur Python pur
- Objectif : exposer les erreurs et warnings sous forme exploitable par la CLI,
  Fusion 360 et de futurs assistants.
- Livrable attendu : structure de rapport de validation serialisable.
- Fichiers probablement concernes : `validation.py`, `report.py`, `tests/`.
- Criteres d'acceptation : les erreurs conservent un code stable, un champ et un
  message ; le rapport JSON les expose clairement.
- Tests ou verifications : tests unitaires et exemple JSON.
- Dependances : P1-M002.
- Statut : `todo`.

### P1-M004 - Ajouter une commande CLI de diagnostic

- Phase liee : Phase 1 - Moteur Python pur
- Objectif : fournir une boucle courte pour valider config, layout et rapport.
- Livrable attendu : commande CLI documentee avec sortie lisible.
- Fichiers probablement concernes : `cli.py`, `README.md`, `tests/`.
- Criteres d'acceptation : la commande retourne un code non nul en erreur ; la
  documentation donne la commande et le resultat attendu.
- Tests ou verifications : tests CLI et execution d'exemple.
- Dependances : P1-M003.
- Statut : `todo`.

## Phase 2 - Layout rectangulaire simple

### P2-M001 - Formaliser l'interface de strategie de layout

- Phase liee : Phase 2 - Layout rectangulaire simple
- Objectif : preparer plusieurs strategies sans disperser la logique.
- Livrable attendu : contrat interne pour `row_fill`, grille et colonnes.
- Fichiers probablement concernes : `layout.py`, `models.py`, `docs/ARCHITECTURE.md`.
- Criteres d'acceptation : `row_fill` garde son comportement ; l'extension future
  est documentee ; aucun couplage Fusion n'est introduit.
- Tests ou verifications : tests layout existants et nouveaux cas de non-regression.
- Dependances : P1-M001.
- Statut : `ready`.

### P2-M002 - Couvrir les cas limites de `row_fill`

- Phase liee : Phase 2 - Layout rectangulaire simple
- Objectif : tester rotation, retour a la ligne, depassement et priorites.
- Livrable attendu : tests exhaustifs des comportements V0.
- Fichiers probablement concernes : `tests/test_layout_basic.py`, `layout.py`.
- Criteres d'acceptation : les erreurs de placement sont previsibles ; les
  priorites sont stables ; les rotations autorisees sont testees.
- Tests ou verifications : suite unitaire complete.
- Dependances : P2-M001.
- Statut : `ready`.

### P2-M003 - Ajouter une strategie grille explicite

- Phase liee : Phase 2 - Layout rectangulaire simple
- Objectif : produire des cellules regulieres pour jeux simples.
- Livrable attendu : strategie `grid` documentee et testee.
- Fichiers probablement concernes : `layout.py`, `models.py`,
  `docs/GEOMETRY_MODEL.md`, `examples/`.
- Criteres d'acceptation : la grille refuse les dimensions impossibles ; les
  cellules sont reproductibles ; un exemple montre l'usage.
- Tests ou verifications : tests unitaires et rapport exemple.
- Dependances : P2-M001.
- Statut : `todo`.

### P2-M004 - Exporter un resume de layout comparatif

- Phase liee : Phase 2 - Layout rectangulaire simple
- Objectif : comparer plusieurs layouts simples avant generation CAD.
- Livrable attendu : rapport listant strategie, occupation, warnings et score
  basique.
- Fichiers probablement concernes : `report.py`, `layout.py`, `tests/`.
- Criteres d'acceptation : au moins deux strategies peuvent etre comparees ; le
  score reste explicable.
- Tests ou verifications : tests rapport et exemples.
- Dependances : P2-M003.
- Statut : `todo`.

## Phase 3 - Tolerances intelligentes

### P3-M001 - Classifier explicitement les faces

- Phase liee : Phase 3 - Tolerances intelligentes
- Objectif : separer faces peripheriques, voisines, libres, internes et
  fonctionnelles.
- Livrable attendu : modele de classification de faces teste.
- Fichiers probablement concernes : `tolerance.py`, `models.py`,
  `docs/TOLERANCE_MODEL.md`.
- Criteres d'acceptation : chaque face a une raison d'offset ; les rapports
  exposent les classifications.
- Tests ou verifications : tests unitaires de voisinage et offsets.
- Dependances : P2-M002.
- Statut : `ready`.

### P3-M002 - Ajouter des profils d'impression

- Phase liee : Phase 3 - Tolerances intelligentes
- Objectif : permettre des presets PLA/PETG/rapide/fin sans cacher les valeurs.
- Livrable attendu : profils resolus en `ToleranceProfile` explicite.
- Fichiers probablement concernes : `models.py`, `config_loader.py`,
  `docs/TOLERANCE_MODEL.md`.
- Criteres d'acceptation : un profil peut etre surcharge champ par champ ; le
  rapport montre les valeurs finales.
- Tests ou verifications : tests loader, validation et rapport.
- Dependances : P3-M001.
- Statut : `todo`.

### P3-M003 - Ajouter un protocole de calibration physique

- Phase liee : Phase 3 - Tolerances intelligentes
- Objectif : documenter comment valider les jeux par impression reelle.
- Livrable attendu : guide de coupons de test et tableau de resultats.
- Fichiers probablement concernes : `docs/QUALITY_RULES.md`,
  `docs/TOLERANCE_MODEL.md`, `examples/`.
- Criteres d'acceptation : le protocole distingue theorie, impression et
  ajustements.
- Tests ou verifications : relecture documentaire.
- Dependances : P3-M002.
- Statut : `todo`.

## Phase 4 - Generation Fusion 360 de blanks

### P4-M001 - Definir le contrat de representation intermediaire CAD

- Phase liee : Phase 4 - Generation Fusion 360 de blanks
- Objectif : decrire les objets que l'adaptateur Fusion recevra.
- Livrable attendu : modele de donnees CAD-agnostic documente.
- Fichiers probablement concernes : `models.py`, `docs/ARCHITECTURE.md`,
  `docs/FUSION_360_STRATEGY.md`.
- Criteres d'acceptation : le contrat ne depend pas de `adsk` ; les blanks
  rectangulaires sont representables.
- Tests ou verifications : tests serialization si code ajoute.
- Dependances : P1-M003, P3-M001.
- Statut : `todo`.

### P4-M002 - Creer un squelette d'adaptateur Fusion 360

- Phase liee : Phase 4 - Generation Fusion 360 de blanks
- Objectif : isoler l'integration Fusion sans polluer le coeur Python.
- Livrable attendu : repertoire d'adaptateur avec documentation d'installation.
- Fichiers probablement concernes : `fusion/` ou `src/.../fusion_adapter/`,
  `docs/FUSION_360_STRATEGY.md`.
- Criteres d'acceptation : le coeur Python reste importable sans Fusion ; le
  squelette explique comment tester hors Fusion.
- Tests ou verifications : suite coeur Python ; verification d'import.
- Dependances : P4-M001.
- Statut : `todo`.

### P4-M003 - Generer des blanks rectangulaires Fusion

- Phase liee : Phase 4 - Generation Fusion 360 de blanks
- Objectif : creer composants, corps rectangulaires, noms et rayons simples.
- Livrable attendu : script ou add-in Fusion capable de generer les blanks V0.
- Fichiers probablement concernes : adaptateur Fusion, exemples, docs.
- Criteres d'acceptation : une config valide produit des composants inspectables
  ; aucun layout n'est recalcule dans Fusion.
- Tests ou verifications : test coeur Python et verification manuelle Fusion
  documentee avec captures ou notes.
- Dependances : P4-M002.
- Statut : `todo`.

## Phase 5 - Cavites et receptacles

### P5-M001 - Modeliser les cavites simples

- Phase liee : Phase 5 - Cavites et receptacles
- Objectif : representer les volumes retires d'un module.
- Livrable attendu : `Cavity` enrichi, documentation et tests.
- Fichiers probablement concernes : `models.py`, `docs/GEOMETRY_MODEL.md`,
  `tests/`.
- Criteres d'acceptation : une cavite a dimensions, origine, type fonctionnel et
  clearance ; elle ne rend pas les parois invalides.
- Tests ou verifications : tests de validation et rapport.
- Dependances : P4-M001.
- Statut : `todo`.

### P5-M002 - Ajouter logements de cartes et cartes sleevees

- Phase liee : Phase 5 - Cavites et receptacles
- Objectif : generer les cavites de decks avec jeux specifiques.
- Livrable attendu : receptecle cartes documente et testable.
- Fichiers probablement concernes : `models.py`, `validation.py`, `tolerance.py`,
  `docs/TOLERANCE_MODEL.md`.
- Criteres d'acceptation : les cartes et cartes sleevees ont des jeux distincts ;
  les parois minimales sont verifiees.
- Tests ou verifications : tests unitaires et exemple de config.
- Dependances : P5-M001.
- Statut : `todo`.

### P5-M003 - Ajouter bacs a tokens, des et meeples

- Phase liee : Phase 5 - Cavites et receptacles
- Objectif : couvrir les receptacles ouverts simples.
- Livrable attendu : primitives de cavites pour tokens/des/meeples.
- Fichiers probablement concernes : `models.py`, `validation.py`, `examples/`,
  docs.
- Criteres d'acceptation : chaque type a un jeu explicite ; les warnings signalent
  les formes irregulieres.
- Tests ou verifications : tests et rapport exemple.
- Dependances : P5-M001.
- Statut : `todo`.

### P5-M004 - Ajouter encoches de doigts et fonds arrondis

- Phase liee : Phase 5 - Cavites et receptacles
- Objectif : ameliorer l'ergonomie des cavites.
- Livrable attendu : features abstraites pour finger notch et rounded floor.
- Fichiers probablement concernes : `models.py`, adaptateur CAD futur,
  `docs/GEOMETRY_MODEL.md`.
- Criteres d'acceptation : les features sont CAD-agnostic ; Fusion pourra les
  mapper plus tard.
- Tests ou verifications : tests de serialization ou rapport.
- Dependances : P5-M002, P5-M003.
- Statut : `todo`.

## Phase 6 - Modules composites

### P6-M001 - Representer les modules composites par primitives soudees

- Phase liee : Phase 6 - Modules composites
- Objectif : formaliser les modules en L, T et volumes multi-primitives.
- Livrable attendu : representation interne et validation des primitives.
- Fichiers probablement concernes : `models.py`, `validation.py`,
  `docs/GEOMETRY_MODEL.md`.
- Criteres d'acceptation : les primitives internes peuvent se toucher sans jeu ;
  les overlaps invalides sont detectes.
- Tests ou verifications : tests de validation geometrique.
- Dependances : P3-M001.
- Statut : `todo`.

### P6-M002 - Appliquer les tolerances uniquement aux faces exposees

- Phase liee : Phase 6 - Modules composites
- Objectif : eviter les jeux internes dans les modules soudes.
- Livrable attendu : algorithme d'exposition de faces.
- Fichiers probablement concernes : `tolerance.py`, `models.py`, tests,
  `docs/TOLERANCE_MODEL.md`.
- Criteres d'acceptation : une jonction interne ne recoit aucun offset ; les faces
  externes restent tolerancees.
- Tests ou verifications : tests unitaires modules L/T.
- Dependances : P6-M001.
- Statut : `todo`.

### P6-M003 - Generer les unions Fusion pour composites simples

- Phase liee : Phase 6 - Modules composites
- Objectif : convertir les primitives composites en corps soudes.
- Livrable attendu : generation Fusion de modules L/T simples.
- Fichiers probablement concernes : adaptateur Fusion, exemples, docs.
- Criteres d'acceptation : un module composite inspectable est genere ; les faces
  internes ne creent pas de separation.
- Tests ou verifications : tests coeur et verification Fusion documentee.
- Dependances : P6-M002, P4-M003.
- Statut : `todo`.

## Phase 7 - Couvercles et mecanismes

### P7-M001 - Modeliser les couvercles poses

- Phase liee : Phase 7 - Couvercles et mecanismes
- Objectif : ajouter des couvercles simples avec jeu vertical.
- Livrable attendu : modele de lid et contraintes fonctionnelles.
- Fichiers probablement concernes : `models.py`, `validation.py`,
  `docs/TOLERANCE_MODEL.md`.
- Criteres d'acceptation : le jeu de couvercle est explicite ; le rapport separe
  module et couvercle.
- Tests ou verifications : tests de validation et rapport.
- Dependances : P5-M001.
- Statut : `todo`.

### P7-M002 - Ajouter couvercles coulissants et rainures

- Phase liee : Phase 7 - Couvercles et mecanismes
- Objectif : produire des interfaces fonctionnelles avec jeux dedies.
- Livrable attendu : representation abstraite de rail/rainure/languette.
- Fichiers probablement concernes : `models.py`, `tolerance.py`,
  `docs/FUSION_360_STRATEGY.md`.
- Criteres d'acceptation : les jeux de coulissement sont distincts des jeux de
  module ; les parois minimales sont controlees.
- Tests ou verifications : tests unitaires et prototype documente.
- Dependances : P7-M001.
- Statut : `todo`.

### P7-M003 - Explorer charnieres et clips simples

- Phase liee : Phase 7 - Couvercles et mecanismes
- Objectif : cadrer les mecanismes plus risques avant implementation.
- Livrable attendu : ADR ou note de recherche avec options et risques.
- Fichiers probablement concernes : `docs/DECISIONS/`, `docs/TOLERANCE_MODEL.md`.
- Criteres d'acceptation : aucune implementation fragile n'est lancee sans
  criteres d'impression.
- Tests ou verifications : revue documentaire.
- Dependances : P7-M002, P3-M003.
- Statut : `todo`.

## Phase 8 - Surcouche esthetique

### P8-M001 - Definir le langage visuel parametrique

- Phase liee : Phase 8 - Surcouche esthetique
- Objectif : separer fonction, ergonomie et decoration.
- Livrable attendu : specification des labels, motifs, coins et ajourages.
- Fichiers probablement concernes : `docs/PRODUCT_SPEC.md`,
  `docs/GEOMETRY_MODEL.md`.
- Criteres d'acceptation : les options esthetiques ne modifient pas les volumes
  fonctionnels sans signalement.
- Tests ou verifications : relecture documentaire.
- Dependances : P5-M004.
- Statut : `todo`.

### P8-M002 - Ajouter texte, labels et gravure

- Phase liee : Phase 8 - Surcouche esthetique
- Objectif : permettre l'identification des modules.
- Livrable attendu : features abstraites de texte/gravure/embossage.
- Fichiers probablement concernes : `models.py`, adaptateur Fusion, docs.
- Criteres d'acceptation : texte et profondeur sont parametres ; aucun label ne
  casse la geometrie minimale.
- Tests ou verifications : tests modele et verification Fusion future.
- Dependances : P8-M001, P4-M003.
- Statut : `todo`.

### P8-M003 - Ajouter textures, motifs et ajourages simples

- Phase liee : Phase 8 - Surcouche esthetique
- Objectif : reduire filament ou donner un style parametrique.
- Livrable attendu : representation CAD-agnostic des patterns autorises.
- Fichiers probablement concernes : `models.py`, `docs/QUALITY_RULES.md`.
- Criteres d'acceptation : les patterns respectent une epaisseur minimale ; ils
  peuvent etre desactives.
- Tests ou verifications : tests de validation.
- Dependances : P8-M001.
- Statut : `todo`.

## Phase 9 - Assistant de conception

### P9-M001 - Definir le modele d'assets utilisateur

- Phase liee : Phase 9 - Assistant de conception
- Objectif : distinguer asset, intention, contrainte et module propose.
- Livrable attendu : specification de donnees pour assets de jeu.
- Fichiers probablement concernes : `docs/PRODUCT_SPEC.md`,
  `docs/CONFIG_SCHEMA.md`, `models.py`.
- Criteres d'acceptation : les assets ne sont pas confondus avec les modules ;
  les intentions de setup sont representees.
- Tests ou verifications : tests si modele code.
- Dependances : P5-M003.
- Statut : `todo`.

### P9-M002 - Proposer plusieurs variantes de layout

- Phase liee : Phase 9 - Assistant de conception
- Objectif : generer des alternatives reproductibles.
- Livrable attendu : moteur de variantes avec scoring simple.
- Fichiers probablement concernes : `layout.py`, `report.py`, docs.
- Criteres d'acceptation : chaque variante indique compacite, ergonomie,
  imprimabilite et warnings.
- Tests ou verifications : tests deterministes de scoring.
- Dependances : P2-M004, P9-M001.
- Statut : `todo`.

### P9-M003 - Ajouter une boucle d'assistance explicable

- Phase liee : Phase 9 - Assistant de conception
- Objectif : aider l'utilisateur a choisir sans boite noire.
- Livrable attendu : rapport de recommendation et raisons de choix.
- Fichiers probablement concernes : `report.py`, docs, future UI.
- Criteres d'acceptation : chaque recommendation cite les contraintes utilisees
  ; les hypotheses restent visibles.
- Tests ou verifications : tests de rapport.
- Dependances : P9-M002.
- Statut : `todo`.

## Phase 10 - Packaging produit

### P10-M001 - Creer des exemples reels complets

- Phase liee : Phase 10 - Packaging produit
- Objectif : fournir des cas d'usage de bout en bout.
- Livrable attendu : plusieurs configs documentees et rapports attendus.
- Fichiers probablement concernes : `examples/`, `README.md`, docs.
- Criteres d'acceptation : chaque exemple explique ses dimensions et limites ;
  les rapports sont reproductibles.
- Tests ou verifications : execution de tous les exemples.
- Dependances : P5-M003, P4-M003.
- Statut : `todo`.

### P10-M002 - Definir le processus de release stable

- Phase liee : Phase 10 - Packaging produit
- Objectif : rendre les versions distribuables.
- Livrable attendu : checklist release, changelog et criteres de qualite.
- Fichiers probablement concernes : `README.md`, `docs/QUALITY_RULES.md`,
  fichiers GitHub.
- Criteres d'acceptation : une release indique ce qui est implemente, experimental
  et a valider par impression.
- Tests ou verifications : checklist release executee.
- Dependances : P0-M004.
- Statut : `todo`.

### P10-M003 - Preparer la distribution utilisateur

- Phase liee : Phase 10 - Packaging produit
- Objectif : permettre installation, usage et support reproductibles.
- Livrable attendu : paquet Python ou distribution documentee, guide utilisateur
  et support d'exemples.
- Fichiers probablement concernes : `pyproject.toml`, `README.md`, docs.
- Criteres d'acceptation : un utilisateur peut installer, lancer un exemple et
  comprendre les limites.
- Tests ou verifications : installation locale propre et suite complete.
- Dependances : P10-M001, P10-M002.
- Statut : `todo`.
