# P64-L09R-V — Recette complète de la gate Fusion

Date de préparation : 2026-07-25

Statut : `installed-awaiting-human-retest`, `human-gate-required`, `print-validated=false`.

Cette recette remplace entièrement P64-L09V 0.1.63, annulée sans observation. Elle ne réactive ni l’anti-chute dure, ni la finalisation obligatoire.

## 1. Ce que Codex doit préparer avant ton intervention

Thomas ne lance aucune commande PowerShell. Dans la mission P64-L09R-V, Codex doit :

1. partir du commit P64-L09R-F intégré et propre sur `origin/main` ;
2. exécuter `scripts/fusion/prepare_p64_l09rv_gate.ps1` sans `-DryRun` ;
3. installer exactement l’add-in BGIG 0.1.65 et le runtime SCIP scellé ;
4. vérifier le marqueur `bgig_installed_commit.txt`, la version 0.1.65 et les marqueurs worker/UI ;
5. installer les deux fixtures publiques dans `Documents\BGIG\projects` ;
6. sélectionner la fixture plateau avec calcul Normal et finition Rapide ;
7. confirmer le reçu `p64-l09rv-preflight-summary.json` et son digest ;
8. te donner seulement les manipulations Fusion restantes ci-dessous.

Si l’écriture dans `%APPDATA%` est bloquée, Codex doit s’arrêter avec exactement :

```text
Local AppData write blocked. Use Local/Handoff or approve filesystem write.
```

## 2. Préflight automatisé déjà exigé

Avant installation, toutes ces preuves doivent être vertes :

- cas public 28x30 : reçu public intègre, 28 placements, solution recertifiée, aucun holdout lu ;
- fixture préférence : petit-dessous/grand-dessus observé avec support par enveloppes ;
- inversion nécessaire : reste admissible et la préférence reste souple ;
- ouverture : le diagnostic matière peut être négatif sans rendre le plan enveloppe infaisable ;
- fixture plateau : plan minimal certifié, réservation transmise et CAD minimal prêt ;
- finition séparée : plan final certifié et CAD final prêt ;
- collision, réservation et entrée invalides : rejet fail-closed ;
- timeout : `no_solution_within_budget`, jamais `proven_impossible` sans preuve formelle ;
- échec de finition : plan minimal strictement inchangé et encore matérialisable ;
- mesures distinctes : durée observée du calcul et durée observée de la finition, sans les confondre ;
- aucun benchmark historique et aucun holdout consommé ne sont ouverts.

## 3. Observation au repos

Après confirmation d’installation par Codex :

1. recharge complètement l’add-in BGIG 0.1.65 ;
2. ouvre **BGIG — Atelier de rangement** ;
3. ne lance encore aucune opération ;
4. confirme que `Calculer`, `Finaliser` et `Matérialiser` sont tous visibles ;
5. confirme que la jauge est totalement absente et ne laisse aucun espace vide ;
6. ouvre Réglages et confirme les deux sélecteurs indépendants ;
7. change successivement le budget de calcul vers Rapide, Court, Normal, Long et Approfondi ; confirme que le champ adjacent devient immédiatement `3 s max`, `10 s max`, `20 s max`, `60 s max`, puis `3 min max`, sans toucher au budget de finition ;
8. change ensuite uniquement le budget de finition et confirme qu’il ne modifie ni la sélection ni le temps affiché du calcul.

KO si un bouton disparaît, si un budget est éditable ou faux, si le temps de calcul attend une autre action pour se rafraîchir, ou si une zone de jauge reste réservée au repos.

## 3 bis. Contrôle correctif sur le cas qui a révélé le défaut

Avant les fixtures publiques, reprends le projet local observé : boîte de 60 mm, hauteur utile 59,6 mm, plan sans plateau culminant à 52,8 mm, plateau 100 × 100 × 1 mm.

1. sélectionne Calcul Normal — `20 s max` ;
2. clique `Calculer` une seule fois ;
3. confirme que le résultat devient une solution certifiée et matérialisable, et non un faux impossible ;
4. relève la durée, le moteur et le nombre de placements ;
5. sans finition, clique `Matérialiser` ;
6. vérifie que le plan minimal atteint le support du plateau, que la réservation est présente et que les cavités restent ouvertes.

KO si le cas reste sans solution à tous les budgets, si la hauteur dépasse 59,6 mm, si une cavité est bouchée ou si une finition est exigée avant matérialisation.

## 4. Fixture 01 — préférence souple et ouvertures

Ouvre `p64-l09rv-01-preference-envelope.bgig.json`.

