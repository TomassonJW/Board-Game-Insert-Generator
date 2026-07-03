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
