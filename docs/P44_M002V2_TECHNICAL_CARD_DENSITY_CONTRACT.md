# P44-M002V2 - Cartes techniques compactes hybride A+B

Date : 2026-07-14
Statut : `implemented`, `automated-validated`, `fusion-validation-required`
Package cible : palette Fusion `0.1.23`
Capabilities : `C-FUSION-UI`, `C-QUALITY`
Dependances : P44-M001 et P44-M002 integrees ; KO UX humain sur 0.1.22.

## 1. Decision

Le package 0.1.22 a passe les preuves automatisees mais a recu un KO humain sur
la compacite reelle. La correction adopte l hybride A+B valide par Thomas :

- A : une grille technique dense, adaptee aux valeurs courtes ;
- B : des bandes semantiques distinctes pour garder une lecture immediate.

La densite vient de l agencement et des largeurs bornees, pas de cibles trop
petites. Les controles interactifs conservent une hauteur minimale de 40 px.

## 2. Contrat visuel

- largeur >= 760 px : identite sur une bande, X/Y/Z/quantite sur une bande ;
- largeur 560 a 759 px : regroupements conserves avec repli sur deux bandes ;
- largeur < 560 px : champs numeriques en grille 2 x 2, jamais etires seuls ;
- nom flexible ; types et destinations bornes ; nombres entre 72 et 112 px ;
- titres de carte renforces et actions groupees dans l en-tete ;
- `Prise et tolerances`, `Placement et ordre` et `Solidite` visibles ;
- explications et calculs secondaires replies : taille, appui, etage et surplus ;
- mode Compact sans resume duplique ni disparition de controle essentiel.

## 3. Frontieres

Aucune logique metier, schema, loader, serialisation, bridge, tolerance,
geometrie, CAD IR ou scene Fusion n est modifie. Les quatre onglets, la
composition parent/enfants, le bouton X/Y et la toolbar restent hors scope.

## 4. Preuves automatisees

- tests DOM sur les classes de bandes, les largeurs bornees et les seuils ;
- tests DOM sur la visibilite des sections essentielles et le repli des calculs ;
- roundtrip, bridge, transport Qt et materialisation historique inchanges ;
- syntaxe JavaScript, suite complete, exemple CLI, compileall, frontiere `adsk`
  et `git diff --check`.

Un preflight Chrome a ete lance aux largeurs 920, 700 et 540 px, mais le
rendu headless Windows a produit un artefact gris apres les premiers controles.
Il ne constitue donc aucune preuve visuelle. L observation humaine dans Fusion
reste obligatoire.

## 5. Gate

P44-M003 reste bloque jusqu au retour humain
`P44-M002V Fusion OK 0.1.23 - commit <sha>`.

Un KO ouvre uniquement une nouvelle correction bornee de cette mission.
`print-validated: false` reste obligatoire.
