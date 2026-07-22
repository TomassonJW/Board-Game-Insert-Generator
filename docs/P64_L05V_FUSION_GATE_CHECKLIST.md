# P64-L05V - Checklist Fusion de capture reelle

## Statut

Gate humaine preparee par P64-L05V-A.

Cette gate ne valide ni l'impression, ni les valeurs physiques, ni la resolution
complete du projet personnel.

## Avant Fusion

Codex prepare le package, l'installe dans le repertoire Fusion local, genere la
fixture p64-l05v-global-void-baseline.bgig.json et verifie le marqueur de
commit. Thomas ne lance aucun script.

## Parcours a observer

1. Recharger l'add-in BGIG puis ouvrir sa palette.
2. Ouvrir la fixture p64-l05v-global-void-baseline.bgig.json.
3. Lancer Calculer l'agencement minimal, puis Matérialiser dans Fusion.
4. Ajouter un conteneur Nouveau bac avec un élément rectangle 8 x 8 x 8 mm.
5. Verifier le message de succes, les voisins conserves, le solve global a zero,
   les details de recertification et l'absence de scene automatique.
6. Changer temporairement l'effort, revenir a Rapide puis recalculer. Verifier
   Plan témoin certifié, warm start accepte, recherche poursuivie et aucun
   cache hit revendique.
7. Cliquer DEV · Capturer le cas. Verifier que le bundle est ecrit localement,
   et qu'aucun calcul, finalisation, CAD ou regeneration de scene n'est lance.
8. Relever dans les details techniques : identite, lanes, budgets, temps,
   provenance et raison d'arret.

## Attendus et refus

Attendus :

- container_placed_in_global_void ou un diagnostic de fallback explicite ;
- anciens placements monde inchanges sur le succes ;
- absence de faux pourcentage, ETA ou Annuler decoratif ;
- activite, etape et temps ecoule observables ;
- capture DEV locale, filtree et sans effet de domaine.

Un KO utile doit contenir l'etape, le statut visible, la methode, l'effort, la
raison d'arret, et une capture du detail technique si possible. Ne pas copier le
bundle dans le depot ; signaler seulement son chemin local ou le laisser a
disposition pour une reprise explicitement autorisee.

## Retour attendu

P64-L05V Fusion OK 0.1.58 - commit <sha>

Ou : P64-L05V Fusion KO contextuel suivi des faits observes.
