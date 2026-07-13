# P66 - Contrat d execution Terra et acceptation du MVP V0.1

Statut : `p66-m000-integrated`, `p66-m001-ready`, `human-fusion-gate-required`,
`print-validated: false`.

Ce document est l instruction canonique pour deleguer P66 a un agent autonome.
Il complete `docs/MVP_V01_ACCEPTANCE_CONTRACT.md`, ADR-0055 et ADR-0056 a
ADR-0061. En cas de contradiction, les ADR acceptees et le contrat d acceptation
MVP restent prioritaires.

## 1. Resultat attendu

P66 ne developpe pas une nouvelle fonction produit. P66 prouve que les briques
P61 a P65 forment ensemble un parcours Fusion-only coherent, puis demande une
observation humaine unique dans Fusion 360.

P66 est verte seulement si une personne peut, depuis l add-in installe :

1. ouvrir la palette BGIG depuis Utilities ;
2. charger ou saisir un projet sans serveur, Vite ou navigateur externe ;
3. utiliser cartes sleevees, orientations et mesures explicites ;
4. encastrer localement plateaux et livrets depuis le dessus ;
5. obtenir une partition complete comportant plusieurs etages en Z ;
6. comprendre tailles, score, appuis, retraits et eventuels residuels ;
7. modifier une source, constater l invalidation, puis recalculer explicitement ;
8. materialiser et regenerer exactement le plan courant ;
9. conserver les objets Fusion non BGIG et une scene BGIG unique ;
10. exporter uniquement les corps imprimables et leurs manifestes.

Un P66 vert accepte le **MVP fonctionnel V0.1 Fusion-only**. Il ne valide ni
impression, ni tolerances physiques, ni formes ergonomiques V0.2, ni couvercles
V0.3, ni publication d une release.

## 2. Clarification P44 a P50

P44 a P50 n ont jamais ete valides comme releases. Les travaux P33/P34 sont des
explorations historiques compatibles, mais ne valent pas implementation ou
acceptation des lots canoniques suivants :

| Lots | Version | Contenu canonique | Etat avant P66 |
| --- | --- | --- | --- |
| P44 | V0.2 | contrat de formes, ergonomie et resistance | deferred |
| P45 | V0.2 | arrondis, chanfreins, encoches et fonds faciles a vider | deferred |
| P46 | V0.2 | preview fidele, materialisation Fusion et gate V0.2 | deferred |
| P47 | V0.3 | nouveau contrat de couvercles | deferred |
| P48 | V0.3 | couvercle encastrable integre au solveur | deferred |
| P49 | V0.3 | couvercle coulissant a trois rainures interieures | deferred |
| P50 | V0.3 | coupons, calibration 0 a 0,2 mm et impressions mesurees | deferred |

P44 ne peut devenir `ready` qu apres P67 accepte. P47 reste bloque jusqu a P46 OK.

## 3. Decomposition obligatoire de P66

### P66-M000 - Quarantaine des complements experimentaux

Type : durcissement produit borne de la palette, sans changement de solveur.

Avant la preparation de gate, l agent retire du parcours normal les actions de
creation Bac vide, Bloc plein / cale et Separateur. Le comportement attendu est
fixe par ADR-0061 :

- aucun controle de creation de complement dans la palette normale ;
- aucun complement dans les presets ou la fixture canonique P66 ;
- schema, loader, coeur et materialisation historiques conserves ;
- un ancien projet avec complement explicite reste lisible et regenerable ;
- aucun complement automatique ni migration destructive ;
- tests DOM, round-trip historique, bridge et materialisation de compatibilite ;
- package 0.1.20 attendu, puis commit et integration avant P66-M001.

P66-M000 ne redefinit pas le vrai futur comportement des complements. Cette
decision reste reservee a P67 et a un lot post-MVP distinct.

### P66-M001 - Preparation automatisee de la gate

Type : implementation de tooling, fixtures, tests et documentation de gate.

