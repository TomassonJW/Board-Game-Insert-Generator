# Quality Rules

## Regles de conception

- Toutes les dimensions sont en millimetres.
- Les axes X, Y et Z doivent rester explicites.
- Le moteur pur ne depend pas de Fusion 360.
- Le JSON n'est pas le modele interne.
- Les tolerances ne sont pas codees en dur dans le layout.
- Les cellules theoriques ne sont pas des corps imprimables.
- Une strategie de layout reservee ne doit pas etre acceptee tant qu'elle n'est
  pas implementee et testee.
- Les modules composites ne recoivent pas de jeu entre primitives internes
  soudees.
- Les valeurs de tolerance doivent rester visibles et ajustables.

## Regles de code

- Preferer des dataclasses typees et lisibles.
- Garder les erreurs comprehensibles pour un utilisateur technique.
- Tester le moteur hors Fusion.
- Eviter les dependances externes tant que la V0 n'en a pas besoin.
- Ne pas introduire de framework structurant sans ADR.
- Garder les fonctions petites et deterministes.
- Ne pas importer Fusion 360 dans le coeur Python.

## Regles de configuration

- Aucun secret dans le depot.
- Les exemples doivent etre realistes mais non lies a des donnees sensibles.
- Les valeurs par defaut doivent etre prudentes.
- Les champs optionnels doivent avoir un comportement documente.
- Les unites doivent etre explicites.

## Regles de validation

- Refuser les dimensions negatives ou nulles.
- Refuser une hauteur utile incoherente avec la boite.
- Refuser les quantites nulles.
- Signaler les layouts impossibles avec un message lisible.
- Ne jamais pretendre qu'un layout actuel est optimal.
- Distinguer erreur bloquante et warning.

## Regles de documentation

- Distinguer ce qui est implemente, experimental, prevu ou a valider par
  impression reelle.
- Documenter toute decision structurante par ADR.
- Garder les documents exploitables par un autre developpeur ou agent.
- Eviter la documentation decorative.
- Mettre a jour `docs/STATUS.md` apres toute mission significative.
- Mettre a jour `docs/BACKLOG.md` si une carte change ou si une tache est
  decouverte.
- Mettre a jour `docs/NEXT_ACTIONS.md` a la fin de chaque mission.
- Ajouter un log dans `docs/LOGS/` si l'orientation, le statut ou un jalon change.

## Regles de tests

Commande minimale :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Commande d'exemple si CLI, rapports ou exemples changent :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Si les tests ne peuvent pas etre lances, le compte rendu doit dire pourquoi.

## Garde-fous documentaires automatises

Le test `tests/test_project_documents.py` verifie maintenant les fichiers de
pilotage critiques et les sections minimales qui permettent a un agent de
reprendre le projet sans contexte oral.

Fichiers critiques couverts :

- `AGENTS.md` ;
- `docs/AUTONOMY_PROTOCOL.md` ;
- `docs/EXECUTION_LOOP.md` ;
- `docs/HUMAN_GATES.md` ;
- `docs/VALIDATION_MATRIX.md` ;
- `docs/STATUS.md` ;
- `docs/NEXT_ACTIONS.md` ;
- `docs/BACKLOG.md` ;
- `docs/ROADMAP.md` ;
- `docs/ARCHITECTURE.md` ;
- `docs/QUALITY_RULES.md` ;
- `docs/DECISIONS/README.md` ;
- `docs/LOGS/README.md`.

Le test echoue avec un message lisible de type `Fichiers de pilotage manquants`
ou `Sections de pilotage manquantes`.

## Regles d'impression reelle

- Ne pas declarer stable un jeu fonctionnel non imprime.
- Utiliser `docs/CALIBRATION_PROTOCOL.md` pour preparer les coupons, mesures et
  criteres OK/KO.
- Documenter le filament, l'imprimante, la buse, la hauteur de couche et le
  slicer si une mesure d'impression influence les valeurs.
- Garder les tolerances par defaut prudentes tant que les calibrations sont
  insuffisantes.
- Toute modification des valeurs de tolerance par defaut reste une gate humaine.

## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.

## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.

## Regles P57 de partition Fusion-only

