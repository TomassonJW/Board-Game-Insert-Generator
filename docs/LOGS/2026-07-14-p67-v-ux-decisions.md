# 2026-07-14 - P67-V accepte la fondation UX V0.2

## Declencheur

Thomas valide la revue P67 et rend explicitement les decisions D67-01 a
D67-11. Il ajoute deux besoins : jeux X/Y/Z herites puis surchargeables par
plateau, livret, asset et conteneur ; simplification des modes et de la
hierarchie d information des cartes Conteneurs.

## Decisions humaines

- option C : fondation UX P44 avant geometries P45 ;
- quatre onglets et suppression de Precedent/Suivant ;
- Conteneur parent -> Elements enfants sans schema recursif ;
- toolbar de creation acceptee, complements exclus ;
- complements maintenus en quarantaine pour maintenant ;
- bouton X/Y, rotation historique conservee ;
- calcul hybride adaptatif a experimenter, jamais de scene automatique ;
- document nomme et recuperation autosauvee ;
- gabarit asset distinct du profil de cavite ;
- accents semantiques fixes, couleurs personnelles reportees ;
- P44-M001 limite a la stabilite de saisie.

ADR-0062 passe de `proposed` a `accepted`. P67 devient `done-human-gate` et
seule P44-M001 devient `ready`.

## Precision sur les jeux

L audit confirme trois contrats actuels distincts :

- l asset utilise un default de jeu de cavite puis un override scalaire ;
- le plateau/livret reutilise le jeu global X-Y pour son top inset et ne porte
  ni override par objet ni jeu Z explicite ;
- le conteneur utilise les jeux globaux P65 contre la boite, les voisins et les
  etages.

La cible partage un motif UX `Herite du projet` / `Personnalise X/Y/Z`, mais ne
fusionne pas les roles physiques. P67-V ne modifie aucune valeur et ne declare
pas 0,2 / 0,2 / 0 mm comme default universel. P44-M008 doit produire le contrat
de tolerance et la gate humaine avant toute implementation P44-M009.

## Precision sur les conteneurs

- un controle global discret applique un mode aux trois axes de tous les
  conteneurs seulement apres confirmation ;
- chaque conteneur montre un mode Auto/Cible/Fixe unique dans le parcours
  normal ;
- un contrat historique mixte reste `Personnalise` et conserve ses axes ;
- `Solidite` reste visible ;
- taille calculee, etage, appui, surplus et raisons rejoignent des details
  calcules replies par defaut.

## Frontieres

- aucune modification runtime, schema, loader, solveur, tolerance, geometrie,
  CAD IR ou scene Fusion ;
- coeur Python toujours sans `adsk` ;
- complements toujours compatibles historiquement et non creatables dans le
  parcours normal ;
- `print-validated: false`.

## Suite

La prochaine mission est P44-M001, package cible 0.1.21, selon
`docs/P44_M001_UI_STATE_STABILITY_CONTRACT.md`. P44-M002 et les missions
suivantes restent bloquees par leurs dependances.
