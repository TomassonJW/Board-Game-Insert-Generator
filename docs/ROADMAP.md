# Roadmap

Cette roadmap decrit les phases macro jusqu'au produit fini. Le detail
operationnel vit dans `docs/BACKLOG.md`; l'etat courant vit dans
`docs/STATUS.md`.

## Phase 0 - Fondation projet

Objectif : rendre le depot autopilotable.

Contenu :

- documentation de vision et produit ;
- protocole Codex ;
- roadmap macro ;
- backlog actionnable ;
- statut projet ;
- prochaines actions ;
- ADR et logs ;
- regles qualite ;
- templates GitHub.

Criteres de reussite :

- un futur agent peut reprendre sans contexte oral ;
- les missions sont petites, testables et documentees ;
- les decisions structurantes ont un emplacement clair ;
- le depot indique ce qui est implemente, experimental, prevu et a valider par
  impression reelle.

## Phase 1 - Moteur Python pur

Objectif : stabiliser le coeur metier local, sans dependance Fusion 360.

Contenu :

- modeles de donnees ;
- chargement JSON ;
- validation ;
- dimensions en millimetres ;
- rapports Markdown/JSON ;
- CLI de diagnostic ;
- tests unitaires.

Criteres de reussite :

- une configuration locale valide produit un resultat reproductible ;
- les erreurs sont actionnables ;
- le moteur est importable et testable hors Fusion 360 ;
- le contrat interne est documente.

## Phase 2 - Layout rectangulaire simple

Objectif : produire des organisations rectangulaires comprehensibles pour jeux
simples.

Contenu :

- decoupage en grille ;
- strategies lignes et colonnes ;
- cellules theoriques ;
- modules imprimables rectangulaires ;
- rotation controlee ;
- comparaison simple de layouts.

Criteres de reussite :

- le moteur peut proposer des layouts simples et deterministes ;
- les cas impossibles sont detectes proprement ;
- les cellules theoriques ne sont pas confondues avec les corps imprimables.

## Phase 3 - Tolerances intelligentes

Objectif : appliquer les jeux selon le role de chaque face et le profil
d'impression.

Contenu :

- jeu peripherique ;
- jeu inter-modules ;
- faces exposees ;
- faces internes ;
- profils d'impression ;
- marges fonctionnelles ;
- protocole de calibration physique.

Criteres de reussite :

- chaque offset a une raison explicable ;
- les rapports affichent les valeurs appliquees ;
- les tolerances restent ajustables ;
- les valeurs critiques sont marquees comme a valider par impression reelle.

## Phase 4 - Generation Fusion 360 de blanks

Objectif : generer des composants Fusion 360 rectangulaires a partir du moteur.

Contenu :

- contrat de representation intermediaire CAD-agnostic ;
- add-in ou script Fusion 360 ;
- creation de composants ;
- corps rectangulaires ;
- parametres ;
- rayons simples ;
- export eventuel.

Criteres de reussite :

- une configuration valide produit des composants inspectables ;
- Fusion ne recalcule ni layout ni tolerances ;
- le coeur Python reste testable hors Fusion.

## Phase 5 - Cavites et receptacles

Objectif : transformer les blanks en modules fonctionnels.

Contenu :

- bacs a tokens ;
- logements cartes ;
- cartes sleevees ;
- des ;
- meeples ;
- encoches de doigts ;
- separateurs ;
- fonds arrondis.

Criteres de reussite :

- les cavites respectent les parois minimales ;
- chaque type fonctionnel a des clearances explicites ;
- les premiers modules sont imprimables et documentes.

## Phase 6 - Modules composites

Objectif : gerer les modules formes de plusieurs volumes soudes.

Contenu :

- modules en L ;
- modules en T ;
- volumes soudes ;
- gestion des faces internes ;
- fusion geometrique ;
- tolerances uniquement sur faces exposees.

Criteres de reussite :

- un module composite ne recoit aucun jeu sur ses jonctions internes ;
- les faces exposees restent tolerancees ;
- les unions CAD sont inspectables.

## Phase 7 - Couvercles et mecanismes

Objectif : ajouter des fermetures et interfaces fonctionnelles.

Contenu :

- couvercles poses ;
- couvercles coulissants ;
- rainures ;
- charnieres simples ;
- clips eventuels ;
- jeux fonctionnels.

Criteres de reussite :

- les mecanismes ont des tolerances dediees ;
- les risques d'impression sont documentes ;
- les pieces doivent etre validees physiquement avant statut stable.

## Phase 8 - Surcouche esthetique

Objectif : ajouter un langage visuel parametrique sans casser la fonction.

Contenu :

- embossage ;
- gravure ;
- labels ;
- textures ;
- ajourages ;
- motifs ;
- coins stylises.

Criteres de reussite :

- les options esthetiques sont des features parametriques ;
- elles peuvent etre activees/desactivees ;
- elles respectent les contraintes d'epaisseur et d'impression.

## Phase 9 - Assistant de conception

Objectif : aider l'utilisateur a passer des assets aux propositions de layout.

Contenu :

- description des assets ;
- generation de propositions ;
- scoring compacite ;
- scoring ergonomie ;
- scoring impression ;
- scoring setup ;
- variantes de layout.

Criteres de reussite :

- les recommandations sont explicables ;
- plusieurs variantes peuvent etre comparees ;
- les hypotheses restent visibles.

## Phase 10 - Packaging produit

Objectif : rendre l'outil utilisable, documente et distribuable.

Contenu :

- documentation utilisateur ;
- exemples reels ;
- presets ;
- export ;
- distribution ;
- versioning ;
- release stable.

Criteres de reussite :

- un utilisateur peut installer, lancer un exemple et comprendre les limites ;
- les releases indiquent clairement ce qui est stable ou experimental ;
- les exemples reels sont reproductibles.

## Regle de progression

Une phase peut etre partiellement exploree avant la phase precedente si cela
reduit un risque majeur, mais elle ne doit pas etre declaree terminee sans :

- tests pertinents ;
- documentation a jour ;
- statut clair dans `docs/STATUS.md` ;
- backlog mis a jour ;
- limites explicites.
