# P64-L09R — Contrat de calcul, finition et progression

## 1. Statut et portée

- Statut : `architecture-accepted`, `done-documentation`.
- Date : 2026-07-25.
- Décision : ADR-0088.
- Mission documentaire : P64-L09R-A.
- Prochaine mission unique : P64-L09R-B.

Ce contrat remplace la trajectoire de gate P64-L09V préparée sur l'add-in
0.1.63. Il ne modifie aucun code produit, budget runtime, package Fusion,
tolérance ou valeur physique à lui seul.

## 2. Résultat produit attendu

Le parcours doit permettre de :

1. calculer un placement minimal 3D certifié, plateaux et livrets compris ;
2. matérialiser immédiatement ce plan minimal si l'utilisateur le souhaite ;
3. lancer séparément une finition facultative qui remplit proprement le volume
   restant ;
4. matérialiser le plan final si cette finition réussit ;
5. voir le budget choisi et une activité visible sans croire que la palette est
   plantée.

Le plan minimal est la base sûre. La finition l'améliore sans devenir une
condition de son existence.

## 3. Contrat du calcul minimal

Entrées :

- projet normalisé courant ;
- variantes locales P45 déjà certifiées ;
- dimensions utiles de boîte ;
- jeux et épaisseurs applicables ;
- réservations supérieures représentables ;
- méthode de calcul et niveau de budget.

Sortie positive :

- un `minimal_layout` courant et recertifié ;
- chaque conteneur à sa taille minimale admissible ;
- compensation Z strictement nécessaire aux réservations ;
- cavités d'assets, fonds, parois, jeux, collisions, support par enveloppe et
  retrait préservés ;
- provenance, moteur, budget, temps et raison d'arrêt.

Sortie négative :

- `no_solution_within_budget`, `unsupported` ou `invalid` honnête ;
- aucun plan partiel matérialisable ;
- aucune preuve d'impossibilité déduite d'un simple timeout.

## 4. Support et préférence de placement

Le certificat dur emploie l'enveloppe extérieure XY comme support. La matière
des rebords peut rester calculée pour diagnostic, mais ne bloque pas un plan.

La recherche préfère les petites empreintes sous les grandes :

1. aire XY extérieure croissante pour construire la base ;
2. plus petit côté croissant ;
3. volume croissant ;
4. identité stable pour départage.

Cette préférence peut alimenter l'ordre d'entrée, le warm start, les priorités
SCIP et un score secondaire. Elle ne peut :

- rendre une solution impossible ;
- empêcher la publication du premier incumbent certifié ;
- consommer tout le budget pour une simple amélioration d'ordre ;
- remplacer les certificats de collision, support, boîte ou retrait.

Fixtures minimales :

- plan préféré avec deux petits conteneurs sous un grand ;
- inversion encore acceptée quand elle est nécessaire ;
- empilement au-dessus d'un conteneur ouvert accepté par enveloppe ;
- ordre déterministe à géométrie égale ;
- plan au sol inchangé.

## 5. Budgets du calcul

| Identifiant | Libellé UI | Deadline totale |
| --- | --- | ---: |
| `quick` | Rapide | 3 s |
| `short` | Court | 10 s |
| `normal` | Normal | 20 s |
| `long` | Long | 60 s |
| `deep` | Approfondi | 180 s |

La deadline couvre l'ensemble du calcul : préparation, SCIP, éventuel
remplissage certifié, voies de repli autorisées et certification finale.
Chaque composant reçoit uniquement le temps restant.

Un ancien projet conserve une migration déterministe vers un niveau nommé. Le
default produit sera confirmé dans P64-L09R-B à partir du comportement actuel ;
aucun ancien budget caché ne doit survivre en parallèle.

## 6. Contrat de la finition

La finition reçoit :

- le `minimal_layout` courant ;
- les réservations et cavités exactes ;
- les faces Auto/Cible/Fixe ;
- un niveau de budget indépendant ;
- les politiques d'équilibrage admissibles.

Elle peut :

