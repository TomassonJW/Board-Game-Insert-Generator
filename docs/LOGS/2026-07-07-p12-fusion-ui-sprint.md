# Log - P12 UI Fusion sprint

Date : 2026-07-07

## Gate P12-UI

Gate humaine validee pour un sprint autonome limite a l'UI Fusion, aux parametres de generation et a la regeneration par relance. Le perimetre interdit reste : nouveau solveur, nouvelle geometrie Fusion, modules composites, fillets/conges, export STL/3MF, changement de tolerances et dependance `adsk` dans le coeur Python.

## P12-M001 - Toolbar relancable

Mission : stabiliser le lancement UI Fusion par bouton toolbar et commande relancable.

Changements :

- ajout d'un plan UI testable dans `fusion_skeleton.py` ;
- centralisation des constantes toolbar/commande ;
- message Fusion enrichi avec la politique `toolbar_button_reopens_command_without_addin_restart` ;
- documentation d'une strategie `Fusion UI Strategy` ;
- correction d'un artefact de statut P11 et d'une incoherence de smoke test P11.

Statut avant smoke test : `implemented-fusion`, validation Fusion manuelle requise, `print-validated: false`.
## Validation P12-M001V

Validation humaine Fusion confirmee apres le commit `a12ef42` :

- add-in recopie depuis le repo vers le dossier Fusion AddIns : OK ;
- commande `Generate Board Game Insert` visible : OK ;
- bouton visible dans `Design workspace > Utilities > Add-Ins` : OK ;
- la commande s'ouvre au lancement de l'add-in : OK ;
- apres fermeture / perte de focus, le bouton toolbar permet de rouvrir BGIG sans redemarrer l'add-in : OK ;
- CAD IR `simple_asset_product_scene` chargee via l'UI : OK ;
- mode `compact_and_exploded` utilise : OK ;
- generation Fusion : OK ;
- `Body sizing report` present : OK ;
- occurrences liees conservees : OK ;
- ligne `UI reopen policy: toolbar_button_reopens_command_without_addin_restart` presente : OK ;
- impression 3D : non validee.

Statut : `fusion-validated`, `print-validated: false`. Prochaine action : gate produit avant palette persistante, generation depuis config BGIG, nettoyage automatique ou regeneration plus ambitieuse.

## P12-UI-M002+ - UI Fusion parametrique V0

Mission : etendre la commande Fusion relancable vers une premiere UI parametrique
V0, sans nouvelle geometrie Fusion et sans palette HTML persistante.

Changements :

- ajout de l'action `generate`, `regenerate` et `clear_bgig_scene` ;
- ajout des champs `BGIG config JSON path` et `BGIG project root` ;
- ajout d'overrides UI pour dimensions de boite, grille, epaisseurs, clearances
  principales et profil d'impression ;
- generation d'une config temporaire puis d'une CAD IR temporaire quand une
  config BGIG est fournie ;
- import du coeur Python pur uniquement via `<project root>/src` cote add-in ;
- tagging des objets BGIG crees et nettoyage limite aux objets tagues ;
- ADR-0023 pour documenter la strategie et les limites.

Statut : `implemented-fusion`, validation Fusion manuelle requise,
`print-validated: false`.

Validation attendue : `P12-UI-M002V` doit confirmer dans Fusion la visibilite des
champs, le flux CAD IR direct, le flux config -> CAD IR temporaire, `Regenerate`,
`Clear BGIG Scene` et la preservation des objets non BGIG.

## P12-UI-M002V2 - Correction UI utilisable

Retour humain P12-UI-M002V : KO partiel. La commande existait, mais
`regenerate` accumulait des doublons, `Clear BGIG Scene` n'etait pas assez clair,
le project root et la config etaient trop manuels et les champs parametriques
semblaient non connectes.

Correction codee :

- modes UI explicites `cad_ir_file`, `config_file`, `quick_parametric_box` ;
- `quick_parametric_box` visible mais desactive ;
- project root auto-detecte via champ, `BGIG_PROJECT_ROOT`, config/add-in ou
  `C:\Users\janko\Documents\BGIG` ;
- settings local `bgig_ui_settings.json` pour memoriser config/root/CAD IR ;
- overrides refuses en `cad_ir_file` ;
- generation sous racine taguee `BGIG Generated Scene` ;
- clear/regenerate limites aux objets BGIG tagues ;
- reporting enrichi avec input mode, root, config, scene roots et preservation
  des objets non BGIG.

Validation attendue : `P12-UI-M002V2` dans Fusion.

## P12-UI-M002V3 - generate non cumulatif

Observation humaine : `generate` fonctionnait mais pouvait accumuler plusieurs
scenes BGIG si l'utilisateur cliquait plusieurs fois. La correction rend le flux
non cumulatif :

- comptage des racines BGIG taguees avant action ;
- `generate` refuse si une scene BGIG existe deja ;
- message explicite `BGIG scene already exists. Use regenerate or clear first.` ;
- `regenerate` conserve le chemin valider -> clear tagged-only -> regenerer ;
- `clear_bgig_scene` affiche les scenes avant/apres et preserve les objets non
  BGIG ;
- ajout d'un texte `Action safety` dans la commande Fusion ;
- tests hors Fusion mis a jour pour verrouiller le guard et les messages.

Validation attendue : `P12-UI-M002V3` dans Fusion, centree sur generate sans
doublon, regenerate sans doublon, clear visible et objet non BGIG preserve.

## P12-UI-M002V4 - occurrences visibles exactes

Observation humaine : P12-UI-M002V3 refusait bien certains doublons de scene,
mais Fusion montrait encore des instances superposees. L'hypothese retenue est
que l'occurrence initiale creee par `addNewComponent` restait visible comme
source parasite.

Correction codee :

- creation d'une occurrence source/helper taguee `source_helper_occurrence` ;
- masquage obligatoire de cette occurrence helper ;
- creation explicite de l'occurrence compacte via `addExistingComponent` ;
- creation explicite de l'occurrence eclatee via `addExistingComponent` en mode
  `compact_and_exploded` ;
- message Fusion enrichi : physical module count, source components, compact,
  exploded, visible expected/actual, helpers visibles et legacy bodies ;
- ADR-0024 ajoutee pour figer la strategie.

Validation attendue : `P12-UI-M002V4` dans Fusion, centree sur compact_only,
compact_and_exploded, absence d'occurrence source visible, regenerate sans
doublon et clear tagged-only.
