# P64-L09U-R3 — runbook profondeur, réservations locales et budget

## Objectif

Corriger de bout en bout les trois défauts humains de 0.1.73, sans perdre le
nouveau chemin de matérialisation rapide et progressive :

1. conserver la profondeur calibrée des cavités après finalisation ;
2. produire des encastrements locaux et étagés pour plusieurs plateaux/livrets ;
3. rendre impossible ou explicitement expliquée une durée supérieure au
   plafond affiché.

Cible initiale : `0.1.74`.

## Autorité

- `docs/P64_L09U_R2_V_0173_HUMAN_KO_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0099-profondeur-calibree-et-reservations-superieures-locales.md` ;
- `docs/DECISIONS/ADR-0098-plan-minimal-exact-et-corps-fusion-transitoire.md` ;
- `docs/DECISIONS/ADR-0093-recalcul-explicite-reservations-optimisees-et-fermeture-hybride.md`.

ADR-0099 supersède les décisions précédentes uniquement pour l'ancrage Z final
et la composition locale des réservations.

## Lectures obligatoires avant mutation

1. `AGENTS.md` ;
2. `docs/PILOTAGE_CURRENT.md` ;
3. `docs/NEXT_ACTIONS.md` ;
4. `docs/HUMAN_GATES.md` ;
5. les quatre autorités ci-dessus ;
6. `src/board_game_insert_generator/expandable_envelope.py` ;
7. `src/board_game_insert_generator/top_inset_reservation.py` ;
8. `src/board_game_insert_generator/partition_cad.py` ;
9. `src/board_game_insert_generator/partition_result_view.py` ;
10. le certificat composite et les tests directement concernés.

## Frontières non négociables

- Aucun benchmark, holdout, corpus ou tournoi solveur.
- Ne jamais modifier ni versionner un projet personnel.
- Les projets personnels peuvent être rejoués en lecture seule, avec SHA-256
  avant et après.
- Ne pas inventer de valeur physique : utiliser les jeux, parois et fonds déjà
  résolus par le projet.
- Ne pas déplacer une cavité en X/Y, la tourner ou la redimensionner.
- La résolution Z finale est déterministe, jamais un degré de liberté de
  fermeture.
- Plateaux et livrets restent des réservations virtuelles.
- Préserver le corps BRep transitoire, l'absence de Combine rectangulaire, le
  rollback global et la respiration Fusion entre modules.
- Les jobs annulables, miniatures de variantes et l'épaisseur distincte de
  séparateur restent hors R3.

## Mission A — tracer la divergence exacte

- Construire des fixtures anonymisées couvrant :
  - corps minimal puis agrandi en Z sans réservation ;
  - même corps sous une réservation locale ;
  - deux réservations disjointes de tailles différentes ;
  - deux réservations partiellement recouvrantes ;
  - deux réservations réellement empilées.
- Tracer pour chaque cavité : dimensions et origine Z au minimum, au final,
  dans la CAD IR, dans l'aperçu et dans le plan Fusion.
- Prouver précisément où `10,6 mm` devient une coupe plus profonde.
- Prouver si le cumul global vient du plan de réservation, de l'intersection,
  du CAD IR ou de l'adaptateur Fusion.

## Mission B — conserver le calibre et résoudre l'ancrage Z

- Supprimer l'augmentation de profondeur
  `canonical_asset_depth_plus_localized_top_inset`.
- Conserver les dimensions calibrées exactes.
- Résoudre l'origine Z finale :
  - `open_top` sans réservation recouvrante ;
  - `below_top_inset` sous la découpe locale concernée.
- Certifier le fond restant et la séparation supérieure avec les paramètres
  physiques existants.
- Refuser explicitement tout plan qui ne peut pas conserver ces deux épaisseurs.
- Étendre le témoin final, l'aperçu et la CAD IR avec les preuves d'ancrage.

## Mission C — composer plusieurs réservations localement

- Conserver une coupe distincte par réservation et par corps intersecté.
- Ne cumuler les hauteurs que là où les empreintes se recouvrent réellement.
- Produire les paliers Z attendus lorsque deux éléments plats sont empilés.
- Éliminer toute utilisation géométrique d'un rectangle englobant ou d'une
  profondeur totale globale.
- Certifier identité, empreinte, intervalle Z, ordre et intersections de chaque
  réservation.

## Mission D — faire respecter le plafond affiché

- Distinguer dans les mesures :
  - budget contractuel de recherche ;
  - plafond mural ;
  - terminaison ou nettoyage après arrêt.
- Ajouter des contrôles de deadline dans toutes les boucles longues concernées.
- Ne jamais afficher une durée supérieure au plafond sous un libellé
  « maximum » sans décomposition explicite.
- Tester avec une horloge contrôlée et une terminaison volontairement lente.
- Ne pas masquer une impossibilité ou un arrêt borné comme épuisement de budget.

## Mission E — non-régression et livraison

- Tests ciblés d'abord, puis suite complète autorisée avec `PYTHONPATH=src`.
- Rejouer `CasLimite01+`, `CasLimite02+` et `CasLimite01++` en lecture seule
  lorsqu'ils existent.
- Vérifier que le minimum et le final conservent exactement les profondeurs de
  cavité attendues.
- Vérifier deux plateaux différents dans l'aperçu, la CAD IR et le plan Fusion.
- Vérifier zéro Combine rectangulaire et le rendu progressif par module.
- Aligner pilotage, version, preflight, préparateur et recette de gate.
- Intégrer directement dans `main`, vérifier le SHA distant, installer la
  candidate puis préparer la gate humaine.

## Critères d'acceptation automatisés

- La profondeur finale d'une cavité égale sa profondeur calibrée source.
- L'exemple `10 mm + 0,6 mm` reste `10,6 mm`, sans constante codée pour ce cas.
- Le surplus Z modifie l'origine Z ou la matière restante, jamais la profondeur.
- Une réservation recouvrante déplace la cavité sous sa coupe locale et conserve
  la séparation canonique.
- Deux réservations disjointes ne cumulent pas leur profondeur.
- Deux réservations recouvrantes produisent des paliers limités à leur
  intersection.
- Le résultat, l'aperçu, la CAD IR et le plan Fusion portent les mêmes mesures.
- Un plafond affiché de `20 s` n'est pas rapporté comme `24 s` sans séparation
  explicite des phases.
- Le chemin Fusion transitoire et progressif de 0.1.73 ne régresse pas.

## Gate V

La gate finale reste humaine. Thomas vérifie au minimum :

1. `CasLimite01+` avec et sans plateau ;
2. `CasLimite02+` avec ses deux plateaux différents ;
3. `CasLimite01++` ;
4. profondeurs mesurées avant et après finalisation ;
5. encastrements locaux et paliers des plateaux ;
6. temps, fidélité aperçu/Fusion et matérialisation progressive.

Codex ne promeut jamais seul `fusion-validated` ou `print-validated`.
