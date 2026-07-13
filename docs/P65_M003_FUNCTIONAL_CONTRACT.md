# P65-M003 - Contrat fonctionnel des tailles de conteneurs

Date de cadrage : 2026-07-13
Statut : `implemented`, `automated-validated`, `fusion-retest-required`
Release cible : palette Fusion `0.1.18`
Capabilities : `C-FUSION-UI`, `C-MODULE`, `C-SOLVER`, `C-QUALITY`
Dependances : P64, P65-M001 et P65-M002 integres ; ADR-0055, ADR-0059 et ADR-0060 acceptees.

## 1. But du lot

P65-M003 rend la taille de chaque conteneur compréhensible et pilotable depuis
l onglet `Conteneurs` de la palette Fusion. L utilisateur doit pouvoir repondre,
sans ouvrir un rapport technique, aux questions suivantes :

1. Quelle est la plus petite taille physiquement possible pour ce conteneur ?
2. Quelle taille ai-je demandee, et avec quel niveau de contrainte ?
3. Quelle taille le solveur propose-t-il dans le plan courant ?
4. Pourquoi la proposition differe-t-elle eventuellement de la cible ?
5. Cette proposition est-elle actuelle, perimee, partielle ou impossible ?

Le lot ajoute aussi une action locale `Estimer les tailles`. Cette action lance
le solveur borne existant afin d afficher une proposition, sans materialiser
dans Fusion et sans modifier silencieusement le projet.

P65-M003 ne cree pas un second solveur, une approximation locale ou une
heuristique concurrente. Une taille dite « calculee » provient toujours du vrai
plan produit par le coeur Python.

## 2. Frontieres strictes

### Inclus

- rapprocher minimum, demande et resultat dans chaque carte de conteneur ;
- exposer les modes par axe `Auto`, `Cible` et `Fixe` avec leur semantique ;
- afficher la derniere taille calculee uniquement avec un statut explicite ;
- expliquer les ecarts par axe avec un vocabulaire utilisateur ;
- afficher le surplus par face en vue detaillee ;
- afficher une information compacte sur l etage Z et l appui quand elle existe ;
- ajouter l action contextuelle `Estimer les tailles` dans `Conteneurs` ;
- projeter les donnees metier necessaires depuis Python vers la palette ;
- couvrir les etats courant, perime, partiel et impossible ;
- conserver `Recalculer` comme action globale persistante de reference.

### Explicitement exclu

- nouvelle strategie de placement, backtracking ou optimiseur ;
- changement de score, de budget de recherche ou de priorite du solveur ;
- recalibrage des tolerances ou de leurs valeurs par defaut ;
- changement des formules de minimum, cavite, paroi ou fond ;
- creation automatique de cale, separateur, support ou corps imprimable ;
- mutation automatique d une cible ou d une dimension fixe ;
- nouvelle forme de cavite ou nouvelle geometrie Fusion ;
- changement des reservations de plateaux/livrets ou de la logique multi-etages ;
- mode avance global, fenetre web, Vite, serveur local ou calcul metier JavaScript ;
- refonte generale du style de la palette ;
- validation ergonomique physique ou impression reelle.

Si l implementation revele qu une formule moteur ou une heuristique doit
changer, P65-M003 s arrete : la correction doit etre recadree dans une mission
separee. Le lot ne doit pas masquer une faiblesse du solveur avec un calcul UI.

## 3. Vocabulaire canonique

### 3.1 Taille minimale

La `Taille minimale` est l enveloppe exterieure minimale derivee des contenus,
des cavites, de la paroi et du fond courants. Elle constitue un plancher dur.
Elle est recalcuree avec les derives du projet et peut donc changer apres une
modification d asset, d orientation, de jeu de cavite, de paroi ou de fond.

Elle n est ni une proposition de rangement, ni une valeur utilisateur, ni une
ancienne valeur memorisee.

### 3.2 Reglage par axe

Chaque axe X, Y et Z porte exactement un des trois contrats suivants :