Dependance : P66-M000 integree et package de quarantaine verifie.

L agent prepare tout ce qui peut etre prouve hors Fusion et installe le package
exact. Il s arrete ensuite. Il ne simule jamais l observation humaine.

Livrables minimaux :

- `scripts/fusion/p66_mvp_complete_project.json` ;
- `scripts/fusion/p66_mvp_impossible_project.json` ;
- `scripts/fusion/prepare_p66_mvp_acceptance.ps1` ;
- `tests/test_p66_acceptance_prep.py` ;
- `docs/P66_FUSION_MVP_ACCEPTANCE.md` ;
- mises a jour de pilotage et log de mission.

Le preparateur doit reutiliser `scripts/fusion/install_addin.ps1`,
`_fusion_helpers.ps1` et `check_installed_addin.ps1`. Il ne cree pas un second
installateur et ne demande pas a Thomas de lancer du PowerShell.

### P66-V - Observation humaine Fusion

Type : gate humaine, aucune mutation du depot.

Thomas suit la checklist generee dans Fusion et retourne soit :

```text
P66 Fusion OK 0.1.20 - commit <sha>
```

soit :

```text
P66 Fusion KO - etape <n> - attendu <...> - observe <...> - message <...>
```

Une capture est utile pour un ecart visuel, mais le numero d etape, les nombres
de scene/corps et le texte visible sont prioritaires.

### P66-Hxx - Correctifs apres KO uniquement

Chaque cause independante devient une mission atomique `P66-H001`, `P66-H002`,
etc. Un hotfix :

- reproduit le KO par test automatise quand c est techniquement possible ;
- corrige une seule cause ;
- ne change pas les tolerances par defaut sans nouvelle gate ;
- ne remplace pas le solveur et n ajoute aucune dependance lourde ;
- relance toute la suite puis reinstalle le package ;
- renvoie vers une gate P66 complete, jamais vers une validation partielle.

### P66-CLOSE - Cloture apres OK humain

Type : documentation et integration seulement.

Apres un retour P66 OK explicite :

- marquer la V0.1 `mvp-accepted`, `fusion-validated`,
  `print-validated: false` ;
- enregistrer le commit/package observe et le rapport de gate ;
- mettre STATUS, CAPABILITY_MAP, ROADMAP, BACKLOG, NEXT_ACTIONS et HUMAN_GATES
  en coherence ;
- rendre P67 `ready` et P68 `planned-after-p66` ;
- ne rendre aucune mission P44 `ready` avant la decision humaine P67 ;
- ne pas publier de tag ou release sans decision humaine separee.

## 4. Preconditions P66-M001

L agent doit verifier avant toute modification :

- branche basee sur `origin/main`, workspace propre ;
- P61, P62, P63, P64 et P65 marques `done` et automatises ;
- P66-M000 integree, tests de compatibilite verts et package 0.1.20 present ;
- package courant 0.1.20 issu de P66-M000 ; P66-M001 ne change pas le runtime ;
- coeur `src/board_game_insert_generator` sans import `adsk` ;
- aucun changement non integre appartenant a une autre mission ;
- aucune nouvelle valeur de tolerance, geometrie V0.2 ou mecanisme V0.3.

Lectures obligatoires en plus d AGENTS.md :

- `docs/MVP_V01_ACCEPTANCE_CONTRACT.md` ;
- `docs/FUSION_ONLY_MVP_CONTRACT.md` ;
- `docs/P60_FUSION_MVP_ACCEPTANCE.md` comme precedent, pas comme specification ;
- ADR-0054 a ADR-0061 ;
- les contrats P61 a P65 et leurs tests ;
- les scripts `scripts/fusion/` existants.

## 5. Contrat des fixtures

### 5.1 Projet complet canonique

La fixture complete doit etre assez riche pour traverser P61-P65, mais assez
petite pour rester inspectable dans Fusion.

Elle doit contenir au minimum :

