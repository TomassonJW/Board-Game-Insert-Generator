# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Gate humaine active

### Gate - Finaliser la validation dimensionnelle P4-M003

Statut : `blocked`.

Decision demandee :

- confirmer les mesures dimensionnelles des deux blanks de la fixture ;
- documenter tout ecart observe dans Fusion avant toute mission Fusion suivante ;
- autoriser explicitement une suite `P4-M004` si le perimetre Fusion doit etre
  elargi.

Contexte :

- `P4-M003` code une premiere generation minimale depuis `cad_ir_input.json` ;
- l'add-in cree une esquisse de reference de boite et des blanks rectangulaires dans le composant racine ;
- les tests hors Fusion couvrent le chargement CAD IR et le plan de generation ;
- le smoke test manuel a confirme que l'add-in apparait, que le message final est OK et que les modules sont visibles ;
- les mesures dimensionnelles des blanks restent a confirmer/documenter ;
- `adsk` reste interdit dans `src/board_game_insert_generator`.

Smoke test manuel restant a completer :

1. Mesurer les blanks :
   - `cards-main-01` : `68.9 x 99.2 x 44.0 mm` ;
   - `dice-01` : `59.7 x 59.2 x 29.0 mm`.
2. Noter OK/KO et ecarts dans un log de validation.

Options apres validation :

- Option 1 recommandee : documenter le resultat manuel et corriger seulement les
  ecarts P4-M003 si necessaire.
- Option 2 : autoriser une mission `P4-M004` limitee a une meilleure UX de
  chargement CAD IR ou a un rapport de validation Fusion.
- Option 3 : bloquer Fusion et revenir au coeur Python si la generation minimale
  est instable.

Risques :

- la generation peut fonctionner hors tests mais echouer dans l'environnement
  Fusion local ;
- une validation visuelle Fusion ne valide pas l'impression reelle ;
- l'elargissement vers cavites, fillets ou exports doit rester gate.

## Missions bloquees tant que la gate n'est pas validee

- `P4-M004` ou toute suite Fusion.
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
