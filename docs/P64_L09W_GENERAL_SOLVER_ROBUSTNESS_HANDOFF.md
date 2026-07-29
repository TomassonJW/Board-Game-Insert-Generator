# P64-L09W — handoff de robustesse générale du solveur

Date : 2026-07-29.

Statut : `ready-for-autonomous-goal`, `priority-before-original-roadmap`,
`no-product-code-yet`.

## 1. Déclencheur et autorité

P64-L09U-R9-V est `human-positive` sur Fusion 0.1.80. La performance des deux
cas de référence est récupérée et leurs résultats fonctionnels restent acquis.

Thomas ouvre maintenant une priorité distincte : le solveur doit devenir
robuste sur une grande diversité de projets réalisables, au lieu d’être
optimisé autour de quelques cas limites connus. Cette priorité passe avant la
reprise de P64-L10 et de la roadmap d’origine.

Le GO autonome est acquis. La tâche de reprise crée immédiatement un Goal
Codex, sans budget de tokens inventé, puis mène les missions atomiques de ce
programme jusqu’à une preuve générale honnête et, si du code produit est
retenu, une nouvelle candidate Fusion installée et une recette humaine finale.

## 2. Objectif produit honnête

Améliorer autant que raisonnablement possible :

- le taux de solutions certifiées sur les cas réalisables du domaine produit
  déclaré ;
- le temps jusqu’à la première solution certifiée ;
- la stabilité après ajout, retrait ou modification d’un paramètre ;
- la finalisation et la matérialisation, mesurées séparément ;
- la qualité du diagnostic lorsqu’une limite est atteinte.

Une cible comme `95 %` ou `99 %` n’a de sens que sur un domaine, une
distribution et des limites de temps déclarés avant la mesure. Il est interdit
de promettre `99 % de tous les cas possibles` : le placement 3D combinatoire
peut devenir extrêmement difficile même quand une solution existe.

Cible de travail à confirmer après la baseline :

- au moins `95 %` de solutions certifiées sur un holdout faisable par
  construction couvrant le domaine rectangulaire V0.1 pris en charge ;
- objectif renforcé de `99 %` sur les familles courantes et les cas faciles à
  moyens ;
- zéro faux `impossible`, zéro solution non certifiée et zéro régression
  géométrique ;
- temps publiés par palier et par percentile, sans seuil universel inventé.

Ces nombres sont des critères candidats à préenregistrer, pas un résultat déjà
démontré.

## 3. Ce qui existe déjà et ne doit pas être recréé aveuglément

Le dépôt possède déjà :

- le corpus P64-L05D1 et sa gate A/B ;
- P64-L06B avec 192 recettes T0/T1, cas faisables par construction, cas
  impossibles prouvés et splits `discovery`, `tuning`, `holdout` ;
- le runner atomique et reprenable P64-L06D ;
- P64-L07 et P64-L08 avec plusieurs moteurs, un corpus 3D adversarial, des
  témoins X/Y/Z et des campagnes scellées ;
- le runtime SCIP produit et les lanes internes actuelles ;
- la télémétrie R9 du calcul, de la certification et des coûts plats.

Les anciens holdouts L06, L07 et L08 sont consommés. Ils restent des
régressions historiques, jamais un nouveau contrôle fermé.

La première mission doit auditer ces artefacts et déterminer ce qui est
réutilisable. Elle ne génère pas immédiatement des milliers de fixtures et ne
change pas encore le solveur.

## 4. Lacunes à vérifier en P64-L09W-A

L’audit doit prouver ou réfuter les lacunes suivantes :

1. les corpus historiques ne représentent pas le parcours produit 0.1.80
   complet depuis un projet utilisateur jusqu’au certificat, à la
   finalisation, au CAD IR et à la matérialisation ;
2. la matrice actuelle n’impose pas explicitement les taux de remplissage
   demandés autour de `30 %`, `65 %` et `95 %` ;
3. elle ne couvre pas systématiquement `0, 1, 2, 3, 4, 5, 6 et 10`
   plateaux/livrets avec des ordres, orientations et profondeurs variés ;
4. elle privilégie plusieurs patrons synthétiques réguliers et ne mesure pas
   assez les dimensions X/Y/Z hétérogènes, les rapports de forme extrêmes, la
   fragmentation et les petites marges sur les trois axes ;
