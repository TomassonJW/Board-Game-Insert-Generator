# P64-L09U-R9 — preuve de récupération de performance 0.1.80

Statut : `automated-validated`, candidate 0.1.80 en préparation,
`fusion-validated=false`, `print-validated=false`.

## Verdict automatisé

R9 ramène les deux projets autoritaires vers l’ordre de grandeur historique de
quelques secondes sans changer la disposition certifiée de 0.1.79.

| Projet | Référence lente | Calcul R9 frais | Finalisation R9 | Placement |
| --- | ---: | ---: | ---: | --- |
| CasLimite02+ | 92,968 s au replay R9-A | 3,727 s | 2,654 s | `a3ef…bc46` |
| CasLimite02++ | 87,192 s | 3,911 s | 2,500 s | `a3ef…bc46` |

Ces temps sont des observations locales, pas un seuil universel promis.

## Autorité fonctionnelle conservée

Pour les deux projets :

- effort de calcul : `deep` ;
- statut de calcul et de finalisation : `solution_found` ;
- placement :
  `a3ef2f440a212ed29496fe50072e065a0c861388e6e55e68c548c2bf8817bc46` ;
- CAD IR et plan Fusion produits ;
- conteneurs finalisés puis soustractions plates uniquement ;
- volume positif plat : `0 mm³` ;
- corps positifs plats : `0` ;
- unions plates : `0` ;
- nouveaux corps imprimables liés aux éléments plats : `0` ;
- cavités gelées, profondeurs calibrées et continuité du vide supérieur
  conservées ;
- profondeurs locales observées : `4/6 mm` sur CasLimite02+ et
  `2/4/6 mm` sur CasLimite02++.

## Projets personnels protégés

Les deux replays ont relu les fichiers personnels sans les sauvegarder :

- CasLimite02+ avant et après :
  `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` ;
- CasLimite02++ avant et après :
  `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743`.

`read_only=true`, `repository_payload_written=false`.

## Route R9 certifiée

Le préflight R9 vérifie sur le fixture déterministe déjà versionné :

- solveur minimal `p64-l09u-r9-c-v2` ;
- première voie interne certifiée exécutée avant SCIP ;
- premier groupe géométrique certifié ayant autorité ;
- aucun appel SCIP lorsque cette voie livre la solution ;
- budgets Deep hérités inchangés, dont `180 000 ms` au total ;
- grille produit `0,1 mm` et epsilon numérique `0,0001 mm` distincts.

SCIP reste un repli honnête si le préfixe interne ne livre pas de solution
certifiée. Aucun timeout, impossible ou cache n’est maquillé.

## Validation

- tests ciblés du calcul, des réservations, de SCIP, de la certification, de la
  finalisation, du pipeline soustractif et du package : passés ;
- suite autorisée complète : `953` tests passés, `1` skip prévu ;
- douze modules de corpus, benchmark et tournoi exclus avant import,
  exactement comme documenté ;
- aucun nouveau benchmark, holdout, corpus ou tournoi créé.

La comparaison automatisée avec un ancien dossier installé 0.1.79 n’a pas été
possible : le dossier d’add-in Fusion local était absent au moment du contrôle.
La fidélité est donc démontrée par le digest de placement autoritaire et le
replay fonctionnel complet, sans prétendre à une comparaison de fichiers
installés inexistante.

## Gate restante

La seule gate restante est la recette humaine Fusion 0.1.80 :
`docs/P64_L09U_R9_V_0180_FUSION_GATE_RECIPE.md`.
