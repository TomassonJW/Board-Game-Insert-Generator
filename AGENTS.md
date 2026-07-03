# AGENTS.md - Protocole Codex pour Board Game Insert Generator

Ce depot construit progressivement un generateur intelligent d'inserts parametriques
pour jeux de societe, avec un coeur Python testable hors Fusion 360 puis une
integration Fusion 360 comme cible de generation.

Travaille en francais dans les documents projet, sauf quand le code, les noms de
types, les commandes ou la documentation officielle imposent l'anglais.

## Lecture obligatoire avant toute mission

Avant de proposer ou modifier quoi que ce soit, lis au minimum :

- `docs/AUTONOMY_PROTOCOL.md`
- `docs/HUMAN_GATES.md`
- `docs/STATUS.md`
- `docs/ROADMAP.md`
- `docs/BACKLOG.md`
- `docs/NEXT_ACTIONS.md`
- les ADR pertinentes dans `docs/DECISIONS/`
- les fichiers de code ou documentation directement concernes par la mission

Ne pars jamais directement sur une implementation lourde sans verifier la mission
active, son statut, ses dependances et ses criteres d'acceptation.

## Priorite de travail

Prefere toujours une petite mission terminee, testee et documentee a une grosse
mission incomplete. Si la demande est trop large, decoupe-la en missions plus
petites et documente ce decoupage dans `docs/BACKLOG.md`.

Le depot doit rester autopilotable : a la fin d'une mission, un futur agent doit
pouvoir reprendre sans contexte oral.

## Autonomous execution rules

Si aucune mission explicite n'est donnee, choisis la premiere mission `ready`
dans `docs/NEXT_ACTIONS.md`, puis seulement en fallback dans `docs/BACKLOG.md`.

Regles obligatoires :

- execute une seule mission a la fois ;
- ne travaille jamais sur plusieurs missions a la fois ;
- ne commence pas une mission dont les dependances ne sont pas terminees ;
- n'ignore jamais une gate humaine decrite dans `docs/HUMAN_GATES.md` ;
- ne modifie jamais la North Star sans validation humaine explicite ;
- prefere un changement petit, teste, documente et commite ;
- mets a jour les fichiers de pilotage a la fin de toute mission significative ;
- si la mission modifie le depot, fais un commit propre apres verification du
  diff et des tests disponibles ;
- termine par un rapport operationnel clair, ou continue la boucle si un run
  autonome multi-missions a ete explicitement demande et que la mission vient
  d'etre integree dans `main`.

La boucle standard est decrite dans `docs/EXECUTION_LOOP.md`. Le protocole
d'autonomie est decrit dans `docs/AUTONOMY_PROTOCOL.md`.

## Autonomous Git Integration Policy

La decision humaine du 2026-07-03 autorise l'integration Git autonome pour les
operations normales. La decision corrective du 2026-07-03 rend l'integration
`direct-to-main` obligatoire comme chemin standard : les pull requests ne sont
plus le chemin normal d'une mission autonome.

Une mission reste atomique, mais un run autonome peut enchainer plusieurs
missions si la demande le precise et si chaque mission est terminee, testee,
documentee, commitee puis integree dans `main` avant la suivante.

## Direct-to-main autonomous integration

Quand les tests passent, que `git diff --check` passe, que le workspace est
propre, qu'aucune vraie gate humaine n'est atteinte, que la branche est basee
sur `origin/main` et que l'integration est fast-forward ou non conflictuelle,
Codex doit integrer directement dans `main` par Git local puis pousser `main`
vers `origin/main`.

Chemin standard :

1. terminer la mission sur une branche dediee ;
2. lancer les tests et validations pertinentes ;
3. committer ;
4. `git fetch origin --prune` ;
5. verifier que `origin/main` n'a pas diverge ;
6. rebaser seulement si necessaire et sans conflit ;
7. integrer localement dans `main` par fast-forward ou merge simple non
   conflictuel ;
8. relancer les tests critiques si l'integration modifie l'etat teste ;
9. pousser directement `main` vers `origin/main` ;
10. supprimer les branches mission locales/distantes devenues inutiles ;
11. repartir d'une branche propre basee sur `origin/main`.

Les pull requests sont autorisees uniquement si GitHub refuse le push direct vers
`main`, si une protection de branche impose une PR, si une review humaine est
explicitement demandee, si une gate humaine est atteinte, si un conflit ou une
divergence non triviale apparait, ou si la mission est risquee ou structurante.
Un refus de merge PR par un controleur n'est pas une gate produit.

