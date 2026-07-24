# ADR-0086 — Recherche de faisabilité et remplissage 3D répété

- Statut : acceptée
- Date : 2026-07-24
- Mission : P64-L08L

## Contexte

La première gate humaine de l’intégration SCIP 0.1.61 a échoué. Le mode `Approfondi` s’arrêtait vers 30 secondes avec `bounded_portfolio_exhausted`, sans plan, sur un projet de 18 conteneurs / 20 éléments. Le vrai projet limite local de Thomas, 28 conteneurs / 30 éléments, échouait également.

Le modèle produit cherchait encore à minimiser son objectif pendant une fenêtre trop courte. Les séries de petits conteneurs identiques ajoutaient en outre un grand nombre de disjonctions binaires alors que leur insertion pouvait être certifiée après résolution de la structure principale.

## Décision

1. SCIP reste le moteur externe 3D prioritaire.
2. Le worker utilise l’emphase officielle `SCIP_PARAMEMPHASIS.FEASIBILITY` de PySCIPOpt et arrête la recherche au premier plan avec `limits/solutions = 1`. La documentation officielle définit cette emphase comme destinée à détecter rapidement la faisabilité : <https://pyscipopt.readthedocs.io/en/latest/tutorials/model.html>.
3. Le plafond produit devient 1 s en Rapide, 5 s en Normal et 120 s en Approfondi. Le plafond de 120 s n’est pas une durée imposée : la recherche retourne dès le premier plan.
4. Pour une famille d’au moins quatre participants strictement identiques, petits et peu hauts, sans réservation, précédence ou région disjointe, deux représentants restent dans le modèle SCIP. Les autres sont insérés ensuite par un remplissage 3D déterministe fondé sur les arêtes X/Y/Z et un appui couvrant entièrement l’empreinte.
5. Si ce remplissage ne trouve pas de place, BGIG réessaie le modèle complet uniquement avec le temps restant. Il n’accorde pas un second budget.
6. Toute proposition, y compris hybride, repasse la projection, le recalcul des appuis, la reconstruction des espaces et le certificat commun BGIG. Un rejet reste un échec.
7. Un premier plan faisable n’est jamais déclaré globalement optimal.

## Garde d’éligibilité du remplissage répété

Une famille est éligible seulement si :

- elle possède une variante unique ;
- ses rotations, dimensions rembourrées et contraintes d’appui sont identiques ;
- le sol est autorisé et un seul appui couvrant suffit ;
- largeur et profondeur maximales ne dépassent pas un quart du monde ;
- la hauteur ne dépasse pas un quart du monde ;
- aucune réservation, précédence d’accès ou région disjointe n’est active.

Deux représentants sont conservés pour que SCIP construise réellement la structure et les possibilités d’appui de cette famille.

## Conséquences

- Le cas privé 28x30 reste local et n’entre pas dans le dépôt.
- Une régression publique 28x30, dérivée uniquement du cas public revu 18x20, exerce la même famille de répétitions.
- Le holdout L08 n’est ni rouvert ni rejoué.
- Le runtime reste hors ligne, sans compte, secret, service, télémétrie ou installation globale.
- `fusion-validated=false` jusqu’au prochain retour humain ; `print-validated=false`.