# Next Actions

Derniere mise a jour : 2026-07-07

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici, sauf gate humaine.

## Politique active - Integration Git autonome

Statut : `active`.

Le chemin standard est `direct-to-main` : une mission doit etre testee, commitee,
integree directement dans `main`, puis poussee vers `origin/main` avant selection
d'une mission suivante. Les pull requests sont reservees aux cas de repli :
protection GitHub, review imposee, conflit, divergence non triviale, risque
structurant, authentification absente ou refus de push direct.

## Gate humaine active

Statut : `manual_validation_required`.

La gate humaine `P12-NEXT-GATE` a ete levee pour lancer `P12-UI-M002+` vers une
UI Fusion parametrique V0. La mission code une commande Fusion enrichie avec
source CAD IR, source config BGIG, overrides parametriques, actions `generate`,
`regenerate` et `clear_bgig_scene`, generation CAD IR temporaire et nettoyage
conservateur des objets BGIG tagues.

Action humaine requise : `P12-UI-M002V3` smoke test Fusion avant toute nouvelle
extension produit.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee apres P12-M002+. La
prochaine action est une validation humaine Fusion.

## Mission bloquee par gate

`P12-UI-M002V3 - Valider generate/regenerate/clear non cumulatifs`.

- Capability : `C-FUSION-UI`.
- Milestone : M14 Usable beta.
- Objectif : lancer l'add-in dans Fusion, verifier les champs parametriques,
  tester que `generate` refuse les doublons, que `regenerate` remplace sans
  doublon, que `clear_bgig_scene` reste visible et que les objets non BGIG sont preserves.
- Statut : `manual_validation_required`, apres correction P12-M002V3 codee.

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.