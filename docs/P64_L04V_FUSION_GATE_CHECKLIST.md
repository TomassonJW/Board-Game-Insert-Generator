# P64-L04V — Checklist de gate Fusion combinée

Statut : `ready-human-gate`.

Cette gate confirme le parcours incrémental P64-L04 dans Fusion 360. Elle ne
valide ni valeur physique, ni slicer, ni imprimabilité, ni impression réelle.

## Préparation automatisée attendue

Le script `scripts/fusion/prepare_p64_l04v_gate.ps1` doit :

- exécuter les régressions L04A/B/C concernées ;
- vérifier le scénario pur `placement_reused` puis `global_solve_required` ;
- installer l'add-in depuis le commit courant ;
- vérifier le manifest 0.1.58, les runtimes copiés et les marqueurs L04C ;
- écrire les réglages UI locaux et le marqueur de commit ;
- créer le projet `p64-l04v-pocket-baseline.bgig.json` dans Documents/BGIG/projects.

## Observation humaine

1. Recharger l'add-in 0.1.58 et ouvrir la palette dans un document Fusion vide.
2. Ouvrir le projet de baseline, calculer son plan minimal puis matérialiser.
3. Vérifier l'activité immédiate, l'étape et le temps écoulé ; aucun pourcentage,
   ETA ou bouton Annuler ne doit être proposé.
4. Créer un corps utilisateur témoin hors BGIG, nommé `TEMOIN_UTILISATEUR`.
5. Ajouter dans `Bac L04` un élément de `8 × 16 × 8 mm` et vérifier :
   `placement_reused`, compteur solveur global à zéro, voisins inchangés.
6. Ajouter ensuite un élément de `20 × 20 × 10 mm` et vérifier : fallback explicite,
   ancien plan stale et absence de solve global automatique.
7. Calculer explicitement, constater que la scène est désynchronisée, puis utiliser
   `Mettre à jour la scène`.
8. Vérifier une seule scène BGIG, le témoin utilisateur préservé, l'identité de
   l'artefact et les détails de provenance, méthodes, budgets, phases, incumbent
   et raisons d'arrêt.

## Retour formel

Réponse attendue :

```text
P64-L04V Fusion OK 0.1.58 - commit <sha>
```

Ou un KO contextuel avec le projet, l'étape, le statut visible et le diagnostic.
