# P64-L09U-R3-V — recette Fusion 0.1.74

Statut historique : `done-human-KO`, `do-not-run`.

La recette courante est
`docs/P64_L09U_R4_V_0175_FUSION_GATE_RECIPE.md`.

Avant le verdict : `fusion-validated=false`, `print-validated=false`.

## Préparation déjà faite par Codex

- package 0.1.74 intégré dans `origin/main` ;
- add-in installé avec son marqueur de commit ;
- fixture et reçus R3 préparés ;
- trois projets personnels relus sans modification ;
- suite automatisée et preflight passés.

Ferme complètement Fusion avant de commencer afin de ne pas conserver l'ancien
code Python en mémoire.

## Étape 1 — démarrage

1. Rouvre Fusion et recharge BGIG.
2. Vérifie la version `0.1.74`.
3. Vérifie que BGIG démarre sur un projet vierge non enregistré.

KO immédiat si la version est différente ou si un ancien projet est rechargé.

## Étape 2 — CasLimite01+

1. Ouvre explicitement `CasLimite01+`.
2. Lance `Calculer` en mode Normal et note le temps affiché.
3. Lance `Finaliser` en mode Normal et note séparément :
   - recherche ;
   - plafond affiché ;
   - terminaison éventuelle ;
   - temps mural total.
4. Mesure une cavité issue d'un asset de `10 mm` avec jeu Z `0,6 mm`.
5. Vérifie une profondeur finale de `10,6 mm`, jamais `18,2 mm`.
6. Matérialise le plan final et note le temps.
7. Vérifie une scène progressive, réactive et fidèle à l'aperçu.

KO si la profondeur change, si le temps dépasse le plafond sous un libellé
« max » sans décomposition, si Fusion se fige, si un corps outil reste visible
ou si `ALL_TOOL_BODY_REFERENCE_LOST` apparaît.

## Étape 3 — CasLimite01+ sans plateau

1. Retire localement le plateau sans enregistrer le projet source.
2. Recalcule, finalise et matérialise.
3. Vérifie que les cavités restent à leur profondeur calibrée.
4. Vérifie qu'elles s'ouvrent sur la face fonctionnelle finale et que le surplus
   Z reste en matière sous leur fond.

Ne sauvegarde pas cette variante.

## Étape 4 — CasLimite02+

1. Ouvre explicitement `CasLimite02+`.
2. Calcule puis finalise en mode Normal.
3. Dans l'aperçu, repère les deux plateaux différents et leurs paliers.
4. Matérialise le plan final.
5. Vérifie dans Fusion :
   - une coupe par empreinte locale ;
   - aucune somme de hauteur dans les zones disjointes ;
   - un cumul uniquement dans l'intersection réelle ;
   - des paliers locaux lorsque les plateaux sont réellement empilés ;
   - les mêmes profondeurs et positions que dans l'aperçu.

KO si un rectangle englobant, une profondeur globale ou une somme totale
remplace les coupes locales.

## Étape 5 — CasLimite01++

1. Ouvre explicitement `CasLimite01++`.
2. Calcule, finalise et matérialise sans modifier ni enregistrer la source.
3. Vérifie la répartition, les profondeurs calibrées, la fidélité aperçu/Fusion
   et la progression par module.

## Étape 6 — rapport

Donne :

- `P64-L09U-R3-V Fusion OK 0.1.74` si tout passe ;
- sinon `P64-L09U-R3-V Fusion KO 0.1.74`, l'étape exacte, le message complet,
  les mesures observées et une capture utile.

Ajoute les temps de calcul, finalisation et matérialisation des trois projets,
les profondeurs mesurées avant/après finalisation et les observations sur les
deux plateaux.

Même en cas de succès Fusion, conserve `print-validated=false` tant qu'aucune
impression réelle n'est mesurée.
