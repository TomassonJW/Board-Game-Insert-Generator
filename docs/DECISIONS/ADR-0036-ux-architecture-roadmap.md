# ADR-0036 - UX architecture roadmap

## Statut

Propose - gate humaine requise avant implementation UI lourde.

## Date

2026-07-10

## Carte liee

- `P18-M005 - Decider la prochaine architecture UI`

## Contexte

La commande Fusion classique est validee pour generer, inspecter, regenerer, clear et exporter. Elle reste une surface de smoke/developpement: elle ne fournit ni inventaire visuel, ni edition de layout, ni variantes comparables. Le moteur Python doit rester independant de Fusion.

## Options

### Option A - CommandInputs Fusion classique seulement

- Avantages : deja validee, faible cout.
- Inconvenients : flux multi-etapes et edition de boite complete peu ergonomiques.
- Compatibilite MVP : developpement seulement.

### Option B - Palette Fusion HTML/JS

- Avantages : persistance, table assets, vue et edition dans Fusion.
- Inconvenients : pont UI/Fusion, lifecycle et tests plus couteux.
- Compatibilite MVP : bonne apres contrat `BoxFillPlan` stable.

### Option C - App locale/web

- Avantages : UX premium, variantes, inventaire et edition independants du CAD.
- Inconvenients : nouvelle surface de distribution et synchronisation avec Fusion.
- Compatibilite MVP : bonne a moyen terme.

### Option D - Hybride app de conception + Fusion CAD/export

- Avantages : respecte les frontieres moteur/adaptateur et laisse l'UX evoluer vite.
- Inconvenients : deux surfaces a relier via contrat projet/CAD IR.
- Compatibilite MVP : cible strategique, plus couteuse a initier.

## Decision proposee

Court terme : la commande Fusion classique reste obligatoire pour smoke tests, compatibilite et actions CAD/export. Elle ne portera pas l'UX finale.

Prochain MVP UX : prototyper une palette Fusion persistante ou une UI externe apres validation humaine du contrat `BoxFillPlan` et d'un premier flux utilisateur. Moyen terme : converger vers une app locale/web pour la composition, Fusion restant adaptateur CAD/export.

Cette ADR n'autorise ni palette, ni app, ni dependance web, ni changement du moteur. Elle exige une gate humaine de choix de surface avant implementation.

## Consequences

### Positives

- L'UX ne contamine pas le moteur pur.
- Les contrats P18 restent reutilisables par palette et app.

### Negatives

- La commande classique reste temporairement peu confortable.
- Le choix palette/app est differe volontairement.

### Risques

- Commencer une UI avant `BoxFillPlan` creerait une seconde representation du projet.
- Une palette Fusion peut lier trop etroitement l'UX au CAD.

## Alternatives refusees

- Ameliorer indefiniment `quick_asset_box` : refuse comme direction produit.
- Implementer une palette maintenant : refuse sans gate et sans plan de boite executable.
- Introduire une dependance UI majeure : refuse sans ADR acceptee et validation humaine.

## Suivi

- P18-M006 doit proposer P19, sans l'implementer.
- Gate humaine : accepter/refuser la direction UX et choisir le moment de la premiere surface persistante.