| Mode | Sens utilisateur | Contrat solveur | Echec attendu |
| --- | --- | --- | --- |
| `Auto` | « Adapte cet axe a l ensemble du rangement. » | aucune taille demandee ; le solveur peut distribuer le surplus | seulement si aucun arrangement global n est possible |
| `Cible` | « Essaie d approcher cette taille. » | preference souple ; la valeur peut etre depassee ou reduite si necessaire | pas d echec du seul fait d un ecart a la cible |
| `Fixe` | « Cette taille doit etre respectee. » | contrainte dure | erreur si la valeur est sous le minimum ou incompatible avec le plan global |

Le mot `Cible` ne doit jamais etre presente comme une garantie. Le mot `Fixe`
ne doit jamais etre corrige silencieusement.

### 3.3 Taille calculee

La `Taille calculee` est `final_outer_dimensions_mm` pour le conteneur dans le
dernier plan solve. Elle inclut la distribution de surplus et les contraintes
globales du rangement. Elle n existe pas avant un calcul et ne peut pas etre
reconstruite localement dans la palette.

### 3.4 Estimation

`Estimer les tailles` est le nom UX d une operation, pas un quatrieme type de
dimension. Elle appelle le meme chemin `solve_project` que `Recalculer`, puis
reste sur l onglet `Conteneurs` pour rendre les tailles calculees visibles.

L estimation :

- ne sauvegarde pas implicitement ;
- ne modifie aucun champ source ;
- ne cree, ne regenere et ne supprime aucune entite Fusion ;
- ne produit pas de CAD IR materialisee ;
- ne transforme pas une proposition partielle en solution complete ;
- ne contourne pas les gardes de materialisation.

## 4. Modele d affichage d une carte

### 4.1 Vue compacte par defaut

Une carte doit permettre de parcourir plusieurs dizaines de conteneurs. Elle
affiche au maximum deux lignes de synthese metier :

```text
Bac cartes · 1 contenu · 1 cavite
Min. 71,6 x 97,6 x 29,8 · Reglage Auto / Cible 140 / Auto
Calculee 140,8 x 178,8 x 63,4 · A jour
```

Regles :

- les unites sont visibles une fois par groupe coherent ;
- l ordre des axes reste toujours X x Y x Z ;
- `Non calculee` remplace une absence de plan ;
- `A reestimer` est visuellement distinct de `A jour` ;
- une proposition partielle porte le mot `Partielle` au premier niveau ;
- aucun digest, identifiant de plan, code Python ou nom de champ brut n apparait ;
- deux conteneurs ayant le meme nom restent relies par leur identifiant stable,
  jamais par leur libelle humain.

La densite `Detaille` reste un choix global de presentation conforme a
ADR-0060 ; P65-M003 ne recree pas un mode avance.

### 4.2 Vue detaillee

La vue detaillee ajoute, pour chaque axe :

- le mode courant ;
- la valeur cible ou fixe editable quand elle existe ;
- le minimum derive ;
- la valeur calculee si elle est valide ;
- un court motif utilisateur si minimum, demande et resultat different.

Elle ajoute egalement :

- surplus gauche, droite, avant, arriere, dessous et dessus ;
- paroi minimale et fond minimal appliques au conteneur ;
- contenus lies et nombre de cavites ;
- etage Z ou plage Z calculee ;
- contribution d appui avec une phrase utilisateur, uniquement si pertinente.

Exemples de motifs autorises :

- `Axe adapte automatiquement au volume disponible.`
- `Cible depassee pour loger tous les conteneurs.`
- `Cible reduite pour conserver un arrangement complet.`
- `Dimension fixe respectee.`
- `Dimension fixe inferieure au minimum de 4,2 mm.`
- `Taille issue d une proposition partielle non materialisable.`

Les motifs ne doivent pas promettre la cause exacte si le moteur ne l expose
pas. Dans ce cas, employer une explication factuelle plus generale.

## 5. Etats et invalidation

La taille minimale et la taille calculee n ont pas le meme cycle de vie.

| Etat | Minimum affiche | Taille calculee | Libelle | Materialisation |
| --- | --- | --- | --- | --- |
| Projet valide, jamais solve | courant | aucune | `Non calculee` | interdite |
| Plan complet correspondant au projet | courant | courante | `A jour` | autorisee selon les gardes existantes |
| Projet modifie apres calcul | nouveau minimum courant | ancienne valeur attenuee, explicitement historique | `Avant modification - A reestimer` | interdite |
| Proposition partielle | courant | valeur partielle si fournie par le plan | `Partielle` | interdite |
| Calcul impossible | courant si les derives sont valides | aucune fausse valeur | `Calcul impossible` | interdite |
| Derives invalides | aucune valeur inventee | aucune | diagnostic local actionnable | interdite |