5. elle ne classe pas assez les échecs après édition locale, reconstruction
   froide, témoin recertifié ou cache refusé ;
6. les métriques de succès produit, de première solution, de finalisation et
   de matérialisation ne sont pas encore réunies dans une même campagne.

## 5. Domaine initial à cadrer

P64-L09W reste d’abord dans le domaine produit rectangulaire V0.1 réellement
pris en charge. Il ne transforme pas les futures formes T2 à T4 en critère
immédiat et ne change aucune valeur physique.

La matrice doit au minimum croiser, sans prétendre réaliser tout le produit
cartésien :

- contenus par conteneur : `1, 2, 4, 8, 16, 32, 64` ;
- conteneurs : `1, 2, 4, 8, 12, 18, 30, 50, 64` ;
- profils : beaucoup de contenus seuls, peu de conteneurs très chargés,
  beaucoup de conteneurs, et beaucoup des deux ;
- occupation utile cible : proche de `30 %`, `65 %`, `85 %` et `95 %` ;
- une à plusieurs couches Z, hauteurs et rapports X/Y/Z variés ;
- orientations, symétries, dimensions presque égales et dimensions extrêmes ;
- boîtes petites, moyennes et grandes dans le domaine supporté ;
- `0, 1, 2, 3, 4, 5, 6 et 10` plateaux ou livrets, dessous, dessus ou
  superposés selon les règles produit ;
- réservations, cavités, accès, parois minimales et profondeurs locales
  existantes ;
- calcul froid, ajout, retrait et modification d’un paramètre.

Le taux volumique seul n’est pas une mesure suffisante. Deux projets à `95 %`
peuvent avoir une difficulté radicalement différente selon les marges par axe,
la fragmentation, les appuis, les réservations et le nombre de variantes.

## 6. Génération et vérités

Les cas positifs sont générés de préférence `faisables par construction` :

1. construire indépendamment un placement valide et complet ;
2. en dériver le projet présenté au solveur sans lui donner le placement ;
3. recertifier le témoin avec le validateur BGIG courant ;
4. engager projet, recette, graine et témoin par digest ;
5. rejeter toute recette dont la vérité ne peut pas être reconstruite.

Les cas impossibles restent des contrôles séparés avec preuve formelle. Un
timeout ou un épuisement heuristique reste `bounded_unknown`.

Les graines et recettes sont déterministes. Le dépôt versionne des manifests,
des générateurs, un échantillon de régression et des rapports compacts, pas des
milliers de gros projets redondants.

## 7. Séparation obligatoire des jeux

La campagne possède au minimum :

- `regression` : cas publics historiques et défauts corrigés ;
- `discovery` : cartographie des échecs et goulets ;
- `tuning` : comparaison des seules hypothèses retenues ;
- `holdout` neuf, fermé et scellé : une seule évaluation du candidat choisi ;
- `soak` déterministe et reprenable : grande campagne hors gate courte.

Le holdout est préenregistré avant toute optimisation, ne fournit aucun témoin
au solveur et n’est jamais utilisé pour régler le code. Après son ouverture,
une nouvelle itération exige un nouveau holdout versionné ou scellé.

## 8. Mesures obligatoires

Par cas et par famille :

- statut final : certifié, impossible prouvé, `bounded_unknown`, non supporté
  ou erreur ;
- temps jusqu’à la première solution certifiée ;
- temps de préparation, projection, lane interne, SCIP, certification,
  finalisation, CAD IR et matérialisation ;
- candidats bruts et uniques, états, essais de pose, complétions, rejets,
  appels solveur et routes réellement utilisées ;
- mémoire de pointe et limites appliquées ;
- digest fonctionnel et résultat déterministe sur replays ;
- motif exact de toute perte après modification.

Les rapports agrègent taux de succès et temps `p50`, `p95` et `p99` par
densité, cardinalité, famille et difficulté. Ils ne masquent jamais une famille
faible derrière une moyenne globale.

## 9. Ordre des missions atomiques

### P64-L09W-A — audit et contrat de mesure

- Reconstituer la couverture actuelle et ses trous.
- Définir le domaine supporté, les strates et les critères préenregistrés.
- Produire une baseline 0.1.80 sur les fixtures déjà versionnées seulement.
- Décider si une ADR est nécessaire avant toute évolution structurante.

