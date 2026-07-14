# P44-M002 - Densite compacte et hierarchie de carte

Date de cadrage : 2026-07-14
Statut : `implemented`, `automated-validated`, `fusion-retest-required`
Package cible : palette Fusion `0.1.22`
Capabilities : `C-FUSION-UI`, `C-QUALITY`
Dependance : P44-M001 integree dans `main`.

## 1. But du lot

P44-M002 rend les cartes de palette plus denses sans retirer les controles de
saisie du parcours normal. Les champs restent lisibles, les titres distinguent
clairement les cartes et leurs actions conservent une cible tactile ou pointeur
d au moins 40 px.

Le lot applique aussi la divulgation progressive aux informations calculees des
conteneurs. La solidite reste toujours editable ; taille calculee, etage, appui,
surplus et raisons par axe deviennent un detail secondaire replie par defaut.

## 2. Inclus

- grilles de champs adaptees a leur contenu dans les cartes de listes ;
- compacite des cartes, titres renforces et espacement regulier ;
- controles d action de cartes d au moins 40 px ;
- `Solidite`, paroi minimale et fond minimal toujours visibles ;
- l intitule UI `Details calcules` pour les calculs de conteneur, replie par defaut ;
- tests DOM couvrant ces invariants et version du package Fusion 0.1.22.

## 3. Explicitement exclu

- quatre onglets, suppression de Precedent/Suivant ou fusion Boite/plateaux ;
- composition Conteneur parent -> Elements enfants ou toolbar de creation ;
- schema, loader, serialisation, migration, coeur Python ou bridge metier ;
- solveur, score, jeu, tolerance, reservation, geometrie, CAD IR ou scene
  Fusion automatique ;
- reactivation, creation ou modification semantique des complements ;
- icones de commande, couleurs personnelles et toute qualification d impression.

## 4. Invariants d interaction

1. Le mode Compact ne masque aucun champ editable essentiel.
2. Les champs X/Y/Z et quantite restent accessibles sans ouvrir de detail.
3. Les champs de solidite restent visibles dans toute carte Conteneur.
4. Les details calcules ne changent aucun projet et ne declenchent aucune scene
   Fusion.
5. Les identifiants stables et la restauration de focus P44-M001 restent en
   vigueur apres chaque rendu de carte.
6. Aucun calcul metier n est ajoute au JavaScript de palette.

## 5. Cas d acceptation

- basculer Compact/Detaille sans masquer les reglages d asset ou de conteneur ;
- saisir dans une carte compacte avec les controles P44-M001 toujours stables ;
- verifier par DOM que les grilles de cartes s ajustent au contenu ;
- verifier que paroi et fond sont visibles avant toute ouverture de detail ;
- verifier que les informations calculees de conteneur sont dans `Details
  calcules`, fermees par defaut ;
- verifier que le package declare exactement 0.1.22.

## 6. Verification de mission

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m board_game_insert_generator examples/simple_box.json --format markdown
python -m compileall -q src tests scripts fusion_addin\BoardGameInsertGenerator
rg -n "(^|\s)(from|import)\s+adsk" src\board_game_insert_generator
git diff --check
```

## 7. Definition of Done

P44-M002 est termine lorsque les controles essentiels sont visibles en compact,
les details calcules sont replies, les tests automatises et controles de
frontiere passent, puis le commit est integre dans `main`. Une observation
Fusion reste obligatoire avant toute promotion au-dela de `implemented`.
`print-validated: false` reste obligatoire.