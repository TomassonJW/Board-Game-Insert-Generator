# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Gate humaine active

### Gate - Validation manuelle P4-M003 dans Fusion 360

Statut : `blocked`.

Decision demandee :

- lancer ou faire lancer le smoke test manuel Fusion 360 de `P4-M003` ;
- confirmer si les sketches, bodies, noms, origines et dimensions observees
  correspondent a la CAD IR ;
- documenter les ecarts eventuels avant toute mission Fusion suivante ;
- autoriser explicitement une suite `P4-M004` si le perimetre Fusion doit etre
  elargi.

Contexte :

- `P4-M003` code une premiere generation minimale depuis `cad_ir_input.json` ;
- l'add-in cree une esquisse de reference de boite et des blanks rectangulaires dans le composant racine ;
- les tests hors Fusion couvrent le chargement CAD IR et le plan de generation ;
- l'execution reelle dans Fusion 360 n'a pas encore ete realisee dans ce run ;
- `adsk` reste interdit dans `src/board_game_insert_generator`.

Smoke test manuel attendu :

1. Installer `fusion_addin/BoardGameInsertGenerator` dans le dossier AddIns local.
2. Ouvrir ou creer un design Fusion vide.
3. Lancer `Board Game Insert Generator` depuis `Utilities > Add-ins`.
4. Verifier le message final : 1 reference outline, 2 blank bodies et creation dans le composant racine.
5. Verifier les sketches dans le composant racine :
   - `BGIG box reference - not printable outline` ;
   - `cards-main-01 - Main cards footprint` ;
   - `dice-01 - Dice tray footprint`.
6. Verifier les bodies :
   - `cards-main-01 rectangular blank` ;
   - `dice-01 rectangular blank`.
7. Mesurer les blanks :
   - `cards-main-01` : `68.9 x 99.2 x 44.0 mm` ;
   - `dice-01` : `59.7 x 59.2 x 29.0 mm`.
8. Noter OK/KO et ecarts dans un log de validation.

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