- une boite avec dimensions internes, marge haute et les jeux P65 separes ;
- au moins quatre conteneurs demandes et aucun conteneur automatique ;
- au moins deux familles dans un meme conteneur ;
- des cartes sleevees a plat et des cartes avec une orientation debout resolue ;
- au moins un reglage `Auto`, un `Cible` et un `Fixe` sur les axes de conteneur ;
- un plateau et un livret avec empreintes superieures localisees, ordre de
  retrait et prise ;
- une composition d au moins deux etages avec une origine Z strictement
  positive ;
- au moins un appui d etage et un ordre de retrait top-down ;
- zero complement dans la fixture canonique P66 ;
- zero filler, cale, separateur ou corps libre invente ;
- compatibilite des anciens complements couverte par un test separe, pas par la gate.

Les donnees exactes ne doivent pas etre choisies a l intuition. Terra doit
partir des fixtures deja prouvees de `test_partition_solver.py`,
`test_top_inset_reservation.py` et `test_project_v1.py`, puis figer dans le test
P66 les nombres effectivement obtenus : corps, cavites, etages, coupes, appuis,
origines Z, composants CAD IR et corps Fusion.

La fixture n est acceptable que si deux executions produisent le meme digest,
les memes placements et les memes dimensions.

### 5.2 Projet impossible

La fixture impossible doit provoquer une contrainte dure locale et explicable,
par exemple une dimension `Fixe` inferieure au minimum ou une hauteur physique
incompatible. Elle doit prouver :

- statut `impossible` ;
- diagnostic utilisateur localise et correction proposee ;
- aucun faux plan complet ;
- `Materialiser dans Fusion` desactive ;
- aucun CAD ou corps trompeur ;
- scene Fusion existante inchangee.

### 5.3 Grande cardinalite

Le cas de dizaines de lignes reste une preuve automatisee. Il ne doit pas
materialiser des dizaines de corps dans la gate humaine. Le test P66 reference
et conserve le cas de 50 conteneurs, son budget borne et son diagnostic.

## 6. Assertions automatiques non negociables

P66-M001 doit echouer si une assertion suivante manque :

### Projet et cycle de vie

- normalisation et round-trip JSON deterministes ;
- source, derive, solve et materialise portent des digests distincts ;
- edition source => derive recalcule, plan obsolete et scene non mutee ;
- estimation des tailles ne sauvegarde ni ne materialise ;
- proposition partielle, impossible ou obsolete non materialisable ;
- sauvegarde/reouverture restaure la saisie, jamais un faux etat materialise.

### Assets, plateaux et solveur

- sleeves et orientations resolues avant cavite ;
- dimensions physiques et dimensions resolues restent distinctes ;
- au moins deux etages, origine Z non nulle et support valide ;
- jeux boite/conteneur XY, inter-conteneurs XY, inter-etages Z et marge haute
  transportes separement ;
- reservation superieure appliquee seulement aux corps intersectes ;
- profondeur utile de cavite compensee sous plateau/livret ;
- non-percement des fonds et ordre de retrait ;
- conservation du volume, absence de collision et zero corps automatique ;
- Auto/Cible/Fixe et raisons par axe presentes.

### CAD IR et adaptateur Fusion

- nombre de composants CAD IR egal au nombre de corps explicites du plan ;
- cavites P55 non agrandies par l expansion de l enveloppe ;
- coupes de reservations distinctes des cavites de contenu ;
- noms techniques uniques meme si des noms utilisateur se repetent ;
- generation et regeneration produisent le meme digest et le meme nombre de
  corps ;
- outlines de boite tagues mais caches par defaut ;
- aucune occurrence eclatee ou reference non imprimable exportee ;
- manifestes JSON et Markdown honnetes, `print-validated: false`.

### Palette et packaging