Une ancienne taille peut rester visible pour aider a comprendre le changement,
mais elle doit etre attenuee, datee semantiquement `Avant modification` et ne
doit jamais porter `Calculee` sans qualificatif historique.

Le minimum courant doit se mettre a jour apres les modifications source selon
le mecanisme reactif P61. L ancien plan reste perime tant qu un nouveau solve
n a pas reussi.

## 6. Action `Estimer les tailles`

### Placement et libelle

- bouton local dans l entete ou le pied de la section `Conteneurs` ;
- libelle initial : `Estimer les tailles` ;
- apres un calcul courant : `Reestimer les tailles` est accepte ;
- aide courte : `Calcule une proposition sans modifier le projet ni Fusion.` ;
- ne pas dupliquer cette action dans chaque carte ;
- ne pas ajouter cette action a la barre persistante.

### Comportement

1. synchroniser les champs source en cours d edition ;
2. demander les derives courants au coeur Python si necessaire ;
3. appeler l action bridge existante `solve_project` ;
4. conserver l onglet `Conteneurs` et la position de defilement autant que
   possible ;
5. projeter les resultats dans toutes les cartes ;
6. afficher un resume discret si la proposition est partielle ou impossible ;
7. laisser `Materialiser dans Fusion` desactive sauf solution complete et a jour.

Le bouton est desactive avec une explication si aucun conteneur explicite n est
present ou si les sources sont invalides. Un double clic ou un calcul deja en
cours ne doit pas lancer deux solves concurrents.

## 7. Contrat de presentation Python -> palette

Le JavaScript assemble l interface mais ne deduit pas la semantique metier. La
projection de resultat Python doit fournir une collection additive, par exemple
`container_sizing`, indexee par l identifiant stable du groupe :

```json
{
  "container_group_id": "cards-tray",
  "label": "Bac cartes",
  "minimum_outer_dimensions_mm": {"x": 71.6, "y": 97.6, "z": 29.8},
  "axis_contracts": {
    "x": {"mode": "auto", "requested_mm": null},
    "y": {"mode": "target", "requested_mm": 140.0},
    "z": {"mode": "auto", "requested_mm": null}
  },
  "calculated_outer_dimensions_mm": {"x": 140.8, "y": 178.8, "z": 63.4},
  "axis_explanations": {
    "x": "auto_distributed",
    "y": "target_adjusted_for_complete_arrangement",
    "z": "auto_distributed"
  },
  "surplus_distribution_mm": {
    "left": 34.6,
    "right": 34.6,
    "front": 40.6,
    "back": 40.6,
    "below": 33.6,
    "above": 0.0
  },
  "proposal_status": "complete",
  "stage_index": 1,
  "support_summary": "supported_by_requested_bodies"
}
```

Les noms exacts peuvent suivre les conventions existantes, mais les invariants
suivants sont obligatoires :

- projection additive et versionnee, sans migration destructive du projet ;
- aucune dependance `adsk` dans le coeur ;
- aucune formule de minimum ou de taille finale en JavaScript ;
- mapping par identifiant de groupe stable ;
- absence explicite de valeur plutot qu un zero ambigu ;
- statut complet/partiel/impossible structure ;
- raisons machine traduites par une table de presentation, sans exposer le code
  brut au premier niveau ;
- l etat `perime` reste pilote par le digest source/plan P61 et ne modifie pas
  artificiellement le resultat moteur.

Cette projection est une extension de presentation dans l architecture acceptee.
Elle ne requiert pas une nouvelle ADR tant qu elle ne modifie ni schema public
source, ni solveur, ni separation coeur/Fusion.

## 8. Cas d acceptation obligatoires

### Donnees et calcul

1. aucun conteneur : estimation desactivee et cause visible ;
2. projet non solve : minimum visible, calculee `Non calculee` ;
3. axes Auto/Auto/Auto : proposition complete et explication de distribution ;
4. combinaison Auto/Cible/Fixe : chaque axe garde sa semantique ;
5. cible inferieure ou superieure a la proposition : pas d echec artificiel,
   ecart visible et explique ;
