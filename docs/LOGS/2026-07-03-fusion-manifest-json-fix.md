# Log - Fusion manifest JSON compatibility fix

## Date

2026-07-03

## Contexte

Le smoke test manuel P4-M003 a revele que Fusion 360 refusait l'ajout local de
l'add-in avec le message demandant un script et un `.manifest` portant le meme
nom que le dossier.

Le dossier, le script et le fichier `.manifest` portaient bien le meme nom, mais
le manifeste etait au format XML. La documentation Autodesk actuelle decrit le
manifeste comme un fichier texte en JSON et indique que le nom de l'add-in est
defini par le dossier, le fichier source principal et le fichier manifeste.

## Correction

- Conversion de `BoardGameInsertGenerator.manifest` en JSON.
- Passage de `autodeskProduct` a `Fusion`.
- Ajout d'un test hors Fusion verifiant le trio dossier/script/manifeste et les
  champs essentiels du manifeste.
- Mise a jour de la procedure d'installation locale avec les chemins recherches
  par Fusion et la selection manuelle du dossier exact.

## Statut

La decouverte de l'add-in doit etre retestee dans Fusion 360. La generation CAD
reste `manual validation required` tant que le smoke test complet n'a pas ete
execute dans Fusion.
