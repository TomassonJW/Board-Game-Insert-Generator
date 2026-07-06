# Next Actions

Derniere mise a jour : 2026-07-06

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

Statut : `required_before_next_fusion_geometry`.

P8-M001/P8-M002 et P10-M008 sont termines dans le perimetre coeur Python pur,
configuration, validation, rapports, placement grille abstrait et CAD IR metadata.
P11-M001 code la generation Fusion compacte depuis placements grille, mais attend
le smoke test manuel Fusion avant statut `fusion-validated`.

Action humaine requise avant toute mission qui genere reellement : grille 3D,
layers, vue eclatee, demi-lune courbe, scoop interne, fillet/conge, fond arrondi,
geometrie courbe, module composite ou export STL/3MF dans Fusion.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee apres `P11-M001` tant que le smoke test Fusion compact n'est pas valide.
La boucle asset-first produit maintenant candidats, variante recommandee, plan de
modules concret, placement grille greedy borne et generation Fusion compacte
codee pour ces placements.

Prochaine action recommandee : preparer une gate si l'on veut passer a un solveur
complexe, a du backtracking, a une optimisation globale, a des modules composites
ou a une generation Fusion volumetrique reelle.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

`P11-M001V - Smoke test humain Fusion de la vue compacte grille`.

- Capability : `C-FUSION-COMPACT`, `C-FUSION-EXPLODED`, `C-GRID-3D`.
- Objectif : choisir explicitement si et comment une grille/layer doit produire
  une vue Fusion reelle.
- Statut : `blocked` jusqu'a validation humaine.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.