# Autonomy Runbook

Ce runbook est destine a l'humain qui lance ou supervise une boucle Codex.

## Lancer une boucle Codex

Demande type :

```text
Lis AGENTS.md, suis docs/EXECUTION_LOOP.md, prends la premiere mission ready dans
docs/NEXT_ACTIONS.md, execute une seule mission, teste, mets a jour le pilotage
et fais un commit propre.
```

Avant lancement, verifier rapidement :

```powershell
git status --short --branch
```

Si le workspace contient des changements humains non commites, dire a Codex s'il
doit les ignorer, travailler autour ou s'arreter.

## Verifier apres une mission

Controler :

- un seul objectif livre ;
- tests lances ou impossibilite documentee ;
- `docs/STATUS.md` a jour ;
- `docs/NEXT_ACTIONS.md` pointe la prochaine mission ;
- `docs/BACKLOG.md` coherent ;
- ADR ou log ajoute si necessaire ;
- commit present si le depot a ete modifie.

Commandes utiles :

```powershell
git status --short --branch
git log --oneline -1
```

## Reconnaitre une gate

Une gate est probablement atteinte si Codex parle de :

- changer la North Star ;
- modifier l'architecture majeure ;
- changer les tolerances par defaut ;
- commencer Fusion 360 ;
- exporter un fichier imprimable ;
- valider une impression ;
- ajouter une dependance lourde ;
- supprimer ou refondre beaucoup de fichiers.

Dans ce cas, demander un rapport conforme a `docs/HUMAN_GATES.md`.

## Si Codex bloque

Demander :

```text
Donne un rapport de blocage : mission visee, dependance manquante, gate eventuelle,
fichiers lus, options possibles et plus petit prochain pas.
```

Ne pas demander de coder autour d'une gate non validee.

## Si les tests echouent

Demander :

```text
Analyse l'echec, corrige seulement si la cause est dans le scope de la mission.
Sinon, mets a jour STATUS/NEXT_ACTIONS/BACKLOG avec le blocage et arrete-toi.
```

La sortie utile doit inclure :

- commande lancee ;
- erreur pertinente ;
- cause probable ;
- correction faite ou raison d'arret.

## Si Codex derive

Signes de derive :

- plusieurs missions melangees ;
- ajout d'une dependance non demandee ;
- implementation Fusion trop tot ;
- changement massif de structure ;
- statut trop optimiste ;
- absence de tests.

Instruction de reprise :

```text
Stoppe la derive. Reviens a la mission initiale, liste le hors-scope detecte,
annule seulement tes propres changements hors-scope si c'est sur, puis termine ou
arrete-toi avec rapport.
```

## Reprendre apres interruption

Demander a Codex :

```text
Reprends la mission en cours. Commence par git status, lis STATUS/NEXT_ACTIONS/
BACKLOG, identifie les changements deja presents, puis continue sans ecraser les
modifications humaines.
```

Si un commit existe deja, verifier :

```powershell
git log --oneline -3
git status --short --branch
```

## Quand refuser l'autonomie

Ne pas lancer de boucle autonome si :

- la mission est floue ;
- le workspace est sale et non compris ;
- une decision produit structurante est en discussion ;
- une validation physique est necessaire ;
- un secret ou un compte externe est implique.
