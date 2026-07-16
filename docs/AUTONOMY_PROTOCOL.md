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
- Travailler par capability, milestone, gate et validation, pas seulement par prochain fichier a modifier.
- Ne jamais confondre `ready`, `done`, `experimental`, `prevu` et `a valider par
  impression reelle`.
- S'arreter si une gate humaine est atteinte.
- Ne jamais presenter une validation par code comme une validation par impression.
- Ne jamais introduire Fusion 360 dans le coeur Python.
- Le MVP se construit dans la palette embarquee de l add-in Fusion selon ADR-0055.
- Refuser toute mission qui remet le Studio web, localhost ou Vite dans le runtime MVP.

## Selection de mission

### Verrou de chemin critique des releases

Depuis ADR-0047, le rebase P60-R et ADR-0061, la selection par capability est
subordonnee a l ordre des releases. Tant que P66 n a pas accepte la V0.1, seules
les missions P61 a P66 du chemin revise peuvent etre `ready`. Apres P66, P67 doit
accepter humainement les priorites avant que P44 devienne `ready`. Tant que P46
n a pas accepte la V0.2, aucune mission couvercle V0.3 ne peut etre `ready`. P69
reste bloquee jusqu a P50 et aucun P70+ ne devient `ready` avant son rapport.

Une gate humaine qui choisit une option d'une version ulterieure n'en change pas
la priorite. Codex doit verifier la checklist de sortie de la version active
avant `NEXT_ACTIONS.md`, puis les capabilities. Les prototypes prematures restent
archives et hors du parcours principal.

Ordre de priorite :

1. Mission explicite donnee par l'humain.
2. Premiere mission `ready` dans `docs/NEXT_ACTIONS.md`.
3. Premiere mission `ready` dans `docs/BACKLOG.md`.

Avant de selectionner une mission, Codex verifie :

- quelle capability elle sert dans `docs/CAPABILITY_MAP.md` ;
- a quel milestone utilisateur elle contribue ;
- si elle rapproche de la North Star ;
- si elle depend d'une capability encore `planned`, `blocked` ou `deferred` ;
- si une gate humaine la bloque ;
- quelle validation prouvera le resultat.

Codex doit refuser de lancer une mission si :

- son statut n'est pas `ready` ;
- une dependance n'est pas terminee ;
- une gate humaine est ouverte ;
- les criteres d'acceptation sont absents ou ambigus ;
- la mission melange plusieurs changements structurants ;
- la mission court-circuite une capability prerequisite ;
- une mission precedente du meme run n'a pas encore ete testee, commitee et
  integree dans `main`, ou la limite de missions du run est atteinte.

Si aucune mission n'est prete, Codex s'arrete avec un rapport de blocage et une
proposition de clarification.

## Verification de readiness

Avant implementation, Codex vérifie d’abord le parcours court :

- `AGENTS.md` ;
- `docs/PILOTAGE_CURRENT.md` ;
- `docs/NEXT_ACTIONS.md` ;
- `docs/HUMAN_GATES.md` ;
- le contrat, les ADR et les fichiers directement concernés.

Il ouvre ensuite `STATUS.md`, `NORTH_STAR.md`, `CAPABILITY_MAP.md`, `ROADMAP.md`
et `BACKLOG.md` dès qu’un fait, une dépendance, une capability, une trajectoire
ou une décision doit être vérifié en détail. Le parcours court ne remplace jamais
ces sources canoniques.

Une mission est prete seulement si son objectif, sa capability, son milestone,
ses livrables, ses dependances, ses criteres d'acceptation et ses verifications
attendues sont actionnables.

## Pilotage par capabilities

`docs/CAPABILITY_MAP.md` est le pont entre la North Star et le backlog. Il sert a
savoir quelle capacite produit existe, laquelle est seulement decrite, laquelle
est bloquee par gate, et quelle validation autorise le statut affiche.

Apres une mission significative, Codex met a jour le statut d'une capability
uniquement si la preuve correspondante existe : test code, test CLI, validation
Fusion, validation impression ou inspection documentaire. Une capability peut
etre `implemented-cad-ir` sans etre `implemented-fusion`.

## Execution

Codex execute la mission par petits changements :

1. Cadrer le besoin reel.
2. Lire les fichiers pertinents.
3. Identifier capability, milestone, risques et gates possibles.
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
plus des gates humaines. La decision corrective du 2026-07-03 etablit que les
pull requests ne sont plus le chemin standard d'integration autonome. Apres
chaque mission reussie, Codex doit integrer le travail dans `main` avant de
selectionner une mission suivante.

## Direct-to-main autonomous integration

Flux obligatoire apres mission :

1. Verifier `git status --short --branch`.
2. Lancer les tests pertinents et `git diff --check`.
3. Verifier que `adsk` reste absent de `src/board_game_insert_generator` sauf
   mission explicitement autorisee.
4. Committer le scope de mission si le depot a change.
5. `git fetch origin --prune`.
6. Verifier que la branche de mission est basee sur `origin/main` et que
   `origin/main` n'a pas diverge.
7. Rebaser seulement si necessaire, uniquement si le rebase est propre et sans
   conflit.
8. Integrer dans `main` par fast-forward ou merge simple non conflictuel.
9. Relancer les tests critiques si l'etat integre differe de l'etat teste.
10. Pousser directement `main` vers `origin/main`.
11. Supprimer les branches mission locales/distantes devenues inutiles si
    l'integration est confirmee.
12. Repartir d'une branche propre basee sur `origin/main` avant toute mission
    suivante.

Si `main` est deja utilise par un autre worktree local, Codex ne force pas ce
worktree. Il peut pousser un `HEAD` verifie directement vers `refs/heads/main`
quand la relation est fast-forward, puis synchroniser le worktree `main` separe
si celui-ci est propre.

Les pull requests ne sont autorisees qu'en repli : push direct refuse ou protege,
review humaine imposee, gate humaine atteinte, conflit reel, divergence non
triviale, checks obligatoires indisponibles ou mission risquee/structurante.

L'humain n'est pas sollicite pour push, pull/fetch, rebase simple, creation de
branche, integration direct-to-main, suppression raisonnable de branche ou
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

## Preparation des gates Fusion

Les validations Fusion restent humaines, mais leur preparation est une
responsabilite Codex.

Pour toute gate Fusion future, Codex doit lancer les scripts disponibles dans
`scripts/fusion/` pour preparer l'environnement local : installation de l'add-in,
generation des CAD IR temporaires si necessaire, ecriture des settings UI et
verification des marqueurs installes. Le rapport final doit donner uniquement les
actions restantes dans Fusion.

Si Codex ne peut pas ecrire dans `%APPDATA%`, il doit s'arreter avec :

```text
Local AppData write blocked. Use Local/Handoff or approve filesystem write.
```

et ne pas presenter la validation Fusion comme prete.
## Documentation de fin de mission

Apres une mission significative, Codex met a jour :

- `docs/STATUS.md` ;
- `docs/NORTH_STAR.md` ;
- `docs/CAPABILITY_MAP.md` ;
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
- la capability visee est bloquee ou prematuree ;
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