- Une solution construite contient uniquement les groupes de bacs constructibles et les complements exacts explicitement demandes.
- `automatic_body_count` doit toujours rester a zero.
- Les jeux contre la boite et entre corps sont des vides techniques non materialises.
- Toute enveloppe finale doit repasser le validateur P55 sans modifier les cavites.
- Une impossibilite doit fournir code, message, reference et action corrective.
- Le solveur borne peut scorer des candidats, mais ne doit jamais revendiquer une optimalite globale.
- Le plan P57 ne constitue ni une CAD IR, ni une validation Fusion, ni une validation d impression.
## Regles P58 de resultat

- Une vue geometrique doit citer le digest du plan P57 dont elle derive.
- Les primitives SVG utilisent les bornes monde et cavites transformees par Python.
- Une partition impossible ne doit jamais etre dessinee comme une solution.
- Toute modification du projet invalide le dernier resultat ; une sauvegarde sans modification ne l invalide pas.
- Les noms utilisateur accompagnent les identifiants stables dans le resultat.
- Le rendu P58 ne vaut ni CAD IR, ni validation Fusion, ni validation d impression.
## Regles P59 de materialisation Fusion

- La CAD IR P59 doit citer le digest P57 et refuser un plan obsolete.
- Le nombre de composants CAD doit egaler le nombre de corps finaux demandes.
- Toute cavite de bac vient de P55 ; aucune cavite n est redimensionnee dans Fusion.
- Les regions libres, fillers historiques et jeux techniques ne deviennent jamais des bodies.
- `automatic_body_count` reste zero dans le plan, la CAD IR et la palette.
- La synchronisation produit utilise `compact_only` et le registry d ownership BGIG.
- Generate ne remplace rien implicitement ; regenerate preserve les objets non-BGIG.
- Une erreur de bridge doit retourner une reponse versionnee et actionnable.
- `implemented` ne vaut ni `fusion-validated`, ni `print-validated`.

## Regles produit acceptees apres revue P60

- Un inspect sain au demarrage ne produit aucun message global.
- Aucun enum, digest, milestone ou nom de moteur ne doit apparaitre au premier niveau utilisateur.
- Toute edition distingue source courante, derives, plan obsolete et scene materialisee.
- Une proposition partielle reste visible mais non materialisable par defaut.
- `Auto`, `Cible` et `Fixe` ont des semantiques testees et distinctes.
- Une reservation de plateau ne peut percer silencieusement cavite, fond ou paroi.
- Une suggestion de cale ne cree jamais de corps sans confirmation.
- Une erreur doit nommer la contrainte en conflit avant de conseiller d agrandir la boite.

## Regles P64 de solveur volumetrique

- La recherche d arrangements XY et d etages Z est deterministe, bornee et ne
  revendique jamais une optimalite globale.
- Les budgets de recherche sont exposes par le resultat ; une troncature reste
  observable et ne transforme pas une heuristique en preuve d optimum.
- `Auto`, `Cible` et `Fixe` sont distincts par axe : seule une dimension fixe
  est dure, une cible peut devier avec une raison explicite.
- Chaque etage superieur doit satisfaire son recouvrement d appui minimal et la
  sequence de retrait est ordonnee du haut vers le bas.
- `proposal_with_residuals` reste visible, mais est strictement non materialisable
  et ne peut appeler Fusion ; `impossible` n est jamais dessine comme solution.
- Les zones residuelles et les suggestions sont non imprimables et non mutantes ;
  `automatic_body_count` reste zero dans le plan, la CAD IR et la palette.
- Les reservations P63 ne peuvent toucher que les corps de l etage superieur
  effectivement intersecte ; les corps sous-jacents restent inchanges.
## Regressions P64 runtime

Les validations P64 doivent couvrir au minimum :

- une sequence 4, 5 puis 6 bacs de cartes avec un bac haut, sans perte de
  solvabilite quand un niveau Z devient necessaire ;
- un corps haut traversant plusieurs intervalles Z a cote de piles courtes ;
- les limites d enveloppe revalidees dans le repere local apres rotation XY ;
- la profondeur utile conservee sous un ou plusieurs plateaux superposes ;
- le blocage si la compensation perce le fond minimal ;
- des noms de corps Fusion uniques malgre des libelles utilisateur identiques ;
- determinisme, non-collision, appui, conservation et zero corps automatique.

## Orthotypographie française de la palette

- Tout texte visible par l’utilisateur emploie les accents français corrects.
- Les sources UI sont encodées en UTF-8 sans BOM.
- La palette conserve `<meta charset="utf-8">`.
- Les identifiants, clés, enums et protocoles restent indépendants des libellés.
- Les tests refusent les signatures de mojibake `Ã`, `Â` et `�`.
- Un nom utilisateur accentué doit survivre au roundtrip projet/bridge.
- Les nouveaux textes respectent la règle dès P44-M003 ; P44-M006 corrige
  exhaustivement l’historique.
