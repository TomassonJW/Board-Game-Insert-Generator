# P64-L06E — décision algorithmique du premier Goal

## Décision

Aucune amélioration algorithmique n'est intégrée dans ce premier Goal P64-L06.

Les trois variantes de lanes Rapide ont été rejetées : elles ne trouvent aucun cas faisable supplémentaire sur discovery, aucun sur tuning et ne justifient donc ni modification du solveur, ni soak. La sélection formelle est `no_algorithm_change_v1`.

Statut : `done`, `automated-validated`, `negative-result-accepted`.

`fusion-validated: false`. `print-validated: false`.

## Gate finale

| Critère | Résultat | Décision |
| --- | --- | --- |
| aucune solution historique perdue | 8/8 régressions satisfaites | conforme |
| certificat BGIG frais | 2 solutions historiques recertifiées ; aucun rejet | conforme |
| qualité lexicographique | aucun comportement produit modifié | conforme |
| budgets Rapide/Normal/Approfondi | inchangés | conforme |
| stabilité fonctionnelle | résultats et digests stables ; reprise sans double exécution | conforme |
| choix avant holdout | sélection scellée avant ouverture | conforme |
| gain objectif | 0 gain discovery, 0 gain tuning, 0 gain holdout | échec de la gate d'amélioration |
| dépendance externe | 0 | conforme |

La gate exige un progrès objectif. Elle est donc volontairement refusée pour les trois candidats algorithmiques, même si aucune régression n'est observée.

## Candidats refusés

- `lane_center_quick_v1` : identique à la baseline ;
- `lane_lowest_quick_v1` : identique à la baseline ;
- `lane_interleave_quick_v1` : identique à la baseline.

Aucun de ces changements ne doit être réintroduit sans nouvelle preuve. Le simple remplacement de la troisième lane Rapide ne cible pas la limite principale révélée par le corpus.

## Ce que le Goal a réellement amélioré

Le solveur produit ne devient pas meilleur pendant ce Goal. En revanche, sa mesure devient nettement plus fiable :

- journal local automatique sans bouton DEV ;
- inventaire des cas réels sans blocage humain ;
- 200 cas versionnés, dont un holdout fermé ;
- deux comparateurs offline sans dépendance ;
- petit oracle exact pour les cas dans sa portée ;
- runner atomique, reprenable et vérifié ;
- rapport de 904 exécutions avec digests ;
- décision négative traçable au lieu d'une amélioration forcée.

## Lacunes conservées

1. Le schéma projet ne permet toujours pas d'imposer une interdiction de rotation.
2. Le petit oracle exact ne couvre pas les réservations, plusieurs niveaux ou de nombreux conteneurs.
3. La recherche courante manque les cas faisables multi-conteneurs dans ses plafonds, même après séparation des contraintes d'entrée.
4. Le holdout de ce Goal est désormais consommé ; une future sélection doit utiliser une nouvelle version de corpus ou un nouveau holdout scellé.

Ces lacunes ne sont pas des autorisations implicites de modifier le schéma, les budgets ou l'architecture. Une évolution structurelle exigera une mission distincte et, si nécessaire, une ADR et un nouveau GO.

## Validation héritée et clôture

La décision repose sur la campagne L06D intégrée dans `main` au SHA `0b84d003090b2551c12013f83956b22d4ff1b038` :

- 904 exécutions cas/comparateur ;
- tests ciblés adapters 9/9 ;
- tests ciblés campagne 8/8 ;
- garde documentaire 2/2 ;
- alignement Fusion-only 6/6 ;
- suite complète 715/715 en 209,367 s ;
- Ruff et compilation ciblés OK ;
- SHA distant `main` vérifié.

L06E est documentaire : aucun fichier du solveur, de Fusion, de géométrie ou du manifest n'est modifié.

## Suite

Le premier Goal P64-L06 est terminé. Aucune action humaine n'est nécessaire pour valider cette décision négative. Les usages futurs de l'add-in continueront à enrichir automatiquement le journal local ; une nouvelle campagne ne doit être lancée que pour une hypothèse précisément cadrée et avec un holdout renouvelé.
