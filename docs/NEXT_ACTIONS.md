# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Gate humaine active

### Gate - Autoriser le prochain perimetre Fusion apres P4-M003

Statut : `blocked`.

Decision demandee :

- choisir le prochain lot Fusion ou revenir au coeur Python ;
- confirmer explicitement le perimetre autorise avant toute nouvelle generation
  Fusion ;
- maintenir separees validation CAD, validation d'impression et exports.

Contexte :

- `P4-M003` code une premiere generation minimale depuis `cad_ir_input.json` ;
- l'add-in cree une esquisse de reference de boite et des blanks rectangulaires
  dans le composant racine ;
- le smoke test manuel confirme que l'add-in apparait, que le message final est
  OK, que les modules/blanks sont visibles et que les dimensions mesurees sont
  conformes a la fixture ;
- la validation physique par impression 3D n'est pas realisee ;
- `adsk` reste interdit dans `src/board_game_insert_generator`.

Options possibles pour la suite, a valider explicitement :

- Option 1 : ameliorer le chargement local de CAD IR et l'UX d'erreur de l'add-in.
- Option 2 : etudier une sortie Assembly avec composants enfants, separee du mode
  Part Design.
- Option 3 : revenir au coeur Python pour cavites, modules composites ou qualite
  de layout avant d'elargir Fusion.

Risques :

- confondre validation CAD visuelle et validation d'impression reelle ;
- recreer trop tot des composants enfants Fusion sans cible Assembly claire ;
- elargir vers cavites, fillets ou exports sans gate.

## Missions bloquees tant que la gate n'est pas validee

- Toute suite Fusion apres `P4-M003`.
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
- committer proprement si le depot a ete modifie.
