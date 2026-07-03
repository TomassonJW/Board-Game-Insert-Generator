# ADR-0004 - Documentation as project control plane

## Statut

Accepte.

## Contexte

Le projet doit etre developpe progressivement par humains et agents Codex. Sans
pilotage centralise, les agents risquent de lancer des implementations trop larges
ou de melanger vision produit, decisions techniques, backlog et statut reel.

Le depot contient deja un moteur Python minimal. La prochaine difficulte n'est
pas seulement de coder plus vite, mais de garder les increments coherents,
testables et documentes jusqu'a l'integration Fusion 360 puis au produit final.

## Options

1. Garder seulement le README et les issues GitHub.
2. Utiliser un ensemble de documents versionnes dans le depot comme plan de
   controle projet.
3. Deporter tout le pilotage dans un outil externe de gestion de projet.

## Decision

Utiliser les documents versionnes du depot comme plan de controle principal :

- `AGENTS.md` pour le protocole de travail des agents ;
- `docs/STATUS.md` pour l'etat reel ;
- `docs/ROADMAP.md` pour les phases macro ;
- `docs/BACKLOG.md` pour les missions actionnables ;
- `docs/NEXT_ACTIONS.md` pour la reprise immediate ;
- `docs/DECISIONS/` pour les ADR ;
- `docs/LOGS/` pour les journaux d'avancement.

Les issues GitHub peuvent materialiser des missions, mais le depot doit rester
comprehensible meme sans contexte externe.

## Consequences

Positives :

- reprise facile par un futur agent ;
- decisions et backlog versionnes avec le code ;
- moins de dependance a un outil externe ;
- meilleure coherence entre implementation, tests et documentation.

Negatives :

- discipline de mise a jour obligatoire ;
- risque de documentation stale si les agents ne suivent pas `AGENTS.md` ;
- duplication possible avec les issues GitHub si les deux ne sont pas synchronises.

## Alternatives refusees

Le README seul est refuse parce qu'il ne suffit pas a porter roadmap, statut,
decisions et backlog detaille.

Un outil externe seul est refuse parce que le depot doit rester autopilotable,
auditable et clonable sans contexte oral.