1. sélectionne **Auto intelligent** et **Normal — 20 s max** ;
2. clique `Calculer` une seule fois ;
3. pendant le calcul, confirme que la jauge apparaît immédiatement au-dessus des boutons, sur toute la largeur ;
4. confirme que le texte nomme le calcul, l’étape, le temps écoulé et le budget 20 s ;
5. observe environ une mise à jour par seconde ;
6. confirme que les trois boutons restent visibles mais désactivés pendant l’opération ;
7. à la fin, confirme que la jauge disparaît entièrement ;
8. vérifie que les deux petits bacs sont sous le grand bac ;
9. vérifie que le résultat est présenté comme un plan certifié, sans prétendre que cet ordre souple constitue un certificat physique ;
10. note le statut, le moteur, le temps affiché et tout diagnostic matière visible.

Cette fixture doit aussi montrer le nouveau produit : un grand bac peut être admis au-dessus des ouvertures de petits bacs lorsque les enveloppes XY le portent. L’ancien rejet anti-chute ne doit pas réapparaître.

## 5. Fixture 02 — plateau, budgets et plan minimal

Ouvre `p64-l09rv-02-tray-separated-flow.bgig.json`.

### Calcul Rapide

1. sélectionne **Rapide — 3 s max** pour le calcul ;
2. clique `Calculer` ;
3. relève durée, statut, moteur et raison d’arrêt ;
4. si aucun plan n’est trouvé dans 3 s, confirme le libellé « aucune solution dans le budget » et jamais « impossible » sans preuve ;
5. confirme la disparition totale de la jauge après le résultat.

### Calcul Normal

1. sélectionne ensuite **Normal — 20 s max** ; le plan précédent doit devenir à recalculer ;
2. clique `Calculer` ;
3. relève de nouveau durée, statut, moteur et raison d’arrêt ;
4. confirme que le plateau/livret apparaît dans les réservations du plan ;
5. confirme que `Finaliser` et `Matérialiser` deviennent disponibles quand le plan minimal est courant.

### Matérialisation minimale avant finition

1. sans cliquer `Finaliser`, clique `Matérialiser` ;
2. confirme une jauge indéterminée, sans pourcentage ni délai inventé ;
3. confirme que la matérialisation reste sur une phase Fusion réelle ;
4. après disparition de la jauge, vérifie que la scène correspond à `minimal_layout` ;
5. inspecte les bacs, les cavités et les retraits plateau/livret ;
6. confirme qu’aucun volume de finition implicite n’a été ajouté.

KO si Fusion impose une finition avant cette matérialisation ou si la scène provient d’un plan partiel/non certifié.

## 6. Finition séparée et plan final

Sur la même fixture 02 :

1. sélectionne **Rapide — 3 s max** pour la finition ;
2. clique `Finaliser` ;
3. confirme que la jauge réapparaît avec un budget propre de 3 s, indépendant des 20 s du calcul ;
4. relève durée, statut et raison d’arrêt de la finition ;
5. si la finition échoue ou atteint sa deadline, confirme que le plan minimal reste courant et que `Matérialiser` cible encore ce minimal ;
6. si la finition réussit, confirme qu’un `finalized_plan` recertifié devient disponible ;
7. clique alors `Matérialiser` ;
8. confirme la jauge Fusion indéterminée, puis sa disparition complète ;
9. vérifie que la scène correspond maintenant à l’identité du plan final ;
10. confirme que cavités et réservations restent intactes.

Tu peux relancer explicitement `Finaliser`, mais aucun double clic concurrent ne doit démarrer une seconde finition.

## 7. Résultat à me renvoyer

Pour chaque opération, renvoie ce tableau complété :

| Fixture | Action | Budget affiché | Durée observée | Statut | Moteur / phase | Raison d’arrêt | Jauge active puis absente | Scène ciblée | OK/KO |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 préférence | Calculer | 20 s max |  |  |  |  |  | aucune |  |
| 02 plateau | Calculer | 3 s max |  |  |  |  |  | aucune |  |
| 02 plateau | Calculer | 20 s max |  |  |  |  |  | aucune |  |
| 02 plateau | Matérialiser | indéterminée |  |  | Fusion |  |  | minimal_layout |  |
| 02 plateau | Finaliser | 3 s max |  |  |  |  |  | minimal conservé ou final prêt |  |
| 02 plateau | Matérialiser | indéterminée |  |  | Fusion |  |  | finalized_plan si disponible |  |

Ajoute :

- une capture au repos montrant les trois boutons et l’absence totale de jauge ;
- une capture pendant calcul ou finition montrant la jauge pleine largeur ;
- une capture de la scène minimale avec plateau ;
- une capture de la scène finale si la finition réussit ;
- le texte exact de tout diagnostic KO.

## 8. Frontières de validation

Cette gate peut produire `fusion-validated` pour le parcours P64-L09R. Elle ne valide pas :

- l’impression réelle ;
- les tolérances physiques ;
- la pose d’un conteneur fermé ou d’un couvercle ;
- une règle anti-chute matérielle ;
- l’optimalité globale du solveur ;
- la modularité ou les formes différées.

Même en cas de gate OK : `print-validated=false` reste obligatoire.