### P64-L09W-B — générateur produit et oracles

- Étendre ou adapter les générateurs existants.
- Construire les cas positifs par preuve et les négatifs par borne.
- Couvrir densités, cardinalités, éléments plats et modifications.
- Créer un nouveau holdout sans l’ouvrir.

### P64-L09W-C — campagne de référence

- Exécuter une campagne bornée, reprenable et instrumentée.
- Classer les pertes par cause mesurée.
- Comparer simplicité, robustesse, maintenance, testabilité, gain probable et
  risque fonctionnel.

### P64-L09W-D — optimisations causales

- Un seul changement mesuré, testé, documenté, committé et intégré à la fois.
- Rejouer régression, discovery et tuning après chaque incrément.
- Refuser tout gain qui perd une vérité ou déplace le coût en aval.

### P64-L09W-E — holdout et verdict

- Geler un candidat unique avant ouverture.
- Ouvrir le holdout une seule fois.
- Publier le résultat par strate, y compris les échecs.
- Ne revendiquer que le domaine et les limites réellement démontrés.

### P64-L09W-F — produit et Fusion, si justifié

- Suite complète autorisée et replays produit de bout en bout.
- Nouvelle candidate uniquement si le runtime produit a réellement changé.
- Installation automatique et recette humaine finale.

Chaque mission est intégrée dans `main` avant la suivante. Une campagne longue
reste découpée en checkpoints et peut être reprise sans double exécution.

## 10. Invariants et interdits

- résultat fonctionnel 0.1.80, certificats, cavités, accès, parois et ordre
  conservés ;
- grille produit `0,1 mm` et epsilon `0,0001 mm` distincts et inchangés ;
- aucune nouvelle valeur physique ;
- conteneurs finalisés puis éléments plats strictement soustractifs ;
- aucun budget, timeout ou nombre de candidats augmenté pour maquiller le coût ;
- aucun cache ou témoin périmé, aucun faux impossible, aucun succès non
  certifié ;
- aucun déplacement silencieux du coût vers finalisation ou matérialisation ;
- aucune dépendance lourde ou nouveau moteur sans mesure, ADR et validation ;
- aucun projet personnel promu automatiquement dans un corpus ;
- aucun entraînement statistique opaque ni auto-modification du solveur ;
- aucune revendication T2 à T4 depuis des cas rectangulaires T0/T1.

## 11. Lecture obligatoire de la tâche de reprise

Dans cet ordre :

1. `AGENTS.md`
2. `docs/PILOTAGE_CURRENT.md`
3. `docs/NEXT_ACTIONS.md`
4. `docs/HUMAN_GATES.md`
5. `docs/P64_L09U_R9_V_0180_HUMAN_OK_EVIDENCE.md`
6. `docs/P64_L09W_GENERAL_SOLVER_ROBUSTNESS_HANDOFF.md`
7. `docs/P64_L06B_BENCHMARK_CORPUS_CONTRACT.md`
8. `docs/P64_L06D_PROGRESSIVE_CAMPAIGN_CONTRACT.md`
9. `docs/P64_L08D_REAL_3D_CORPUS_EVIDENCE.md`
10. `docs/P64_L08F_REAL_3D_TOURNAMENT_EVIDENCE.md`
11. ADR-0079, ADR-0081, ADR-0084 et ADR-0106
12. les générateurs, runners, manifests, solveurs, certificats, finalisation,
    matérialisation et tests directement concernés.

Utiliser obligatoirement `$windows-command-resilience` avant tout lot de
commandes, test long ou clôture Git. Tout temporaire reste dans
`<worktree>/.codex-work` puis est supprimé.

## 12. Première action de la tâche neuve

Créer immédiatement un Goal Codex sans budget de tokens inventé, puis exécuter
P64-L09W-A. Le GO autonome est déjà donné : ne pas demander à Thomas de le
répéter et ne pas lui faire rejouer R9-V.

La première sortie attendue est un diagnostic versionné qui dit précisément :

- ce qui existe déjà ;
- ce qui manque pour mesurer les projets demandés ;
- comment le domaine et le futur `95 %` sont définis ;
- quelle baseline 0.1.80 est observée ;
- quelles causes dominantes justifient ou non la première optimisation.
