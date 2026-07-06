# Log - P7 occurrence name guard

Date : 2026-07-06

## Contexte

Smoke test humain `P7-M001V3` KO dans un contexte Fusion compatible avec la
creation de composants : l'add-in a echoue avec :

```text
property '_get_name' of 'Occurrence' object has no setter
```

## Interpretation

La strategie produit reste valide : un module physique BGIG doit correspondre a
un `Component` Fusion unique, avec une occurrence compacte et une occurrence
eclatee liee. Le probleme vient du renommage direct des occurrences, qui peut
etre refuse par l'API Fusion selon le contexte.

## Correction

- Suppression de toute assignation directe `occurrence.name = ...` dans l'add-in.
- Conservation des noms lisibles sur les `Component`, bodies, sketches et
  features sources.
- Ajout d'une politique de nommage dans le plan hors Fusion : les labels
  d'occurrences sont informatifs et non assignes directement dans Fusion.
- Ajout du message Fusion `Occurrence direct rename attempted: no`.
- Mise a jour du smoke test : ne pas exiger de noms exacts d'occurrences dans le
  Browser Fusion ; verifier les composants sources, les roles reportes et la
  liaison compact/exploded.

## Statut

Code et tests hors Fusion a relancer. Stop ensuite pour smoke test humain
`P7-M001V4`.