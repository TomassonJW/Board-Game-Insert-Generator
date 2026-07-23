# P64-L06A - Inventaire des cas réels locaux

Date : 2026-07-23

Statut : done, automated-validated ; fusion-validated: false ; print-validated: false.

## Résultat

Le répertoire local contient 13 SolverCaseBundles. Les 13 passent le validateur canonique : schéma, empreinte globale, empreintes des composants, projet normalisé et réglages solveur sont cohérents.

Aucun journal automatique 0.1.59 n'existait encore au moment de l'inventaire, ce qui est normal immédiatement après l'installation. Cette absence ne bloque pas la campagne.

Aucun nom de projet, chemin local, nom d'élément ou identifiant personnel n'est copié dans cette preuve.

## Classement

| Bundle | Groupes / contenus | État observé | Classement |
| --- | ---: | --- | --- |
| `cab9838464a2` | 2 / 2 | solution fraîche certifiée | smoke simple, non promu comme preuve de capacité |
| `4654c5c26d93` | 12 / 16 | solution fraîche certifiée | exploration locale, non promue |
| `dfa2ac115d79` | 17 / 19 | solution certifiée relue | exploration locale, non promue |
| `20a029b2ad70` | 18 / 20 | plan solution devenu stale | paire pré-R1 avec `48a98a092851`, non promue |
| `48a98a092851` | 18 / 20 | échec frais dans le budget | paire pré-R1, non promue |
| `7407d1d504e0` | 17 / 19 | solution certifiée relue | exploration locale, non promue |
| `bf8ba8cdac34` | 18 / 20 | plan solution devenu stale | paire pré-R1 avec `b2ae18bbc47c`, non promue |
| `b2ae18bbc47c` | 18 / 20 | échec frais dans le budget | paire pré-R1, non promue |
| `b6554b7f7d51` | 18 / 20 | insertion positive dans le vide global | preuve positive complémentaire, non promue dans L06A |
| `087ad387d219` | 39 / 44 | plan solution devenu stale après de nombreux ajouts | parcours artificiellement long, non promu |
| `c558a4f2e15c` | 39 / 44 | échec frais dans le budget | même projet que `087ad387d219`, non promu |
| `13f90ebe611c` | 18 / 20 | plan solution devenu stale après ajout d'un contenu | paire cohérente récente avec `0693aef760d9` |
| `0693aef760d9` | 18 / 20 | échec global frais, cache manqué, aucun cache négatif | seul cas retenu puis anonymisé |

La paire récente partage exactement la même empreinte de projet `500ae2a115d6...`. Elle décrit un ajout de contenu, pas l'ancien refus incrémental d'un nouveau conteneur. Cette limite reste explicite et n'est pas maquillée.

## Cas intégré

Le bundle `0693aef760d92fb7b42f21210ec36efdda4ee738effbf237861cb5899c3f508d` produit le cas :

- identifiant : `real-18-containers-20-contents-normal` ;
- tier : `extended` ;
- réglage : Auto / Normal ;
- 18 conteneurs et 20 contenus ;
- baseline : `no_solution_within_budget` ;
- source revue : `reviewed-local-bundle-20260723-001` ;
- fixture : `tests/fixtures/p64_l06a_reviewed_real_case.v1.json` ;
- empreinte du corpus autonome : `dafc18a5610fce524f69756c6001b652ac36c397ed17f2075ed5c760cb2a01e5`.

L'anonymisation remplace le nom du projet, les noms et identifiants des conteneurs, contenus, éléments plats et remplissages. Les références internes sont réécrites de manière cohérente. Les métadonnées différées non utiles au solveur sont supprimées. La trace d'interaction et le contexte client ne sont pas importés.

La recherche de marqueurs personnels et de chemins dans la fixture est vide.

## Replay

Deux répétitions donnent le même résultat fonctionnel :

- attentes satisfaites : oui ;
- transition de baseline : stable ;
- résultat : `no_solution_within_budget` ;
- empreinte fonctionnelle : `24baa7acdb6dea46df1a145569e493b94fdb58871d5f6fc991e3e3700cdf463e` ;
- médiane observée : 3 370,863 ms, mesure informative seulement.

Le replay ne lance ni finalisation, ni CAD, ni scène Fusion. Il ne modifie pas le solveur.

## Vérifications

- suite complète : OK, code retour 0 après environ 160 s ;
- tests ciblés corpus : 6/6 ; constructeur et fixture : 3/3 ;
- garde documentaire : 2/2 ; alignement Fusion-only : 6/6 ;
- Ruff ciblé et compilation Python : OK ;
- inventaire local : 13/13 bundles valides ;
- anonymisation du projet : testée ;
- constructeur de corpus séparé et sans modification de la source : testé ;
- fixture versionnée : validation et replay réussis ;
- replay réel répété : stable ;
- aucune promotion des 12 autres bundles ;
- aucun journal ou projet personnel ajouté au dépôt.

## Suite

P64-L06A est terminée. P64-L06B peut construire les générateurs et splits T0/T1 en combinant le corpus L05D1 et ce cas réel étendu, sans nouvelle action humaine.