Codex s'arrete seulement pour une vraie gate, un echec de test non reparable dans
le scope, un conflit Git reel, une protection de branche, un probleme
d'authentification GitHub, un risque de perte de travail ou une decision
ambigue que les docs ne resolvent pas.

## Frontieres d'architecture

- Ne fais pas dependre le moteur principal de Fusion 360.
- Garde le coeur Python testable hors Fusion 360.
- Ne jamais importer `adsk.core`, `adsk.fusion` ou une API Fusion dans le coeur
  `src/board_game_insert_generator/`.
- Fusion 360 est un adaptateur de sortie, pas le moteur de decision.
- Toutes les dimensions metier sont en millimetres.
- Distingue toujours cellule theorique, corps imprimable, cavite, feature,
  tolerance, layout et export CAD.
- Ne confonds jamais `implemente`, `prevu`, `experimental` et `a valider par
  impression reelle`.

## Cycle de mission

Pour toute mission non triviale :

1. Comprendre l'objectif reel.
2. Lire les documents et fichiers pertinents.
3. Identifier les ambiguities, risques et decisions structurantes.
4. Proposer un plan court si la mission change l'architecture ou le produit.
5. Attendre validation si la decision est structurante ou irreversible.
6. Implementer par petits changements.
7. Ajouter ou adapter les tests utiles.
8. Lancer les verifications disponibles.
9. Relire le diff.
10. Mettre a jour le pilotage projet.

## Mise a jour documentaire obligatoire

Apres toute mission significative :

- mets a jour `docs/STATUS.md` avec l'etat reel ;
- mets a jour `docs/NEXT_ACTIONS.md` avec les prochaines missions recommandees ;
- mets a jour `docs/BACKLOG.md` si une tache est decouverte, terminee, bloquee ou
  redecoupee ;
- mets a jour les documents de conception concernes (`docs/ARCHITECTURE.md`,
  `docs/GEOMETRY_MODEL.md`, `docs/TOLERANCE_MODEL.md`,
  `docs/FUSION_360_STRATEGY.md`, `docs/QUALITY_RULES.md`) si le comportement ou
  les invariants changent ;
- ajoute une entree dans `docs/LOGS/` si la mission modifie l'orientation, le
  perimetre, le statut ou une hypothese importante du projet.

## Decisions techniques

Cree une ADR dans `docs/DECISIONS/` pour toute decision structurante, notamment :

- choix du format de configuration ;
- separation moteur/Fusion ;
- modele de layout ;
- strategie de tolerance ;
- representation des modules composites ;
- strategie de generation geometrique ;
- ajout d'une dependance majeure ;
- changement de comportement public d'API, CLI ou format de fichier.

Une decision raisonnable et reversible peut etre prise sans bloquer. Documente-la
clairement et cree une carte de revision si elle devra etre revalidee.

## Tests et validation

Lance les tests disponibles avant de terminer :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Si tu modifies la CLI ou les exemples, execute aussi au moins un exemple :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Si les tests ne peuvent pas etre lances, explique pourquoi dans le compte rendu
final et dans `docs/STATUS.md` si cela change l'etat projet.

Ne pretend jamais qu'une fonctionnalite est terminee si elle n'est pas testee.
Utilise plutot les statuts suivants :

- `implemente` : code present et tests automatises pertinents passes ;
- `experimental` : code present mais comportement incomplet ou peu valide ;
- `prevu` : decrit dans la roadmap ou le backlog, non code ;
- `a valider par impression reelle` : necessite un prototype physique.

## Regles de scope

- Ne cree pas de dependance lourde, service externe, framework structurant,
  moteur CAD alternatif, base de donnees ou outil SaaS sans ADR et validation.
- Ne supprime pas massivement, ne renomme pas des modules centraux et ne change
  pas une API publique sans expliquer l'impact.
- Ne stocke jamais de secrets, tokens, cles API, mots de passe ou identifiants
  dans le depot.
- Les donnees d'exemple doivent rester locales, non sensibles et reproductibles.

## Fin de mission

Le compte rendu final doit mentionner :

- fichiers modifies ;
- decisions prises ;
- tests ou verifications lances ;
- limites connues ;
- risques ;
- prochaine action recommandee.

Si un commit est demande, fais un commit propre avec un message explicite apres
verification du diff.