- palette locale et bridge versionne, aucun localhost/Vite/navigateur requis ;
- un seul bouton persistant `Recalculer` et un seul `Materialiser dans Fusion` ;
- estimation locale dans Conteneurs, export primaire dans Apercu ;
- aucune fuite de digest, enum solveur ou rapport inspect brut au premier niveau ;
- lancement sain sans timeout ni message technique intrusif ;
- runtime pur copie dans `lib/board_game_insert_generator` ;
- manifeste, icones, palette, bridge et modules P61-P65 presents dans le package ;
- commit installe ecrit et relu ;
- installation idempotente et sauvegarde du projet courant non destructive ;
- actions Bac vide, Bloc plein / cale et Separateur absentes du parcours normal ;
- ancien projet avec complement explicite toujours lisible sans creation nouvelle.

## 7. Comportement du preparateur PowerShell

`prepare_p66_mvp_acceptance.ps1` doit :

1. resoudre repo, commit et chemin Fusion avec les helpers existants ;
2. lancer les preuves P66 ciblees avant toute installation ;
3. construire plan, vue resultat, CAD IR et plan Fusion temporaires ;
4. verifier les digests et nombres attendus ;
5. installer l add-in du commit exact ;
6. verifier le manifeste, le runtime package et les marqueurs P61-P65 ;
7. sauvegarder un projet utilisateur different une seule fois ;
8. installer atomiquement la fixture complete comme projet courant ;
9. ecrire un marqueur de commit et un rapport de preflight lisible ;
10. imprimer uniquement les actions restantes dans Fusion.

Le mode `-DryRun` ne modifie ni APPDATA ni Documents. Deux executions reelles
successives doivent etre idempotentes. En cas de refus APPDATA, le message exact
reste :

```text
Local AppData write blocked. Use Local/Handoff or approve filesystem write.
```

## 8. Checklist humaine P66-V

Le document genere `docs/P66_FUSION_MVP_ACCEPTANCE.md` doit demander exactement
les observations suivantes.

### A. Acces et chargement

1. Creer un design Fusion compatible Assembly et un corps non BGIG nomme
   `P66 NON BGIG - KEEP`.
2. Lancer BGIG depuis son icone Utilities.
3. Confirmer une seule palette, taille exploitable, aucun ancien dialogue,
   aucun navigateur et aucun timeout moteur.
4. Confirmer que le statut sain est discret et le rapport technique replie.

### B. Projet et invalidation

5. Parcourir Boite, Plateaux et livrets, Elements du jeu, Conteneurs, Reglages,
   Apercu. Confirmer que Bac vide, Bloc plein / cale et Separateur ne sont plus
   proposes dans le parcours normal.
6. Confirmer sleeves, dimensions resolues, une orientation a plat et une debout.
7. Dans Conteneurs, lancer `Estimer les tailles` et confirmer minimum, demande,
   calculee, etage et raisons par axe sans creation de scene.
8. Modifier une dimension source. Confirmer derive actualise, ancien apercu
   grise, Materialiser desactive et scene inchangee.
9. Restaurer la fixture ou annuler la modification, puis Recalculer.

### C. Resultat complet

10. Confirmer statut construit, nombre exact de corps, zero automatique et au
    moins deux etages.
11. Confirmer vue dessus et coupe X/Z, plateau/livret encastres, prise, appuis,
    ordre de retrait et cavites encore suffisamment profondes sous les plats.
12. Confirmer score et sous-criteres en langage utilisateur, sans code moteur.

### D. Scene Fusion sure

13. Cliquer Materialiser dans Fusion.
14. Confirmer une seule racine BGIG, le nombre exact de composants et des corps
    sur au moins deux origines Z.
15. Confirmer les coupes localisees des plats, les cavites ouvertes, les noms
    uniques et les deux sketches de boite caches.
16. Confirmer que `P66 NON BGIG - KEEP` existe toujours.
17. Cliquer Regenerer et reconfirmer une racine, les memes nombres, aucun
    doublon et l objet non BGIG preserve.

### E. Export, reouverture et refus honnete

