# ADR-0041 - Pont CAD IR explicite pour une selection locale P21

## Statut

Accepte pour P28 par validation humaine explicite le 2026-07-11.

## Date

2026-07-11

## Carte liee

- `P28-GATE - Materialiser une selection locale dans Fusion`

## Contexte

P23 a P27 permettent de composer localement une boite, comparer des variantes P21 et choisir explicitement une proposition. ADR-0040 limite volontairement cet export a une CAD IR metadata-ready : la selection est traçable mais Fusion ne peut pas creer une scene car la liste `components` est vide.

P28 est autorisee pour un raccord borne vers le pipeline Fusion existant. Le moteur Python doit rester la source de verite : Fusion ne doit ni reclasser les variantes, ni recalculer un placement, ni appliquer de tolerance nouvelle.

## Options

### Option A - Lire directement les metadonnees BoxFill dans Fusion

- Avantages : peu de donnees dupliquees dans la CAD IR.
- Inconvenients : pousse la logique de selection et de conversion dans l adaptateur Fusion.
- Risques : divergence moteur/Fusion et tests hors Fusion plus faibles.
- Compatibilite MVP : faible.

### Option B - Convertir la selection resolue en composants CAD IR standards

- Avantages : reutilise exactement le contrat `rectangular_blank` deja supporte par Fusion ; conversion testable hors Fusion ; aucune logique P21 dans l add-in.
- Inconvenients : les premiers composants ne sont que des enveloppes de modules.
- Risques : un utilisateur pourrait les prendre pour des bacs finis si les limites ne sont pas visibles.
- Compatibilite MVP : forte.

### Option C - Conserver une selection non materialisable

- Avantages : aucun nouveau raccord CAD.
- Inconvenients : bloque la validation du chemin de bout en bout.
- Compatibilite MVP : insuffisante apres autorisation P28.

## Decision

Adopter l option B : `export_from_draft` transforme chaque module imprimable du plan BoxFill deja resolu en un composant CAD IR `rectangular_blank`.

- Les origines et dimensions sont copiees telles quelles depuis le plan selectionne.
- Chaque composant porte l identifiant de variante et le marqueur `p28_selected_module_blank.v0`.
- Aucun mur, fond, cavite, encoche, tolerance, score ou placement n est infere par ce pont.
- Fusion consomme les composants par son pipeline CAD IR existant ; aucun comportement special P21 n est ajoute a l add-in.
- La commande `export-local-composer-selection` et le preparateur `prepare_local_composer_selection_test.ps1` produisent le scenario de smoke reproductible.

## Consequences

### Positives

- Le parcours local selection -> CAD IR -> Fusion est testable de bout en bout sans changer le solveur ni l add-in.
- La trace de la decision reste dans la selection et dans les metadonnees de chaque composant.
- Le contrat Fusion ne depend pas du format interne de P21.

### Negatives

- Le resultat Fusion P28 montre des blocs/enveloppes, pas des bacs ergonomiques finis.
- La commande CLI P28 est volontairement limitee aux starters locaux ; le Studio existant exporte deja le draft actif via son API locale.

### Risques

- Le smoke Fusion humain reste indispensable : aucune execution API Fusion n est prouvee par les tests Python.
- Aucune impression, slicer, ergonomie, tolerance reelle ou export imprimable automatique n est validee.

## Alternatives refusees

- Extension du solveur P21 : hors scope, le plan est deja resolu.
- Generation de cavites ou de parois dans ce lot : hors scope et non justifiee par le plan de volumes P20/P21.
- Calcul de la scene dans Fusion : refuse, car Fusion resterait alors une seconde source de verite.

## Suivi

- Tests Python : l export P28 est lu par `generation_plan_from_cad_ir` et la CLI produit une scene de selection valide.
- Smoke Fusion : preparer l add-in et les settings avec `scripts/fusion/prepare_local_composer_selection_test.ps1`, puis observer la scene dans Fusion.
- Statut `fusion-validated` interdit tant que cette observation humaine n est pas rapportee.
- Gate impression maintenue.