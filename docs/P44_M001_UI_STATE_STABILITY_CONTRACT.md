# P44-M001 - Stabilite de saisie et d etat de la palette

Date de cadrage : 2026-07-14
Statut : `ready`, `no-business-change`, `fusion-retest-required`
Package cible : palette Fusion `0.1.21`
Capabilities : `C-FUSION-UI`, `C-PROJECT`, `C-QUALITY`
Dependances : P66 acceptee, P67-V acceptee, ADR-0062 acceptee.

## 1. But du lot

P44-M001 rend la saisie stable avant toute densification ou reorganisation de
la palette. Modifier un champ ne doit plus fermer une section, deplacer le
focus, perdre la selection du texte, remonter la liste ou changer de carte.

Le lot traite une cause unique : les rendus de listes et les reponses derivees
asynchrones reconstruisent actuellement des portions de DOM sans preserver l
etat d interaction local.

## 2. Inclus

- conserver le focus, la selection et la position du curseur pendant une
  edition source valide ;
- conserver l etat ouvert/ferme des details par identifiant stable d objet ;
- conserver le scroll de la vue et le contexte de la carte active ;
- appliquer ces invariants aux boites, plateaux/livrets, assets et conteneurs ;
- preserver l etat lors d une reponse derivee asynchrone encore pertinente ;
- ignorer proprement une reponse obsolete selon les gardes P61 existantes ;
- definir les resets legitimes : changement de projet, import, suppression de l
  objet actif et navigation explicite vers une autre vue ;
- couvrir les listes jusqu a cinquante conteneurs sans identifiant DOM ambigu.

L implementation peut mettre a jour le DOM de facon ciblee ou capturer/restaurer
un etat local avant rendu. Le choix reste interne tant qu il respecte les tests,
les identifiants stables et la frontiere metier.

## 3. Explicitement exclu

- quatre onglets, suppression de Precedent/Suivant ou fusion des vues ;
- densification CSS, changement de couleurs, icones ou nouveaux labels ;
- composition visuelle Conteneur parent -> Elements enfants ;
- toolbar de creation, presets, cycle document ou calcul adaptatif ;
- nouveau champ de projet, migration de schema ou changement de serialisation ;
- changement de solveur, score, tolerance, jeu, reservation ou geometrie ;
- modification automatique de la scene Fusion ;
- reactivation des complements ;
- toute qualification d impression.

## 4. Invariants d interaction

1. Une saisie dans un champ texte ou numerique garde le meme champ actif.
2. Un select garde la carte et la section visibles apres application.
3. Une section ouverte ne se ferme pas a cause de `markDirty`, des derives ou
   d un solve termine.
4. Une section fermee ne s ouvre pas sans action utilisateur ou erreur locale
   qui exige explicitement son attention.
5. Le scroll ne saute pas en haut lors d un rendu pertinent.
6. L objet actif est retrouve par identifiant stable, jamais seulement par son
   index de liste.
7. Dupliquer ou supprimer recalcule le contexte sans rattacher le focus a un
   autre objet par accident.
8. Une reponse asynchrone obsolete ne restaure pas un ancien etat visuel.
9. Aucun calcul metier n est ajoute au JavaScript de palette.

## 5. Cas d acceptation

- modifier successivement nom, X, Y, Z et quantite d un plateau/livret sans
  fermeture de `Placement et ordre` ;
- modifier un asset, y compris un champ cartes, sans perte de carte active ;
- modifier Auto/Cible/Fixe et une valeur de conteneur sans saut de scroll ;
- recevoir des derives pendant la saisie sans perdre focus ni caret ;
- recevoir deux reponses dans le desordre et conserver uniquement l etat de la
  source courante ;
- dupliquer puis supprimer un objet autour de la carte active sans collision d
  identifiant ;
- parcourir et editer un projet de cinquante conteneurs ;
- changer volontairement d onglet, importer ou ouvrir un autre projet avec un
  reset d etat explicite et coherent ;
- conserver les actions de materialisation et leurs gardes P61/P66 inchangees.

## 6. Strategie de tests

### Tests DOM

- focus, caret, section ouverte et scroll apres `change` ;
- meme invariants apres reponse derivee asynchrone ;
- reponse obsolete ignoree ;
- duplication, suppression et cinquante cartes ;
- navigation clavier et identifiants uniques.

### Tests bridge et non-regression

- projet source identique hors champ explicitement edite ;
- aucun appel de scene Fusion provoque par le rendu ;
- roundtrip des anciens projets inchange ;
- syntaxe JavaScript et package Fusion verifies.

### Verification de mission

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m board_game_insert_generator examples/simple_box.json --format markdown
python -m compileall -q src tests scripts fusion_addin\BoardGameInsertGenerator
rg -n "(^|\s)(from|import)\s+adsk" src\board_game_insert_generator
git diff --check
```

## 7. Definition of Done

P44-M001 est termine seulement si les cas d acceptation passent, si le diff ne
contient aucun changement metier hors scope, si la suite complete est verte et
si le package installe est ensuite observe dans Fusion avant de promouvoir le
statut au-dela de `implemented`.

La mission suivante n est pas lancee dans le meme lot. `print-validated: false`
reste obligatoire.