18. Exporter les imprimables : un STL par corps explicite, aucun sketch/
    reference, manifestes JSON et Markdown presents.
19. Fermer puis relancer l add-in et confirmer la restauration du projet.
20. Importer la fixture impossible, verifier le diagnostic local et le bouton
    Materialiser desactive ; la scene precedente reste intacte.
21. Effacer la scene BGIG et confirmer que l objet non BGIG reste present.

Une seule etape KO rend P66 KO. Une observation partielle ne peut pas accepter
le MVP.

## 9. Boucles de review exigees de Terra

Terra doit executer au minimum trois revues avant de livrer P66-M001 :

1. **Review contrat** : chaque critere MVP est relie a une fixture, une
   assertion automatique ou une observation humaine.
2. **Review technique** : aucune logique metier dupliquee dans PowerShell,
   JavaScript ou adsk ; aucun nouveau solveur, tolerance ou corps automatique.
3. **Review operabilite** : preparateur idempotent, chemins Windows surs,
   sauvegarde non destructive, sortie courte et checklist numerotee.

Commandes minimales :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m compileall -q src fusion_addin/BoardGameInsertGenerator
git diff --check
rg -n "adsk" src/board_game_insert_generator
scripts/fusion/prepare_p66_mvp_acceptance.ps1 -DryRun
scripts/fusion/prepare_p66_mvp_acceptance.ps1
scripts/fusion/check_installed_addin.ps1
```

La recherche `adsk` doit retourner zero import dans le coeur. La suite complete,
le dry-run, l installation reelle et les marqueurs doivent etre verts avant la
gate humaine.

## 10. Interdits explicites

P66-M001 ne doit pas :

- modifier le solveur, les formules de score ou les valeurs physiques pour
  forcer la fixture a passer ;
- ajouter CP-SAT, MIP, service, serveur, framework ou dependance ;
- reintroduire frontend, Vite, localhost ou navigateur externe ;
- modifier une cavite, reservation ou geometrie Fusion sans KO reproduit et
  mission P66-Hxx separee ;
- afficher une proposition partielle comme construite ;
- materialiser une suggestion de cale ;
- supprimer ou modifier un objet Fusion non BGIG ;
- revendiquer `print-validated` ;
- accepter P66 automatiquement ;
- commencer P44 avant le retour humain P66 OK et l atelier humain P67 ;
- reactiver ou supprimer les complements historiques pendant P66-M001.

## 11. Rapport de fin P66-M001

Le rapport Terra doit contenir :

- commit source et version du package installe ;
- fixtures et resultats exacts ;
- nombre de tests et commandes lancees ;
- digests et nombres plan/CAD/Fusion attendus ;
- chemin de sauvegarde du projet utilisateur ;
- resultat du dry-run, de l installation et des marqueurs ;
- limites et risques ;
- uniquement la checklist Fusion restante ;
- statut final `gate-prepared`, jamais `fusion-validated`.

## 12. Prompt court a donner a Terra

```text
Reprends BGIG sur une branche propre basee sur origin/main et execute P66-M000
puis P66-M001, strictement une mission a la fois, selon
docs/P66_TERRA_EXECUTION_CONTRACT.md et ADR-0061. Lis AGENTS.md et tout le
pilotage obligatoire. P66-M000 retire seulement du parcours normal la creation de
Bac vide, Bloc plein / cale et Separateur, conserve les anciens projets et interdit
toute migration destructive. Teste, committe et integre P66-M000 dans main avant
P66-M001. Prepare ensuite les fixtures complete sans complement et impossible, les
preuves automatiques, le preparateur Fusion idempotent, l installation du commit
exact et la checklist humaine. Lance la suite complete, compileall, diff-check,
controle adsk, dry-run, installation reelle et marqueurs. Integre P66-M001 puis
arrete-toi a la gate humaine P66-V. Ne commence ni P67 ni P44 et ne revendique ni
validation Fusion ni impression.
```
