# Gate report - P22 premiere surface UX persistante

## Declencheur

P19, P20 et P21 rendent le plan de boite, le placement borne, le portefeuille de variantes et la selection exportable disponibles dans le moteur Python pur. Le prochain gain produit est l edition humaine persistante de la boite complete : inventaire, intentions, reservations, locks, comparaison et choix.

ADR-0036 interdit explicitement de demarrer une palette Fusion ou une app locale/web sans choix humain de surface. Cette gate est atteinte : les deux options engagent l architecture, les dependances, la distribution, les tests et la maintenance.

## Etat actuel

- Le moteur est la source de verite : `BoxFillPlan`, P20 greedy et P21 portfolio sont testables hors Fusion.
- La commande Fusion classique est validee pour smoke, inspection, generation, clear et export STL V0 ; elle reste une surface technique.
- P21 fournit deja une comparaison HTML statique et une selection CAD IR portable, mais ne permet ni edition persistante ni sauvegarde d intentions utilisateur.
- Aucune impression physique, ergonomie reelle ou materialisation Fusion d une variante choisie n est validee.

## Contrat non negociable

1. Le moteur Python reste CAD-agnostic et sans `adsk`.
2. L UI edite un contrat projet/versionne, jamais une scene Fusion comme source de verite.
3. Fusion ne fait que materialiser ou exporter une selection explicite, lors d une mission et d une gate distinctes.
4. Les modes novice et expert progressent : boite, assets, intentions et propositions avant tolerances, grille et diagnostics bruts.
5. Le fonctionnement local/offline et les fichiers JSON reproductibles restent le defaut.

## Options

### A - Conserver la commande Fusion classique

- Cout : faible a court terme.
- Avantage : aucun nouveau runtime ni distribution.
- Limite : ne couvre pas inventaire visuel, variantes comparables, edition de locks ni parcours novice.
- Verdict : refuse comme UX produit ; conserve comme outil de smoke et export.

### B - Palette Fusion HTML/JS persistante

- Cout : moyen ; bridge Fusion, lifecycle de palette, tests difficiles hors Fusion.
- Avantage : contexte CAD visible et actions Fusion proches.
- Risque : l UX de conception devient dependante de Fusion et la scene peut etre prise a tort pour la source de verite.
- Cas d usage : bon si le produit cible exclusivement des utilisateurs deja dans Fusion.

### C - App locale autonome minimaliste

- Cout : moyen ; serveur local, persistence et packaging a definir.
- Avantage : independance CAD, parcours novice clair, tests UI automatisables, partage de projet JSON.
- Risque : une implementation sans design system ni contrat API propre creerait une seconde dette UX.
- Cas d usage : bon socle si l objectif est un outil local simple avant une integration CAD plus riche.

### D - Hybride : app locale de conception + Fusion adaptateur CAD/export

- Cout : le plus eleve initialement, mais decouple nettement conception et CAD.
- Avantage : correspond a la North Star et a l UX cible : app pour boite/assets/intentions/variantes/edition, Fusion pour materialisation/export d une selection explicite.
- Risque : exige une frontiere de contrat, une strategie de distribution et un premier choix de stack UI.
- Cas d usage : meilleure trajectoire vers une beta utilisable par novice et expert sans enfermer le produit dans Fusion.

## Comparaison de decision

| Critere | A Commande Fusion | B Palette Fusion | C App locale | D Hybride |
| --- | ---: | ---: | ---: | ---: |
| Parcours novice | faible | moyen | fort | fort |
| Controle expert CAD | fort | fort | moyen | fort |
| Independance moteur/CAD | moyen | faible | fort | fort |
| Testabilite hors Fusion | moyenne | faible | forte | forte |
| Cout initial | faible | moyen | moyen | eleve |
| Trajectoire UX cible | faible | moyenne | forte | tres forte |

## Recommandation

Choisir **D - hybride**, avec une premiere tranche volontairement petite : une app locale de composition devient la surface utilisateur principale ; Fusion conserve son role d adaptateur de materialisation/export.

Le premier spike apres autorisation ne doit pas encore generer dans Fusion. Il doit prouver le parcours `ouvrir projet -> saisir/editer boite, assets et reservations -> generer P21 -> comparer -> verrouiller/selectionner -> exporter selection JSON/CAD IR`, sur des fichiers locaux versionnes. Cette tranche rend visible la valeur utilisateur sans imposer de nouvelle geometrie ou de boucle Fusion.

La stack exacte ne doit pas etre choisie implicitement. La recommandation de mise en oeuvre est une UI locale TypeScript/React avec build Vite et un adaptateur Python local fin ; elle apporte un socle ergonomique et testable mais introduit des dependances majeures, donc elle reste incluse dans la validation demandee. Une variante standard-library/HTML est possible, mais moins adaptee a l objectif UX premium.

## Perimetre P23 propose si la gate est acceptee

- Projet local chargeable et sauvegardable sans cloud ni compte.
- Etapes simples : boite, assets, intentions/reservations, propositions, edition de locks/selection, export.
- Vue 2D/SVG de la boite et des layers, warnings et raisons visibles.
- Mode expert progressif pour JSON, dimensions, tolerances et diagnostics.
- Reutilisation du moteur P19/P20/P21 ; aucun calcul de layout dans l UI.
- Export d une selection explicite ; aucune generation Fusion automatique ni promesse d impression.
- Tests moteur existants plus tests UI de parcours et de non-regression de contrat.

## Hors scope P23

- Materialisation Fusion du plan selectionne.
- Solveur global, backtracking, IA, cloud, authentification, collaboration, catalogue SaaS.
- Geometries de mecanismes, modification de tolerances par defaut et validation d impression.

## Risques

- Une app locale sans contrat projet unique dupliquerait `BoxFillPlan` : interdit.
- Une palette Fusion prematuree rendrait les tests et la distribution dependants du CAD.
- Une stack UI choisie sans gate ajouterait des dependances et de la maintenance non consenties.
- L UI ne doit jamais presenter un score P21, un export STL ou une scene Fusion comme preuve d ergonomie ou d impression reelle.

## Validation demandee

Choisir explicitement une option pour la premiere surface persistante :

1. **D recommande** : app locale de conception + Fusion adaptateur, et autoriser le spike P23 avec une stack UI locale moderne (TypeScript/React/Vite + adaptateur Python local).
2. **B** : palette Fusion persistante comme MVP interactif, avec Fusion au centre de l experience.
3. **C** : app locale autonome avec technologie a preciser avant implementation.
4. Reporter la surface persistante et rester temporairement sur les rapports/commandes existants.

Sans cette validation, Codex peut maintenir le moteur, les rapports et la documentation, mais ne doit pas creer de palette ou d app.