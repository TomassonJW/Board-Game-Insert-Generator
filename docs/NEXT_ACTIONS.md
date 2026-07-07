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

Statut : `manual_validation_required` pour la prochaine extension produit ; P12-UI-M002V7 est validee fonctionnellement.

La gate humaine `P12-NEXT-GATE` a ete levee pour lancer `P12-UI-M002+` vers une
UI Fusion parametrique V0. La mission code une commande Fusion enrichie avec
source CAD IR, source config BGIG, overrides parametriques, actions `generate`,
`regenerate` et `clear_bgig_scene`, generation CAD IR temporaire et nettoyage
conservateur des objets BGIG tagues.

Action humaine recommandee : smoke test court du reporting `inspect_bgig_scene` corrige avant toute nouvelle extension produit.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee apres la correction du reporting inspect. La prochaine action est un smoke test humain court du rapport `inspect_bgig_scene`.

## Mission bloquee par gate

`P12-UI-M002V7R - Verifier le reporting inspect BGIG deduplique`.

- Capability : `C-FUSION-UI`.
- Milestone : M14 Usable beta.
- Objectif : verifier que le rapport standard `inspect_bgig_scene` affiche une seule racine BGIG reelle, des entites taguees uniques, zero faux positif `BGIG-looking untagged` quand les objets sont tagues, puis que `generate`/`regenerate`/`clear` restent fonctionnels.
- Statut : `manual_validation_recommended`, apres validation fonctionnelle P12-UI-M002V7 et correction reporting codee.

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
