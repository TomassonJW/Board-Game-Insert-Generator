# Quality Rules

## Regles de conception

- Toutes les dimensions sont en millimetres.
- Les axes X, Y et Z doivent rester explicites.
- Le moteur pur ne depend pas de Fusion 360.
- Le JSON n'est pas le modele interne.
- Les tolerances ne sont pas codees en dur dans le layout.
- Les cellules theoriques ne sont pas des corps imprimables.
- Une strategie de layout reservee ne doit pas etre acceptee tant qu'elle n'est
  pas implementee et testee.
- Les modules composites ne recoivent pas de jeu entre primitives internes
  soudees.
- Les valeurs de tolerance doivent rester visibles et ajustables.

## Regles de code

- Preferer des dataclasses typees et lisibles.
- Garder les erreurs comprehensibles pour un utilisateur technique.
- Tester le moteur hors Fusion.
- Eviter les dependances externes tant que la V0 n'en a pas besoin.
- Ne pas introduire de framework structurant sans ADR.
- Garder les fonctions petites et deterministes.
- Ne pas importer Fusion 360 dans le coeur Python.

## Regles de configuration

- Aucun secret dans le depot.
- Les exemples doivent etre realistes mais non lies a des donnees sensibles.
- Les valeurs par defaut doivent etre prudentes.
- Les champs optionnels doivent avoir un comportement documente.
- Les unites doivent etre explicites.

## Regles de validation

- Refuser les dimensions negatives ou nulles.
- Refuser une hauteur utile incoherente avec la boite.
- Refuser les quantites nulles.
- Signaler les layouts impossibles avec un message lisible.
- Ne jamais pretendre qu'un layout actuel est optimal.
- Distinguer erreur bloquante et warning.

## Regles de documentation

- Distinguer ce qui est implemente, experimental, prevu ou a valider par
  impression reelle.
- Documenter toute decision structurante par ADR.
- Garder les documents exploitables par un autre developpeur ou agent.
- Eviter la documentation decorative.
- Mettre a jour `docs/STATUS.md` apres toute mission significative.
- Mettre a jour `docs/BACKLOG.md` si une carte change ou si une tache est
  decouverte.
- Mettre a jour `docs/NEXT_ACTIONS.md` a la fin de chaque mission.
- Ajouter un log dans `docs/LOGS/` si l'orientation, le statut ou un jalon change.

## Regles de tests

Commande minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Commande d'exemple si CLI, rapports ou exemples changent :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Si les tests ne peuvent pas etre lances, le compte rendu doit dire pourquoi.

## Garde-fous documentaires automatises

Le test `tests/test_project_documents.py` verifie maintenant les fichiers de
pilotage critiques et les sections minimales qui permettent a un agent de
reprendre le projet sans contexte oral.

Fichiers critiques couverts :

- `AGENTS.md` ;
- `docs/AUTONOMY_PROTOCOL.md` ;
- `docs/EXECUTION_LOOP.md` ;
- `docs/HUMAN_GATES.md` ;
- `docs/VALIDATION_MATRIX.md` ;
- `docs/STATUS.md` ;
- `docs/NEXT_ACTIONS.md` ;
- `docs/BACKLOG.md` ;
- `docs/ROADMAP.md` ;
- `docs/ARCHITECTURE.md` ;
- `docs/QUALITY_RULES.md` ;
- `docs/DECISIONS/README.md` ;
- `docs/LOGS/README.md`.

Le test echoue avec un message lisible de type `Fichiers de pilotage manquants`
ou `Sections de pilotage manquantes`.

## Regles d'impression reelle

- Ne pas declarer stable un jeu fonctionnel non imprime.
- Utiliser `docs/CALIBRATION_PROTOCOL.md` pour preparer les coupons, mesures et
  criteres OK/KO.
- Documenter le filament, l'imprimante, la buse, la hauteur de couche et le
  slicer si une mesure d'impression influence les valeurs.
- Garder les tolerances par defaut prudentes tant que les calibrations sont
  insuffisantes.
- Toute modification des valeurs de tolerance par defaut reste une gate humaine.

## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.

## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.

## Regles P57 de partition Fusion-only

- Une solution construite contient uniquement les groupes de bacs constructibles et les complements exacts explicitement demandes.
- `automatic_body_count` doit toujours rester a zero.
- Les jeux contre la boite et entre corps sont des vides techniques non materialises.
- Toute enveloppe finale doit repasser le validateur P55 sans modifier les cavites.
- Une impossibilite doit fournir code, message, reference et action corrective.
- Le solveur borne peut scorer des candidats, mais ne doit jamais revendiquer une optimalite globale.
- Le plan P57 ne constitue ni une CAD IR, ni une validation Fusion, ni une validation d impression.
## Regles P58 de resultat

- Une vue geometrique doit citer le digest du plan P57 dont elle derive.
- Les primitives SVG utilisent les bornes monde et cavites transformees par Python.
- Une partition impossible ne doit jamais etre dessinee comme une solution.
- Toute modification du projet invalide le dernier resultat ; une sauvegarde sans modification ne l invalide pas.
- Les noms utilisateur accompagnent les identifiants stables dans le resultat.
- Le rendu P58 ne vaut ni CAD IR, ni validation Fusion, ni validation d impression.
