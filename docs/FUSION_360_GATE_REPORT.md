# Gate report - Premiere integration Fusion 360

## Declencheur

La Phase 3 est consolidee : le moteur Python pur charge une configuration JSON,
valide les contraintes de base, genere un layout rectangulaire simple, applique
les tolerances par face, expose les profils d'impression et documente un
protocole de calibration physique.

La prochaine phase de roadmap concerne Fusion 360. Cette transition atteint la
gate humaine `Premiere integration Fusion 360`, car un adaptateur Fusion pourrait
facilement aspirer la logique metier ou creer une promesse CAD/impression trop
tot.

## Etat actuel du moteur

Implemente et teste par code :

- chargement JSON V0 strict ;
- validation de dimensions, unites, quantites, hauteurs et strategie layout ;
- strategies `row_fill` et `grid` ;
- comparaison simple de layout dans les rapports ;
- separation `Cell` theorique / `PrintableBody` imprimable ;
- classification des faces rectangulaires simples ;
- application explicite des tolerances par role de face ;
- profils d'impression opt-in resolus en `ToleranceProfile` ;
- rapports Markdown/JSON ;
- commande CLI `diagnose` ;
- protocole de calibration physique documente.

Experimental ou incomplet :

- `row_fill` et `grid` ne sont pas des optimiseurs ;
- les valeurs de tolerance et profils ne sont pas valides par impression ;
- `PrimitiveVolume`, `CompositeModule`, `Cavity` et `Feature` existent comme
  concepts mais ne pilotent pas encore une generation complete ;
- les roles `internal` et `welded` sont regles mais pas detectes par un moteur
  composite ;
- aucune representation CAD-agnostic dediee aux operations Fusion n'est encore
  stabilisee ;
- aucun adaptateur Fusion, aucun STL et aucun 3MF n'existent.

## Ce qui est pret

- Le coeur Python reste independant de Fusion 360.
- Aucun import `adsk` n'est present dans `src/board_game_insert_generator/`.
- Les donnees necessaires a des blanks rectangulaires existent : origine, taille,
  identifiant, offsets, warnings et metadata de rapport.
- Les rapports permettent de diagnostiquer layout et tolerances avant CAD.
- Les tests unitaires couvrent le moteur hors Fusion.
- Les limites physiques sont documentees comme non validees par impression.

## Ce qui manque avant un adaptateur executable

- Un contrat CAD-agnostic explicite pour la premiere sortie Fusion.
- Une decision sur la granularite de sortie : `PrintableBody` direct ou objet
  intermediaire dedie.
- Une specification de nommage des composants et corps Fusion.
- Une convention d'origine et d'axes a transmettre a Fusion.
- Une politique minimale pour rayons/chamfers : appliquer les defaults ou les
  reporter.
- Une checklist de verification Fusion : composants, dimensions, origine,
  units, noms et warnings.
- Une politique claire sur exports : les exclure de la premiere integration ou
  demander une gate separee.

## Options techniques

### Option A - Continuer sans Fusion et consolider le contrat CAD-agnostic

- Principe : faire `P4-M001` avant tout code Fusion executable.
- Avantages : risque faible, coeur pur preserve, tests locaux possibles.
- Inconvenients : aucun composant Fusion visible tout de suite.
- Risques : peut retarder la decouverte des contraintes reelles de l'API Fusion.

### Option B - Autoriser un squelette d'adaptateur Fusion non productif

- Principe : creer la structure d'adaptateur sans generation CAD exploitable.
- Avantages : prepare l'installation et isole le futur code Fusion.
- Inconvenients : peut encourager une integration avant contrat stable.
- Risques : confusion entre squelette et fonctionnalite utilisable.

### Option C - Autoriser une premiere generation de blanks rectangulaires

- Principe : generer composants et corps rectangulaires simples dans Fusion.
- Avantages : feedback CAD rapide.
- Inconvenients : plus risque, depend de Fusion, peut masquer les limites du
  contrat intermediaire.
- Risques : logique metier dupliquee dans l'adaptateur, validation physique
  confondue avec validation CAD.

## Recommandation

Recommandation : choisir l'option A.

Autoriser d'abord `P4-M001 - Definir le contrat de representation intermediaire
CAD`, sans import Fusion et sans generation executable. Cette mission doit
stabiliser les objets que Fusion recevra : blanks rectangulaires, metadata de
nommage, axes, unites, warnings et contraintes de validation.

Ne pas autoriser encore :

- add-in Fusion executable ;
- script Fusion avec import `adsk` ;
- export STL/3MF ;
- cavites, couvercles, modules composites ou mecanismes ;
- modification des valeurs de tolerance par defaut.

## Risques

- Risque d'aspiration metier par Fusion : l'adaptateur pourrait recalculer layout
  ou tolerances s'il ne recoit pas un contrat clair.
- Risque de promesse utilisateur : un blank Fusion visible peut etre percu comme
  imprimable alors que l'impression n'est pas validee.
- Risque de dette CAD : une premiere implementation sans contrat peut fixer de
  mauvais noms, axes ou conventions d'unites.
- Risque de debug lent : les erreurs Fusion sont plus couteuses a diagnostiquer
  que les tests Python purs.

## Criteres d'acceptation pour autoriser la premiere integration Fusion

Avant d'autoriser un adaptateur Fusion executable, il faut valider :

- contrat CAD-agnostic documente et teste ;
- aucune logique layout/tolerance dans l'adaptateur ;
- aucune importation `adsk` dans le coeur `src/board_game_insert_generator/` ;
- suite unitaire coeur verte ;
- exemple CLI Markdown et JSON reproductible ;
- checklist de verification Fusion ecrite ;
- perimetre limite a des blanks rectangulaires simples ;
- aucun STL/3MF dans la premiere integration sauf gate separee ;
- statut experimental explicite ;
- validation physique exclue du jalon.

## Validation demandee

Decision humaine attendue :

1. Autoriser `P4-M001` uniquement : contrat CAD-agnostic sans Fusion executable.
2. Autoriser un squelette d'adaptateur non productif apres `P4-M001`.
3. Autoriser directement une premiere generation Fusion de blanks rectangulaires.
4. Reporter toute progression Phase 4 et demander une consolidation supplementaire.

Decision recommandee : option 1.