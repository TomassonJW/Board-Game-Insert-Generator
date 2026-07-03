# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Politique active - Integration Git autonome

Statut : `active`.

Depuis la decision humaine du 2026-07-03, les operations Git standard sont gerees
automatiquement par Codex apres une mission reussie. Une mission doit etre testee,
commitee et integree dans `main` avant selection d'une mission suivante. Une pause
humaine reste requise seulement pour les vraies gates, les echecs, les conflits,
les protections de branche, les problemes d'authentification ou les risques de
perte de travail.

## Gate humaine active

### Gate - Autoriser le prochain perimetre apres P4-M004/P4-M006

Statut : `blocked`.

Decision demandee :

- choisir explicitement le prochain lot Fusion ou le retour au coeur Python ;
- confirmer le perimetre autorise avant toute nouvelle generation Fusion ;
- maintenir separees validation CAD, validation d'impression et exports.

Contexte :

- `P4-M003` code et valide manuellement une premiere generation minimale depuis
  une CAD IR JSON ;
- `P4-M005` rend la CAD IR regenerable depuis une configuration BGIG via
  `export-cad-ir` ;
- `P4-M006`, autorisee sous le libelle humain `P4-M004`, stabilise le pipeline
  d'entree Fusion : `cad_ir_input.json` par defaut ou `cad_ir_path.txt` comme
  chemin configure ;
- l'add-in valide le contrat minimal avant generation et affiche des erreurs
  Fusion actionnables ;
- la validation physique par impression 3D n'est pas realisee ;
- `adsk` reste interdit dans `src/board_game_insert_generator`.

Options possibles pour la suite, a valider explicitement :

- Option 1 : revenir au coeur Python pour cavites abstraites, modules composites
  ou qualite de layout avant d'elargir Fusion.
- Option 2 : etudier une sortie Assembly avec composants enfants, separee du mode
  Part Design.
- Option 3 : autoriser une prochaine mission Fusion ciblee, par exemple cavites
  simples ou preparations d'exports, avec perimetre et validations explicites.

Risques :

- confondre validation CAD visuelle et validation d'impression reelle ;
- elargir vers cavites, fillets, composants enfants ou exports sans gate ;
- laisser Fusion recalculer layout, offsets ou tolerances au lieu de consommer la
  CAD IR deja resolue.

## Missions bloquees tant que la gate n'est pas validee

- Toute suite Fusion apres stabilisation du pipeline CAD IR.
- Premier export STL/3MF.
- Cavites Fusion.
- Fillets/conges Fusion.
- Validation physique par impression reelle.
- Modification des valeurs de tolerance par defaut.
- Modules composites complets.

## Fin de chaque mission

Avant de terminer :

- mettre a jour `docs/STATUS.md` ;
- mettre a jour `docs/BACKLOG.md` ;
- remplacer cette liste par les prochaines actions reelles ;
- ajouter une ADR si une decision structurante a ete prise ;
- ajouter une entree de log si l'orientation ou le statut a change ;
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances ;
- committer proprement si le depot a ete modifie ;
- integrer automatiquement dans `main` si les tests passent et qu'aucune gate ou
  blocage Git n'est atteint.