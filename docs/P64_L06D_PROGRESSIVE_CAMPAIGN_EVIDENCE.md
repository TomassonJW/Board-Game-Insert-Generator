# P64-L06D — preuve de campagne progressive autonome

## Résultat

La campagne est terminée et aucun changement algorithmique n'est intégré. Les trois variantes de lanes au même budget produisent exactement les mêmes résultats fonctionnels que la version courante sur discovery puis tuning. Le holdout, ouvert seulement après la sélection scellée `no_algorithm_change_v1`, confirme l'absence de gain et ne révèle aucune contradiction avec l'oracle.

C'est un résultat négatif valide : intégrer l'une des variantes aurait ajouté du code sans améliorer le solveur.

Statut : `implemented-core`, `automated-validated`, `negative-result-accepted`.

`fusion-validated: false`. `print-validated: false`.

## Régressions et baseline

Les huit cas historiques passent : 8/8 attentes satisfaites, dont deux solutions recertifiées à neuf et six absences de solution attendues. Une seconde exécution du même run saute 8/8 résultats valides et conserve le checkpoint à l'identique.

Sur les 64 cas discovery :

| Comparateur | Faisables trouvés | Faisables manqués | Impossibles prouvés | Impossibles non sur-vendues | Hors portée |
| --- | ---: | ---: | ---: | ---: | ---: |
| solveur BGIG courant | 0 | 19 | 0 | 8 | 37 |
| petit oracle exact | 4 | 0 | 2 | 0 | 58 |

L'oracle ne couvre volontairement que six petits cas ; il retrouve les quatre témoins faisables et les deux impossibilités de sa portée.

## Contrôles d'entrée

Les trois contrôles discovery montrent que les commandes absentes du schéma et les réservations expliquent une partie importante des refus, sans résoudre le problème de recherche à grande échelle :

| Contrôle | Faisables trouvés | Faisables manqués | Impossibles non sur-vendues | Hors portée |
| --- | ---: | ---: | ---: | ---: |
| rotation autorisée | 12 | 32 | 17 | 3 |
| réservations retirées | 6 | 15 | 8 | 35 |
| rotation autorisée et réservations retirées | 18 | 28 | 17 | 1 |

Ces transformations portent sur les entrées du benchmark. Elles ne sont pas des améliorations du solveur et n'ont pas été proposées pour intégration.

Le premier contrôle a dépassé le délai de retour de son enveloppe de commande. L'état réel a ensuite été vérifié sans relance : aucun processus Python restant, checkpoint `phase_complete`, 64 résultats présents, digest du résumé égal à celui du checkpoint. Le cas n'a donc pas été exécuté deux fois.

## Tournoi des trois hypothèses

Chaque variante conserve trois lanes Rapide et les mêmes plafonds publics.

| Hypothèse | Discovery : trouvés / manqués / hors portée | Tuning : trouvés / manqués / hors portée | Décision |
| --- | --- | --- | --- |
| version courante | 0 / 19 / 37 | 0 / 21 / 33 | témoin |
| `lane_center_quick_v1` | 0 / 19 / 37 | 0 / 21 / 33 | rejetée, aucun gain |
| `lane_lowest_quick_v1` | 0 / 19 / 37 | 0 / 21 / 33 | rejetée, aucun gain |
| `lane_interleave_quick_v1` | 0 / 19 / 37 | 0 / 21 / 33 | rejetée, aucun gain |

Aucune solution n'est perdue parce qu'aucune hypothèse ni la baseline n'en trouve dans ces deux splits. Aucun certificat n'est rejeté et aucune contradiction d'oracle n'est observée.

## Sélection et holdout

Avant toute ouverture du holdout, la campagne a scellé :

- hypothèse : `no_algorithm_change_v1` ;
- digest du candidat : `8ae8c9a93a5bdacd73841edaa90b34540926fd708f17b6c67268b1e911596d4b` ;
- digest de sélection : `4c84aaa5a864fa04a7c6cfeed2c338f549c60f3c4f9a0dd4928132ff10151d7d`.

Le holdout exécute ensuite 64 cas avec le solveur courant et 64 avec l'oracle de référence :

- solveur courant : 19 faisables manqués, 8 impossibles non sur-vendues, 37 cas hors contrôle représentable ;
- oracle exact : 1 impossible prouvée, 63 cas hors de sa petite portée ;
- solution certifiée : 0 ;
- contradiction d'oracle : 0 ;
- digest du résumé : `437b26879bfb723e3499223e94c4661d10b74ec183ba8c75d1980d0bc9c6fa28`.

Le holdout ne justifie aucun réglage postérieur. Le soak est volontairement omis : aucune hypothèse n'a produit le moindre gain fonctionnel à confirmer.

## Coût et intégrité

- 904 exécutions cas/comparateur enregistrées ;
- un worker fonctionnel ;
- zéro dépendance externe ;
- zéro changement des budgets publics ;
- zéro changement du solveur produit ;
- checkpoints et résultats écrits atomiquement ;
- digest du manifest : `53db786793dee3a26128f4db28cc830f68dde394262cd7ffbfad27cb895a85ee` ;
- digest du rapport versionné : `27722e8fdbc6662c45ba6a33714f37cf2197de9decd3a76fb3b05993198b1fd5`.

## Lacunes classées

1. Le schéma projet ne permet pas d'imposer l'absence de rotation ; 33 à 37 cas par split restent donc hors comparaison stricte pour le solveur courant.
2. Les réservations supérieures empêchent le petit oracle de servir de référence sur la majorité du corpus.
3. Même après relaxation des contrôles, les familles avec de nombreux conteneurs restent fréquemment sans solution dans le budget.
4. Changer seulement la troisième lane Rapide ne suffit pas : les trois variantes sont fonctionnellement indiscernables de la baseline.

La prochaine amélioration ne doit donc pas être choisie au hasard parmi ces lanes. Elle devra cibler une lacune plus profonde et passer une nouvelle gate mesurée.

## Validation automatisée

- tests ciblés adapters : 9/9 OK ;
- tests ciblés campagne : 8/8 OK ;
- garde documentaire : 2/2 OK ;
- alignement Fusion-only et frontière `adsk` : 6/6 OK ;
- suite complète : 715/715 OK en 209,367 s ;
- Ruff ciblé et `py_compile` ciblé : OK ;
- rapport et sélection vérifiés par digest : OK ;
- `git diff --check` : OK avant staging.

## Suite

P64-L06E doit enregistrer la décision négative : aucune amélioration algorithmique intégrée pendant ce premier Goal. Les hypothèses de travail suivantes restent au backlog, sans élargir T0/T1 et sans rouvrir le holdout utilisé.