- répartir le volume résiduel entre les conteneurs demandés ;
- augmenter les dimensions extérieures dans leurs bounds ;
- compenser la profondeur des plateaux par Z ;
- réparer localement les placements ou hauteurs affectés ;
- rappeler le placement global seulement après échec local et avec le temps
  restant.

Elle ne peut jamais :

- réduire ou déplacer une cavité d'asset ;
- percer un fond ou une paroi minimale ;
- créer silencieusement un corps, une cale ou un micro-conteneur ;
- invalider le plan minimal après un échec ;
- publier un plan final non recertifié.

La finition utilise initialement les mêmes cinq niveaux temporels que le calcul,
mais son choix et sa deadline sont indépendants.

## 7. États et actions

Les trois boutons sont toujours rendus :

| État courant | Calculer | Finaliser | Matérialiser |
| --- | --- | --- | --- |
| Projet neuf ou source modifiée | actif | grisé | grisé |
| Calcul minimal courant | grisé | actif | actif sur le plan minimal |
| Finition en cours | grisé | grisé | grisé |
| Plan final courant | grisé | actif pour recalcul explicite | actif sur le plan final |
| Calcul en cours | grisé | grisé | grisé |
| Matérialisation en cours | grisé | grisé | grisé |

Une nouvelle modification pertinente réactive `Calculer`. Le réglage du budget
de calcul est pertinent pour le calcul. Le seul réglage de finition invalide le
plan final, mais conserve le plan minimal et sa matérialisabilité.

Le target de matérialisation est explicite dans l'état :

- `minimal_layout` si aucun plan final courant n'existe ;
- `finalized_plan` après une finition courante réussie.

## 8. Réglages visibles

Dans l'onglet Réglages :

- le niveau du calcul est sélectionnable ;
- un petit champ adjacent et non éditable affiche `3 s max`, `10 s max`,
  `20 s max`, `60 s max` ou `3 min max` ;
- juste en dessous, le niveau de finition est sélectionnable séparément ;
- son champ adjacent affiche son propre budget réel ;
- les deux valeurs persistent avec les réglages locaux selon le contrat
  existant, sans devenir des valeurs physiques du projet.

Le libellé ne doit jamais afficher seulement `Rapide`, `Normal` ou
`Approfondi` sans la limite réelle correspondante.

## 9. Jauge d'activité

La zone d'activité est placée immédiatement au-dessus des boutons et prend toute
la largeur disponible.

Règle dure d'affichage :

- opération active : zone visible ;
- aucune opération active : zone non rendue ou `display:none`, sans espace
  réservé et sans dernier état terminal.

Pour le calcul et la finition :

- rafraîchissement cible : une fois par seconde ;
- progression visuelle : temps écoulé / budget total ;
- texte : opération, étape connue, temps écoulé, budget ;
- fin anticipée : disparition immédiate de la jauge après publication du
  résultat normal ;
- deadline atteinte : résultat honnête, puis disparition.

Pour la matérialisation :

- jauge indéterminée par défaut ;
- étapes CAD réelles admises si elles sont observables ;
- aucun pourcentage ou délai inventé.

## 10. Réactivité et exécution sûre

Le cœur du calcul et le cœur de la finition restent purs et testables hors
Fusion. Ils peuvent être exécutés dans un worker qui ne charge jamais `adsk`.

Le thread Fusion :

- déclenche l'opération ;
- reçoit les événements d'activité sûrs ;
- met à jour la palette ;
- compare les digests au retour ;
- rejette un résultat stale ;
- exécute la matérialisation CAD sur le thread autorisé.

Un heartbeat UI ne constitue pas un appel métier supplémentaire et ne doit pas
relancer le solveur.

## 11. Invalidation minimale

| Modification | Plan minimal | Plan final | Scène |
| --- | --- | --- | --- |
| Source, géométrie, cavité, réservation | stale | stale | stale |
| Méthode ou budget du calcul | stale | stale | stale |
| Politique ou budget de finition | courant | stale | scène minimale encore comparable |
| Préférence d'affichage seule | courant | courant | inchangée |
| Finition échouée | courant | absent/stale | plan minimal matérialisable |

