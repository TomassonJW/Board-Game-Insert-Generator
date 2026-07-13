# P65-M004 - Contrat fonctionnel des explications d Apercu

Date de cadrage : 2026-07-13
Statut : `implemented`, `automated-validated`, `fusion-retest-required`
Release cible : palette Fusion `0.1.19`
Capabilities : `C-FUSION-UI`, `C-QUALITY`
Dependances : P64 et P65-M001 a P65-M003 integres ; ADR-0055, ADR-0059 et ADR-0060 acceptees.

## But

P65-M004 rend l onglet `Apercu` lisible sans exposer les codes ou structures
internes du solveur. L utilisateur doit comprendre :

1. ce que mesure le score et ce qu il ne garantit pas ;
2. si les etages et les plateaux ont un appui calcule ;
3. dans quel ordre retirer les elements superieurs quand cet ordre existe ;
4. si un volume residuel reste a decider, sans creer une fausse solution ;
5. qu une suggestion reste optionnelle et ne cree aucun corps ;
6. quelle action est disponible : modifier, recalculer, materialiser ou exporter.

## Contrat de donnees et de presentation

- La projection Python additive versionnee `bgig.preview_explanations.v1` traduit
  les donnees deja presentes dans `bgig.partition_result_view.v1`.
- Elle ne modifie jamais le plan P64, le score, les placements, les appuis,
  les retraits, les residuels, les suggestions ni la materialisabilite.
- Le JavaScript affiche cette projection ; il ne traduit pas de code solveur et
  ne reconstitue aucune formule.
- Aucun digest, enum, nom de fonction, code Python ou valeur brute comme
  `supported_by_requested_bodies` ne parait au premier niveau.

## Experience Apercu

- Le score est presente comme une indication comparative : les quatre
  sous-criteres sont nommes et une aide locale explique qu il ne remplace pas
  une verification physique.
- L appui des etages et des plateaux est formule avec une phrase utilisateur,
  et les rapports de couverture restent dans le detail si utiles.
- L ordre de retrait est une liste courte et nommee ; son absence est expliquee
  sans inventer de sequence.
- Une proposition partielle isole le volume residuel et les suggestions dans
  une zone de decision explicite ; aucune suggestion ne devient un corps.
- `Exporter les imprimables` est l action locale primaire de l Apercu.
- `Materialiser dans Fusion` reste l unique action persistante, voisine de
  `Recalculer` et gardee par une proposition complete et a jour. L Apercu ne
  duplique pas ce bouton ni `Recalculer`.

## Hors scope

P65-M004 ne change ni solveur, heuristique, score, tolerance, cavite,
reservation, placement, CAD IR, scene Fusion, export ni schema source. Il ne
creee aucun corps, support, separateur ou cale automatiquement.

## Cas d acceptation

1. proposition complete : score et appui sans fuite technique ;
2. plusieurs etages : appui et ordre de retrait nommes ;
3. plateau/livret : statut d appui traduit, jamais enum brut ;
4. proposition partielle : residuel et suggestion explicites, sans
   materialisation ;
5. plan obsolete : les actions locales ne contournent pas la barre persistante ;
6. aucune suggestion : formulation honnete et courte ;
7. la palette ne contient plus les libelles techniques connus au premier niveau ;
8. les tests result view, bridge, DOM, compilation et la suite complete restent
   verts ; `adsk` reste absent du coeur Python.

## Definition of Done

Le lot est termine lorsque la projection de presentation est testee, que
l Apercu utilise exclusivement ses textes utilisateur, que les actions finales
respectent ADR-0060, que le package 0.1.19 est verifie localement, et que le
pilotage est mis a jour sans pretendre a une validation Fusion ou impression.