6. fixe inferieure au minimum : blocage local, aucune fausse proposition ;
7. fixe globalement incompatible : calcul impossible explicite ;
8. plan complet : valeur a jour et materialisation gardee normalement ;
9. plan partiel : tailles partielles identifiees, residuel visible,
   materialisation interdite ;
10. plan impossible : aucune ancienne valeur presentee comme courante ;
11. edition apres solve : minimum recalcule, ancien plan marque perime ;
12. deux libelles identiques : aucune collision de resultat ;
13. cinquante conteneurs : cartes compactes parcourables et un seul CTA local ;
14. plusieurs etages : taille et information Z conformes au plan P64 ;
15. reservation superieure : taille calculee et profondeur utile restent celles
    du plan P63/P64, sans recalcul UI ;
16. estimation repetee sans changement : resultat deterministe et sans mutation.

### Non-regression et securite produit

- le projet serialise est identique avant et apres une estimation seule ;
- aucune commande de scene Fusion n est envoyee par l estimation ;
- aucune cale, aucun support et aucun corps automatique n apparait ;
- `Materialiser dans Fusion` reste unique, persistante et adjacente a
  `Recalculer` ;
- une proposition partielle ou perimee ne peut pas etre materialisee ;
- Compact/Detaille fonctionne sans case `Mode avance` ;
- aucun texte brut comme `supported_by_requested_bodies`, digest ou identifiant
  de plan n est visible au premier niveau ;
- le package Fusion contient la bonne palette et aucun runtime localhost.

## 9. Strategie de tests

### Tests Python

- projection pure minimum/demande/calculee par identifiant stable ;
- modes Auto/Cible/Fixe et valeurs absentes ;
- complet, partiel et impossible ;
- raisons par axe et surplus par face ;
- multi-etages et reservations superieures sans changement de solveur ;
- serialisation source inchangee apres solve.

### Tests palette et bridge

- marqueurs DOM des trois dimensions et des quatre etats ;
- un seul bouton `Estimer les tailles` ;
- ce bouton utilise `solve_project`, pas une nouvelle action metier ;
- conservation de l onglet Conteneurs ;
- invalidation apres edition et garde de materialisation ;
- absence des codes techniques au premier niveau ;
- rendu Compact et Detaille ;
- syntaxe JavaScript valide.

### Verification de mission

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m board_game_insert_generator examples/simple_box.json --format markdown
python -m compileall src tests scripts
git diff --check
```

L installation du package `0.1.18` et ses marqueurs sont verifies localement.
L observation manuelle dans Fusion reste groupee dans P66, sauf echec runtime
qui rendrait impossible la poursuite automatisee.

## 10. Definition of Done

P65-M003 est termine seulement si :

- les cinq questions du but sont repondables dans chaque carte ;
- taille minimale, demande et taille calculee ne sont jamais confondues ;
- `Estimer les tailles` reutilise le solveur et ne mute rien ;
- les etats non calcule, a jour, perime, partiel et impossible sont couverts ;
- les ecarts de cible et blocages fixes sont explicables ;
- aucun changement de solveur, tolerance, corps ou geometrie n a glisse dans le lot ;
- les tests complets et controles de package passent ;
- les documents de pilotage et la version du package sont a jour ;
- le commit est integre a `main` selon la politique du depot ;
- `fusion-retest-required` et `print-validated: false` restent explicites.

## 11. Instruction d execution autonome

Un agent autonome peut realiser P65-M003 sans nouvelle decision humaine s il
respecte ce contrat. Il doit travailler par boucles courtes :

1. projection Python pure et tests ;
2. rendu compact/detaille et tests DOM ;
3. action d estimation, invalidation et tests bridge ;
4. review de frontiere : zero solveur/tolerance/geometrie ;
5. suite complete, package, diff et pilotage.

Deux revues explicites sont obligatoires avant commit :

- revue fonctionnelle contre les sections 3 a 8 ;
- revue architecture/scope contre la section 2 et ADR-0055.

Tout changement d heuristique, de formule de taille ou de contrat public source
sort de P65-M003 et impose un nouveau cadrage.
