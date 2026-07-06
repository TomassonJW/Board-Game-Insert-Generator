# Log - P7 Assembly-compatible document required

## Date

2026-07-06

## Declencheur

Smoke test humain `P7-M001V2` bloque par contexte Fusion : le document actif etait
un document `Part Design` qui refuse plusieurs composants. Fusion a retourne :

```text
3 : Failed to create component: Part Design documents can only contain one component, please add this Part to an Assembly to add multiple components.
```

## Interpretation

La strategie produit reste correcte : un module physique BGIG doit etre un
`Component` Fusion unique avec une occurrence compacte et une occurrence eclatee
liee. Le blocage vient du contexte document Fusion, pas de la CAD IR ni du
modele produit.

## Correction

- Ajout d'une detection testable de l'erreur Part Design single-component.
- Ajout d'un statut/message `assembly document required`.
- Interception de l'erreur Fusion dans l'add-in pour afficher un message
  actionnable plutot que l'erreur brute.
- Documentation de la procedure P7-M001V3 : ouvrir/creer un document
  Assembly-compatible ou ajouter le Part a une Assembly avant de lancer l'add-in.
- Aucun retour aux copies independantes de bodies.

## Suite

Stop pour smoke test humain `P7-M001V3`.
