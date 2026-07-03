# Autonomy Protocol

## Objectif

Le projet doit etre auto-pilotable, mais jamais auto-souverain.

Codex peut avancer mission par mission avec une forte autonomie locale, a
condition de respecter les documents de pilotage, les ADR acceptees, les tests
disponibles et les gates humaines.

Codex ne peut pas modifier la North Star, l'architecture structurante, le modele
de tolerance, l'integration Fusion 360 ou les valeurs physiques critiques sans
validation humaine explicite.

## Principes

- Executer une seule mission a la fois.
- Preferer un changement petit, teste, documente et commite.
- Lire l'etat reel avant de choisir une mission.
- Ne jamais confondre `ready`, `done`, `experimental`, `prevu` et `a valider par
  impression reelle`.
- S'arreter si une gate humaine est atteinte.
- Ne jamais presenter une validation par code comme une validation par impression.
- Ne jamais introduire Fusion 360 dans le coeur Python.

## Selection de mission

Ordre de priorite :

1. Mission explicite donnee par l'humain.
2. Premiere mission `ready` dans `docs/NEXT_ACTIONS.md`.
3. Premiere mission `ready` dans `docs/BACKLOG.md`.

Codex doit refuser de lancer une mission si :

- son statut n'est pas `ready` ;
- une dependance n'est pas terminee ;
- une gate humaine est ouverte ;
- les criteres d'acceptation sont absents ou ambigus ;
- la mission melange plusieurs changements structurants ;
- une mission precedente du meme run n'a pas encore ete testee, commitee et
  integree dans `main`, ou la limite de missions du run est atteinte.

Si aucune mission n'est prete, Codex s'arrete avec un rapport de blocage et une
proposition de clarification.

## Verification de readiness

Avant implementation, Codex verifie :

- `AGENTS.md` ;
- `docs/STATUS.md` ;
- `docs/ROADMAP.md` ;
- `docs/NEXT_ACTIONS.md` ;
- `docs/BACKLOG.md` ;
- `docs/HUMAN_GATES.md` ;
- les ADR pertinentes dans `docs/DECISIONS/` ;
- les fichiers de code ou documentation directement concernes.

Une mission est prete seulement si son objectif, ses livrables, ses dependances,
ses criteres d'acceptation et ses verifications attendues sont actionnables.

## Execution

Codex execute la mission par petits changements :

1. Cadrer le besoin reel.
2. Lire les fichiers pertinents.
3. Identifier les risques et gates possibles.
4. Proposer un plan court si une decision structurante est en jeu.
5. Attendre validation si une gate humaine est atteinte.
6. Modifier le minimum de fichiers necessaires.
7. Ajouter ou adapter les tests utiles quand le comportement change.
8. Lancer les validations pertinentes.
9. Relire le diff.
10. Mettre a jour le pilotage.
11. Committer proprement si le depot a ete modifie.
12. Integrer automatiquement dans `main` si les tests passent et qu'aucune gate
    ou blocage Git n'est atteint.

## Autonomous Git Integration Policy

La decision humaine du 2026-07-03 etablit que les operations Git normales ne sont
plus des gates humaines. Apres chaque mission reussie, Codex doit integrer le
travail avant de selectionner une mission suivante.

Flux obligatoire apres mission :

1. Verifier `git status --short --branch`.
2. Lancer les tests pertinents et `git diff --check`.
3. Verifier que `adsk` reste absent de `src/board_game_insert_generator` sauf
   mission explicitement autorisee.
4. Committer le scope de mission si le depot a change.
5. `git fetch origin --prune`.
6. Integrer dans `main` par la methode la plus sure autorisee : push
   fast-forward vers `origin/main`, PR puis merge automatique, ou integration Git
   distante equivalente.
7. Si l'integration reussit, repartir d'une branche propre basee sur
   `origin/main` avant toute mission suivante.

L'humain n'est pas sollicite pour push, pull/fetch, rebase simple, creation de
branche, PR standard, merge standard, suppression raisonnable de branche ou
reprise depuis `origin/main`.

Arrets obligatoires lies a Git : conflit reel, push/merge refuse par protection,
authentification GitHub indisponible, checks obligatoires en echec, review humaine
obligatoire, divergence non triviale ou risque de perte de travail.

Les rapports finaux doivent rester courts et orientes decision : missions faites,
commits, integrations, tests, branche finale, workspace, prochaine mission et
gate eventuelle.

## Tests et validations

Validation minimale avant fin de mission :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Si la CLI, les exemples ou les rapports sont concernes :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Si une validation ne peut pas etre lancee, Codex doit documenter la raison dans
le compte rendu final et, si cela change l'etat reel, dans `docs/STATUS.md`.

## Documentation de fin de mission

Apres une mission significative, Codex met a jour :

- `docs/STATUS.md` ;
- `docs/NEXT_ACTIONS.md` ;
- `docs/BACKLOG.md` ;
- les documents de conception impactes ;
- une ADR si une decision structurante est prise ;
- un log dans `docs/LOGS/` si le statut, le perimetre ou une hypothese importante
  change.

## Commit

Si la mission modifie le depot, Codex doit preparer un commit propre apres :

- tests disponibles lances ou impossibilite documentee ;
- diff relu ;
- statut des fichiers verifie ;
- scope limite a une seule mission.

Le message de commit doit indiquer le lot livre, par exemple :

```text
bootstrap autonomy protocol
```

## Arrets obligatoires

Codex s'arrete sans implementation si :

- une gate humaine est atteinte ;
- une dependance n'est pas satisfaite ;
- les tests echouent et la correction sortirait du scope ;
- le diff attendu implique une refonte massive ;
- une nouvelle dependance lourde semble necessaire ;
- une decision structurante manque d'ADR ;
- l'etat Git ne correspond pas au scope de mission ;
- une information externe recente est necessaire et non verifiee.

## Rapport final

Le rapport final doit indiquer :

- hash du commit si commit cree ;
- fichiers crees ou modifies ;
- decisions prises ;
- tests ou verifications lancees ;
- limites connues ;
- risques ;
- etat du workspace ;
- prochaine action recommandee.
