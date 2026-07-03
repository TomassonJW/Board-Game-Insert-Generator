# Execution Loop

Cette boucle est le mode standard d'un run Codex autonome sur ce depot.

## Boucle standard

1. Lire `AGENTS.md`.
2. Lire `docs/STATUS.md`.
3. Lire `docs/NEXT_ACTIONS.md`.
4. Lire `docs/BACKLOG.md`.
5. Identifier la premiere mission `ready` non bloquee et non gated.
6. Verifier ses dependances.
7. Creer une branche ou travailler dans un worktree si disponible.
8. Executer exactement une mission atomique.
9. Lancer les tests pertinents.
10. Mettre a jour les docs impactees.
11. Mettre a jour `docs/STATUS.md`.
12. Mettre a jour `docs/NEXT_ACTIONS.md`.
13. Mettre a jour `docs/BACKLOG.md` si de nouvelles taches apparaissent.
14. Creer une ADR si une decision structurante a ete prise.
15. Committer proprement.
16. Integrer automatiquement dans `main` si les tests passent et qu'aucune gate
    n'est atteinte.
17. Continuer sur une branche propre si le run autorise plusieurs missions, sinon
    s'arreter avec un rapport clair.

## Detail operationnel

### 1. Lecture

La lecture initiale doit etablir :

- phase active ;
- mission recommandee ;
- dependances ;
- gates humaines possibles ;
- verifications attendues ;
- fichiers probablement concernes.

### 2. Choix de mission

Priorite :

1. Mission explicite de l'humain.
2. Mission suivante dans `docs/NEXT_ACTIONS.md`.
3. Fallback vers `docs/BACKLOG.md`.

Codex ne doit pas choisir une mission plus interessante si une mission plus
prioritaire est deja `ready`.

### 3. Branche ou worktree

Si le depot est propre, creer une branche courte avec prefixe `codex/`.

Exemple :

```powershell
git switch -c codex/p0-m004-autonomy-dry-run
```

Si un worktree existe deja pour la mission, l'utiliser. Si le workspace contient
des modifications non liees, s'arreter ou travailler autour sans les ecraser.

### 4. Execution d'une mission atomique

Une mission atomique peut modifier plusieurs fichiers, mais elle doit garder un
objectif coherent. Elle ne doit pas cumuler, par exemple, une refonte de modele,
un changement de CLI et une preparation Fusion.

### 5. Verifications

Commande minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Commande d'exemple quand applicable :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Verification de diff recommandee :

```powershell
git diff --check
```

### 6. Mise a jour du pilotage

Mettre a jour les documents qui permettent au prochain agent de reprendre sans
contexte oral :

- statut reel ;
- prochaines actions ;
- backlog ;
- logs ;
- ADR si necessaire.

### 7. Commit

Avant commit :

```powershell
git status --short
git diff --check
```

Puis :

```powershell
git add <fichiers>
git commit -m "<message court>"
```

Le commit doit couvrir une seule mission.

### 8. Integration Git autonome

Apres un commit de mission reussi, Codex integre automatiquement le travail dans
`main` sans demander de validation humaine pour les operations Git standard. Le
chemin standard est maintenant `direct-to-main` ; une pull request est seulement
un repli si GitHub ou le depot refuse l'integration directe.

Procedure minimale :

```powershell
git status --short --branch
git diff --check
git fetch origin --prune
```

Si `origin/main` est ancetre de `HEAD` et qu'aucun conflit n'existe, l'integration
directe autorisee est :

```powershell
git push origin HEAD:refs/heads/main
```

Si `main` est disponible dans le worktree courant, le chemin local equivalent est :

```powershell
git switch main
git pull --ff-only origin main
git merge --ff-only <branche-mission>
git push origin main
```

Si `main` est deja utilise par un autre worktree, Codex ne force pas ce worktree :
il pousse le `HEAD` verifie vers `origin/main` quand la relation est
fast-forward, puis synchronise l'autre worktree seulement s'il est propre.

Si le push direct est refuse par les regles GitHub, Codex peut creer une PR et la
merger automatiquement seulement si les checks obligatoires passent et qu'aucune
review humaine n'est requise. Si la protection de branche, l'authentification, un
conflit ou une review humaine bloque l'integration, Codex s'arrete avec un
rapport d'infrastructure.

Apres integration, Codex repart d'une branche propre basee sur `origin/main` pour
la mission suivante.

## Echecs et blocages

Si les tests echouent, Codex peut corriger seulement si la cause est dans le
scope de la mission. Sinon il s'arrete avec :

- commande lancee ;
- sortie pertinente ;
- hypothese de cause ;
- fichiers suspects ;
- prochaine action recommandee.

Si une gate humaine apparait, Codex prepare un rapport de gate et s'arrete.

Si la mission revele une tache future, Codex l'ajoute au backlog sans commencer
cette tache dans le meme run.
