# ADR-0055 - Add-in Fusion 360 comme produit MVP unique

## Statut

Accepte le 2026-07-12 par decision humaine explicite : Fusion uniquement.

## Date

2026-07-12

## Cartes liees

- P54-R - Realignement Fusion-only
- P56 - Editeur de projet embarque dans Fusion
- P57 - Solveur de partition et expansion
- P58 - Resultat et preview dans la palette Fusion
- P59 - Materialisation et synchronisation de scene
- P60 - Acceptance end-to-end dans Fusion

## Contexte

La trajectoire P23 puis ADR-0042 a fait du Studio web local la surface produit
principale et de Fusion une surface secondaire. Cette interpretation ne
correspond pas au produit voulu : BGIG est un module Fusion 360. Une personne
doit installer l add-in, ouvrir Fusion et realiser le parcours complet sans
lancer un serveur Python, Vite ou un navigateur externe.

Le besoin Fusion-only ne remet pas en cause la frontiere technique saine du
projet. Le moteur de decision doit rester Python pur, testable hors Fusion et
sans import adsk. Fusion est a la fois le conteneur de l experience utilisateur
et l adaptateur CAD, mais la scene Fusion ne devient jamais la source de verite.

## Options

### Option A - Studio web principal et palette Fusion secondaire

Avantages : tests UI hors Fusion et libertes de layout web.

Inconvenients : deux applications, deux processus locaux, navigation hors de
Fusion et packaging contradictoire avec le produit attendu.

Decision : refusee et supersedee pour le MVP.

### Option B - CommandInputs Fusion uniquement

Avantages : implementation native simple et deja robuste pour les smoke tests.

Inconvenients : tableaux dynamiques, navigation progressive, apercus et grande
cardinalite deviennent difficiles a utiliser.

Decision : conservee comme mode expert, diagnostic et secours, pas comme
experience principale.

### Option C - Palette HTML embarquee dans l add-in Fusion

Avantages : experience unique dans Fusion, UI riche et dynamique, aucun serveur
local, bridge versionne vers le coeur Python et reutilisation du socle P32 deja
fusion-validated.

Inconvenients : lifecycle et tests du bridge Fusion plus exigeants, observation
Fusion humaine necessaire pour la qualification finale.

Decision : retenue.

## Decision

1. Le produit MVP est l add-in BoardGameInsertGenerator installe dans Fusion 360.
2. La palette HTML locale embarquee dans le dossier de l add-in est la surface
   principale : projet, boite, assets, groupes de bacs, plateaux/livrets,
   reglages, construction, resultat et export.
3. Aucun navigateur externe, serveur loopback, processus Vite ou application web
   separee n est requis pour utiliser le MVP.
4. Le coeur src/board_game_insert_generator reste CAD-agnostic, sans adsk et
   testable hors Fusion. Il normalise le projet, derive les cavites, resout la
   partition et produit le plan puis la CAD IR.
5. Le bridge de palette transmet des messages JSON versionnes. Il ne duplique ni
   solveur, ni tolerances, ni dimensionnement en JavaScript.
6. L adaptateur Fusion consomme la CAD IR et synchronise uniquement les objets
   BGIG tagues. La scene Fusion reste une projection regenerable, jamais la
   source de verite.
7. La commande CommandInputs existante reste accessible sous Reglages experts
   pour diagnostic, compatibilite, smoke et secours.
8. frontend/, local_composer.py, ADR-0040 et le parcours P23-P30 sont classes
   prototypes historiques hors MVP. Ils ne sont ni lances, ni packages, ni
   prolonges dans le chemin P56-P60.
9. Le contrat P55 cavites fixes / enveloppes extensibles reste valide dans le
   coeur pur. Sa route loopback est un adaptateur historique, pas une API produit.
10. P56-P60 sont redefinis autour d un parcours integralement observable dans
    Fusion.

Cette decision supersede ADR-0040 et ADR-0042 pour la surface MVP. Elle
supersede la clause Studio principal d ADR-0053 sans remettre en cause son
exigence de conformite produit avant acceptance.

## Consequences

### Positives

- Le produit correspond a l attente : installer un module et travailler dans
  Fusion.
- Il n existe qu un point d entree utilisateur et un seul packaging a livrer.
- Le coeur reste testable et maintenable hors Fusion.
- La palette P32, son bridge et les protections generate/regenerate/clear sont
  reutilisables.
- Le smoke P60 peut couvrir le parcours reel, pas une passerelle entre deux apps.

### Negatives

- Les composants d edition dynamique doivent etre reconstruits dans palette.html.
- Les tests hors Fusion couvrent le DOM, les messages et le bridge, mais la
  qualification finale exige une observation dans Fusion.
- Le prototype React/Vite reste temporairement dans le depot comme dette
  historique jusqu a une mission de retrait explicite.

### Risques et controles

- Risque de logique metier en JavaScript : interdit par contrat et tests de
  frontiere.
- Risque de palette bloquee sur Chargement : timeout, etat d erreur et retry
  obligatoires.
- Risque de perte de saisie : projet JSON versionne, sauvegarde locale atomique
  et import/export explicites.
- Risque de doublons CAD : registre BGIG et regeneration conservative existants.
- Risque de couplage adsk au coeur : recherche automatisee et tests de contrat.

## Alternatives refusees

- Revenir a une UI web externe : contraire a la decision Fusion uniquement.
- Tout mettre dans BoardGameInsertGenerator.py : melangerait UI, moteur et CAD.
- Utiliser uniquement CommandInputs : insuffisant pour l experience MVP complete.
- Faire de la scene Fusion la base projet : rendrait les calculs non
  deterministes et difficiles a tester.

## Suivi

- P54-R realigne tous les contrats et archive la trajectoire web.
- P56 construit l editeur complet dans la palette embarquee.
- P57 ajoute la partition pure et son bridge.
- P58 affiche le plan reel dans cette meme palette.
- P59 materialise et synchronise exactement ce plan.
- P60 execute les scenarios end-to-end et demande uniquement l observation
  humaine finale dans Fusion.
