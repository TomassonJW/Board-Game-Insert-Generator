# Contrat produit MVP Fusion-only

## Statut

Reference active depuis ADR-0055. Ce document remplace P54 comme contrat de
surface utilisateur pour P56-P60.

## Promesse

Une personne installe BGIG comme add-in Fusion 360, ouvre la palette Atelier de
rangement et realise tout le parcours sans navigateur externe, serveur local,
Vite, JSON manuel ni application separee.

Le moteur Python pur reste la source de verite. La palette edite un projet
versionne et demande des calculs au coeur. L adaptateur Fusion materialise le plan
accepte sans recalculer les decisions metier.

## Architecture d interaction

Flux obligatoire :

1. palette HTML embarquee dans l add-in ;
2. message JSON versionne vers le bridge Python Fusion ;
3. validation et calcul dans src/board_game_insert_generator ;
4. retour JSON de projet, erreurs ou plan resolu ;
5. rendu de l etat dans la palette ;
6. CAD IR produite par le coeur ;
7. materialisation par l adaptateur adsk ;
8. inspection, regeneration et export dans Fusion.

Interdictions :

- appel a localhost, serveur HTTP ou navigateur externe ;
- lancement de npm ou Vite dans le parcours utilisateur ;
- calcul de cavite, tolerance, partition ou CAD dans JavaScript ;
- lecture de la scene Fusion comme projet canonique ;
- creation silencieuse de corps automatiques.

## Surface principale

La palette Fusion est persistante, redimensionnable et relancable depuis le
bouton BGIG de la toolbar. Elle contient six vues dans une seule surface :

1. Boite ;
2. Pieces ;
3. Plateaux et livrets ;
4. Bacs ;
5. Fabrication ;
6. Resultat.

La navigation reste accessible a tout moment. Le mode simple montre les champs
essentiels ; le mode avance ouvre les jeux, minima, axes extensibles, dimensions
verrouillees et diagnostics sans changer d outil.

## Vue Boite

Champs obligatoires :

- nom du projet ;
- largeur, profondeur et hauteur interieures ;
- hauteur utilisable ;
- marge sous couvercle ;
- jeu contre la boite ;
- jeu entre les bacs.

Les erreurs sont locales, en francais et actionnables.

## Vue Pieces

Table dynamique sans limite metier arbitraire :

- nom ;
- forme rond, carre, rectangle, cartes, cube/de, pion ou sur mesure ;
- dimensions en millimetres ;
- quantite ;
- bac cible ;
- jeu propre optionnel ;
- confiance de mesure ;
- ajouter, dupliquer et supprimer.

Nouveau bac cree un groupe stable. Plusieurs lignes avec le meme bac cible
produisent plusieurs cavites dans un seul corps.

## Vue Plateaux et livrets

Table dynamique :

- nom ;
- type ;
- dimensions ;
- quantite ;
- ordre automatique ou explicite.

La palette montre la hauteur reservee et la hauteur restante. Une reservation
reste non imprimable.

## Vue Bacs

Une carte par groupe demande affiche :

- nom et contenus ;
- cavites calibrees ;
- enveloppe minimale ;
- paroi et fond minimaux ;
- axes extensibles X/Y/Z ;
- dimensions finales verrouillees ;
- preference de surplus.

Copie obligatoire : les cavites gardent leurs mesures ; le surplus epaissit le
bac autour et sous son contenu.

## Vue Fabrication

Reglages essentiels et avances, complements explicitement ajoutes et actions :

- verifier le projet ;
- construire ou recalculer ;
- sauvegarder et importer un projet ;
- ouvrir les reglages experts ;
- inspecter ou nettoyer la scene BGIG.

BGIG ne propose ni ne cree de complement automatique.

## Vue Resultat

Avant materialisation, la palette affiche exclusivement le plan moteur resolu :

- statut construit, partiel ou impossible ;
- liste des bacs et contenus ;
- cavites, enveloppes minimale/finale et surplus ;
- positions X/Y/Z ;
- pile superieure et supports ;
- complements explicites ;
- nombre de corps final ;
- confirmation zero corps automatique ;
- vue dessus et coupe derivees des placements reels ;
- erreurs et corrections.

Actions :

- Modifier ;
- Recalculer ;
- Materialiser dans Fusion ;
- Regenerer ;
- Exporter les corps imprimables.

## Etats obligatoires

- chargement borne avec timeout ;
- projet vide ;
- saisie invalide ;
- pret a construire ;
- calcul en cours ;
- impossible ;
- resultat obsolete apres modification ;
- resultat pret ;
- scene Fusion synchronisee ;
- erreur de bridge avec retry.

Aucun etat ne reste sur Chargement sans timeout, cause et action.

## Persistance

Le projet utilise bgig.project.v1 ou une migration additive suivante. La
persistance est locale a l add-in :

- sauvegarde atomique du projet courant ;
- export JSON explicite ;
- import et normalisation ;
- reprise apres fermeture/reouverture ;
- aucune donnee distante.

Les settings techniques et le projet utilisateur restent distincts.

## Accessibilite et ergonomie

- labels explicites ;
- navigation clavier dans la palette ;
- focus visible ;
- controles tactiles ou souris d au moins 40 px ;
- contrastes lisibles ;
- aucune action disponible uniquement au survol ;
- tables adaptables a une palette etroite ;
- debutant guide, expert non bride.

## Preuves P56

- tests DOM et bridge hors Fusion ;
- build/validation des ressources embarquees ;
- ajout, modification, duplication, suppression et grande cardinalite ;
- sauvegarde/import/migration ;
- timeout, erreur et retry ;
- aucune URL localhost ni dependance runtime frontend ;
- smoke humain de la palette dans Fusion avant statut fusion-validated.

## Frontieres P57-P60

P56 edite et valide le projet. P57 resout la partition. P58 affiche le vrai plan.
P59 materialise et synchronise. P60 prouve le parcours complet dans Fusion.

Aucune validation d impression n est deduite de P60. Le statut
print-validated reste faux tant qu une impression reelle n est pas mesuree.
