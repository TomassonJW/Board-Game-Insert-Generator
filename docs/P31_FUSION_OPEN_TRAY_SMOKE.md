# Smoke Fusion P31 - Bacs ouverts issus du Studio

## But

Observer dans Fusion les trois bacs ouverts issus du modele local `mixed-box`.
Cette observation valide seulement le passage CAD IR -> Fusion pour ces coupes.
Elle ne valide pas l ajustement des assets, le slicer ou une impression.

## Preparation faite par Codex

- Export P31 du starter `mixed-box` : trois composants, trois cavites top-open.
- Add-in et settings Fusion prepares par
  `scripts/fusion/prepare_local_composer_selection_test.ps1`.
- Contrats hors Fusion verifies : corps, cavites, fond conserve et plan de
  coupes Fusion.

## Ce qui doit etre visible dans Fusion

1. Trois bacs ouverts dans les positions compactes du plan choisi.
2. Pour chaque bac : quatre parois, un fond de 1.2 mm et une cavite ouverte en
   haut.
3. Aucune encoche, cloison asset-specific, arrondi, couvercle ou geometrie
   utilisateur non BGIG ajoutée.
4. Aucun message ne doit dire que la piece est imprimee ou validee.

## Resultat a rapporter

Repondre simplement avec l un des deux formats :

- `P31 Fusion OK` : les trois bacs ouverts sont visibles et propres.
- `P31 Fusion KO : <ce qui est visible ou le message exact>`.

## Limites maintenues

`fusion-validated` ne sera accorde qu apres ce retour. `print-validated` reste
faux jusqu a une impression et des mesures reelles.

## Resultat humain

`P31 Fusion OK` recu le 2026-07-11. Les trois bacs ouverts sont observes. Le smoke est `fusion-validated`; aucune validation d impression n est deduite.