- Une observation Fusion reste requise pour qualifier le rendu réel.

- P44-M003 impose exactement quatre onglets primaires ; une interversion X/Y
  est locale, ne crée aucune action bridge et ne modifie jamais une origine
  ni une valeur Z ; pour un conteneur, elle échange le contrat complet de ses
  axes X/Y.


- P44-M004 : la composition parent/enfant ne doit pas indexer root.children ;
  les identifiants DOM sont dérivés des identifiants métier de chaque parent et
  enfant. Le contrôle global de mode refuse toute valeur Cible/Fixe absente,
  les axes historiques mixtes restent traçables sous Personnalisé, et aucun
  changement de collection ou d’action bridge n’est autorisé.

- P44-M004V2 : une densité acceptable est structurelle. La palette doit exposer
  une seule commande de densité, utiliser jusqu’à 1180 px, maintenir les champs
  primaires en rangées et conserver des cibles principales de 40 px. Les calculs
  secondaires peuvent être repliés, jamais supprimés. Les libellés nouveaux ou
  touchés sont écrits en français UTF-8 accentué. Aucun compactage ne peut
  modifier schéma, bridge, solveur, tolérance, géométrie ou scène Fusion.

- P44-M004V2H01 : les commandes collantes utilisent la hauteur réelle de
  l’en-tête et ne doivent ni chevaucher les onglets ni masquer le contenu. Un
  nouveau toast annule le minuteur précédent. Confirmation : 3 secondes ;
  avertissement ou erreur : 6 secondes. Les tests DOM verrouillent offset,
  temporisation et position haute.

## Règles P64 multi-solveurs

- `Calcul impossible` ne représente jamais un simple épuisement heuristique.
- `proven_impossible` exige une preuve et un domaine explicitement couverts.
- Aucun seuil de quantité de conteneurs ne force un étage ; les scénarios 2/8/32
  sont des régressions, jamais des règles produit.
- Les profils d'effort sont bornés et monotones : un profil plus profond ne
  retire aucune famille ou option autorisée au profil précédent.
- Toute stratégie passe par le même validateur final.
- Les métriques distinguent non applicable, zéro réel et donnée non collectée.
- Le temps réel ne participe pas aux digests déterministes.
- Une réponse obsolète ne peint ni résultat, ni diagnostic, ni métrique.
- Une vue développeur ne vole pas focus/sélection et ne reconstruit pas le DOM.
- Une finition échouée conserve la solution certifiée et ne devient pas un échec
  de faisabilité.
- Aucune grille, cale, corps ou relaxation implicite ne peut être ajoutée par un
  profil d'effort.

Les régressions P64-H04+ couvrent corpus simple/dense, déterminisme, budgets,
annulation, validation commune, non-collision, appui, retrait, réservations,
zéro corps automatique et parité du baseline.


## Règles P64-A02 — calcul étagé et capacité

- Chaque analyse locale, plan global, finalisation et carte de capacité cite les
  digests exacts de ses entrées.
- Une réponse stale ne modifie aucun état visible et ne devient jamais
  matérialisable.
- Une shortlist UI, y compris top 3, ne limite jamais silencieusement la
  frontière consommable par le solveur.
- Un score classe uniquement des variantes déjà certifiées ; ses composantes
  restent exposables séparément et aucune somme ne masque une contrainte dure.
- Modifier un asset n'invalide pas les autres conteneurs sans dépendance réelle ;
  modifier un conteneur ne réécrit jamais ses assets source.
- Un plan global certifié n'est pas matérialisable avant finalisation explicite
  lorsque le nouveau cycle P64-L03 est actif.
- Une finalisation échouée conserve le plan global certifié et ne devient ni
  impossible ni no_solution_within_budget.
- InternalOpportunityZone, BoxReserveBay et CapacityOpportunityMap restent des
  données dérivées non imprimables.
- Réutiliser une pose monde ne réutilise jamais un ancien certificat.
- Sans BoxReserveBay certifiée, ajouter un conteneur impose un solve global.
- Aucun asset, séparateur, conteneur, corps ou cale n'est créé automatiquement.
- Les gates Fusion et impression restent distinctes ; aucune valeur physique
  n'est calibrée par une observation UI.