Tout résultat asynchrone est rejeté si le digest d'entrée a changé.

## 12. Validation automatisée requise

Avant la gate Fusion :

- budgets 3/10/20/60/180 transmis comme deadline globale ;
- monotonie du préfixe de recherche ou justification documentée ;
- préférence petits-dessous sans perte de faisabilité ;
- plateaux réellement transmis à SCIP ;
- plan minimal avec plateau matérialisable ;
- finition indépendante et échec non destructif ;
- trois boutons toujours présents et états exacts ;
- champs de budget adjacents exacts ;
- jauge absente du layout hors opération ;
- rafraîchissement temporel sans second solve ;
- résultat stale rejeté ;
- aucun import `adsk` dans le cœur ou le worker ;
- suite complète, contrôles documentaires et `git diff --check`.

Les cas représentatifs doivent inclure le cas public 28x30, un cas avec plateau,
un empilement au-dessus d'une ouverture et des cas négatifs de collision ou de
réservation. Un holdout consommé n'est jamais rouvert pour régler cette
trajectoire.

## 13. Découpage des missions

### P64-L09R-A — décision et pilotage

- ADR-0088, présent contrat, backlog, roadmap, capabilities et gates.
- Statut après intégration : `done-documentation`.

### P64-L09R-B — calcul minimal fiable

- rétablir le support dur par enveloppe ;
- retirer l'anti-chute de la faisabilité produit ;
- ajouter la préférence souple petits-dessous/grands-dessus ;
- appliquer les budgets 3/10/20/60/180 comme deadlines totales ;
- conserver les réservations SCIP et rendre le plan minimal avec plateau
  matérialisable.

### P64-L09R-C — finition séparée et non destructive

- découpler F01B/F02B du calcul minimal ;
- conserver le plan minimal courant en cas d'échec ;
- ajouter le réglage et le budget de finition indépendants ;
- borner expansion, réparations locales et éventuel rappel global ;
- publier uniquement un `finalized_plan` recertifié.

### P64-L09R-D — cycle d'interface explicite

- rendre les trois boutons permanents ;
- appliquer les états d'activation et l'invalidation ;
- afficher les deux sélecteurs et leurs champs de budget adjacents ;
- montrer clairement le plan ciblé par la matérialisation.

### P64-L09R-E — progression et réactivité

- jauge pleine largeur visible uniquement pendant une opération ;
- rafraîchissement proche d'une seconde ;
- calcul et finition hors thread UI sans `adsk` ;
- matérialisation sur le thread Fusion avec phases honnêtes ;
- stale et doubles lancements fail-closed.

### P64-L09R-F — durcissement représentatif

- tests de cas limites et de projets avec plateau ;
- mesure séparée calcul/finition ;
- vérification des budgets et fins anticipées ;
- correction des régressions dans le scope, sans recalibrage physique ;
- préparation du dossier de gate seulement si les preuves passent.

### P64-L09R-V — gate Fusion combinée

- package installé depuis le commit intégré ;
- calcul sous plusieurs budgets, plateau inclus ;
- préférence d'empilement observée sans la traiter comme certificat ;
- matérialisation minimale sans finition ;
- finition séparée puis matérialisation finale ;
- jauge visible pendant l'activité et totalement absente au repos ;
- aucune promotion d'impression.

## 14. Dépendances et ordre

```text
P64-L09R-A
  -> P64-L09R-B
  -> P64-L09R-C
  -> P64-L09R-D
  -> P64-L09R-E
  -> P64-L09R-F
  -> P64-L09R-V
```

Une seule mission est active à la fois. P45, P46, la modularité, les capacités
post-solve C01-C03 et les horizons P70+ ne sont pas absorbés dans ce programme.

## 15. Hors scope absolu

- nouvelles formes P45 ;
- nouvelle sémantique de couvercle ou pose de conteneur fermé ;
- changement de tolérance ou valeur physique ;
- création automatique de cales ou de conteneurs ;
- réouverture d'un holdout consommé ;
- dépendance ou service externe supplémentaire ;
- logique métier JavaScript ou `adsk` dans le cœur ;
- validation d'impression.
