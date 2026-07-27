# P64-L09S — Runbook du Goal de stabilisation de bout en bout

<!-- P64-L09T-SUPERSESSION -->
## Statut historique apres 0.1.69

P64-L09S-A a F restent des preuves historiques. La gate 0.1.69 est desormais
`human-KO`, `do-not-run`. Le programme actif est P64-L09T, defini par ADR-0093
et `docs/P64_L09T_END_TO_END_GOAL_RUNBOOK.md`.

<!-- P64-L09S-F -->
## Point de passage P64-L09S-F

F est automatisee-validee avec le package 0.1.67. Le preflight reproduit les dimensions critiques, prouve l'absence de croissance liee au plateau et traverse minimal, finalisation, CAD IR et plan Fusion. Apres installation du commit integre, la boucle autonome s'arrete obligatoirement a V.


<!-- P64-L09S-E -->
## Point de passage P64-L09S-E

E est acquise : la proposition D devient un plan final seulement apres trois preuves concordantes. Le CAD IR conserve un composant utilisateur par proprietaire, cree le coeur, unit les annexes par vraies faces X/Y, puis applique les cavites et les coupes plateau/livret exactes. Le squelette Fusion refuse toute attache composite invalide et transporte le repere global sans recalcul.


<!-- P64-L09S-D -->
## Point de passage P64-L09S-D

D est acquise : apres l'echec honnete de C, le repli construit une partition brute complete, soustrait exactement les reservations hautes ouvertes et certifie des corps logiques composites de meme base Z. Toute annexe possede un proprietaire unique et une chaine de vraies faces verticales X/Y ; les liaisons Z seules, par arete ou par point sont refusees. La proposition reste non publiable jusqu'a E.


## Avancement apres P64-L09S-C

- A, B et C terminees.
- Fermeture globale BSP 3D complete par construction.
- Equilibre et proportion compares uniquement entre partitions completes.
- Zero residuel imprimable avant publication.
- Cas non tranchable dirige vers D sans plan partiel.

## Avancement apres P64-L09S-B

- A et B terminees.
- Aucun faux `finalized_plan_ready` sans certificat final courant.
- Interface : calcul bleu, finition orange, materialisation verte.
- Budgets visibles et reactifs conserves.
- Prochaine mission : C, fermeture rectangulaire globale.

## Avancement execution au 2026-07-25

- Goal lance et ADR-0089 acceptee.
- A terminee : aucune reservation ne fabrique un porteur.
- Cas recent : corps 23,2 x 23,2 x 31,6 mm a Z 21,2 ; sommet 52,8 ; plan sous plateau 58,6 ; gap 5,8 mm.
- Prochaine mission : B.
- Aucun benchmark, holdout ou package Fusion installe.

## 1. Rôle et statut

- Statut : `ready-for-user-goal-launch`, `done-documentation`.
- Décision proposée : ADR-0089.
- Entrée : KO humain P64-L09R-V sur 0.1.65.
- Goal : non créé et non lancé par la mission de préparation.
- Déclencheur unique : lancement explicite du Goal par Thomas dans le
  clavardage de reprise.

Ce runbook transforme le retour Fusion réel en un programme borné. Avant ce
déclencheur, le successeur reste en lecture seule : aucun code, benchmark,
package Fusion, installation ou mutation de projet.

## 2. Objectif exact du Goal

> Rendre impeccable le parcours BGIG complexe de bout en bout — calcul minimal
> sans déformation liée aux plateaux, finalisation complète et équilibrée de tout
> le volume imprimable, annexes XY soudées bornées si nécessaire,
> matérialisation fidèle, UX honnête et gate Fusion finale.

Le résultat visé est :

```text
cas complexe
  -> plan minimal 3D certifié, sans support artificiel
  -> finalisation globale complète et équilibrée
  -> corps composites XY seulement si nécessaire
  -> CAD IR fidèle et unions Fusion
  -> observation humaine finale
```

## 3. Préflight bloquant après lancement

Avant la première modification :

1. lire `AGENTS.md`, `PILOTAGE_CURRENT.md`, `NEXT_ACTIONS.md` et
   `HUMAN_GATES.md` ;
2. lire ADR-0089, ce runbook et la preuve KO 0.1.65 ;
3. vérifier `git status --short --branch`, `HEAD`, `origin/main`,
   `HEAD...origin/main` et les worktrees ;
4. préserver tous les worktrees étrangers, notamment celui qui possède
   localement `main` ;
5. vérifier qu'aucun autre Goal BGIG n'est actif ;
6. créer une branche `codex/` depuis `origin/main` pour la mission atomique ;
7. relire uniquement le code directement concerné par la mission en cours.

Un écart Git, un travail étranger menacé ou une divergence non triviale bloque
la mutation. Un simple timeout de solve ne bloque pas le programme et ne vaut
jamais impossibilité.

## 4. Règles d'exécution

- Une seule mission P64-L09S est active à la fois.
- Chaque mission est testée, documentée, committée, intégrée dans `main` puis
  poussée avant la suivante.
- Aucun nouveau GO n'est demandé entre A et F après lancement du Goal.
- Les budgets publics restent 3/10/20/60/180 s.
- Aucun benchmark, tournoi ou holdout consommé n'est exécuté.
- Aucun package Fusion n'est installé avant la préparation de V.
- Aucun secret, snapshot personnel ou witness local n'entre dans le dépôt.
- Aucun changement de tolérance, jeu, épaisseur physique ou couvercle.
- Aucun `adsk` dans le cœur ou le worker.
- Tout échec conserve le dernier plan minimal certifié.

## 5. Invariants communs

### Calcul minimal

- dimensions extérieures égales aux minima certifiés ;
- aucun agrandissement de support en X, Y ou Z ;
- réservations exactes, sans intersection ;
- gap sous plateau autorisé ;
- timeout honnête et plan partiel non publié.

### Finition

- chaque cellule imprimable finale appartient exactement une fois à un
  conteneur ;
- seuls les vides techniques explicitement certifiés restent libres ;
- aucun chevauchement, corps implicite ou cale silencieuse ;
- cavités, axes Fixe, prises, jeux et retrait préservés ;
- résultat complet et recertifié avant publication ;
- minimal conservé bit à bit en cas d'échec.

### Composite

- annexe attachée par face verticale X/Y réelle ;
- bas Z concomitant ;
- corps final connexe et uni ;
- aucune liaison uniquement Z, arête ou point ;
- un propriétaire unique et déterministe ;
- complexité et nombre d'annexes minimisés.

### UI et matérialisation

- succès de finition seulement avec `finalized_plan` courant ;
- message et stop reason fidèles au résultat ;
- trois boutons toujours visibles et colorés ;
- CAD IR, certificat, artefact et scène portent la même identité ;
- union Fusion et coupes sur le thread autorisé.

## 6. P64-L09S-A — minimal sans support artificiel

Objectif : retirer la compensation Z de plateau du calcul minimal.

Travail :

- supprimer le chemin qui choisit et allonge un conteneur porteur ;
- retirer l'obligation de support du worker SCIP ;
- conserver l'épaisseur, l'empreinte et l'ordre des réservations ;
- post-certifier le premier incumbent ;
- si nécessaire, relancer sous le temps restant avec les prismes réservés
  interdits ;
- garder le correctif du rafraîchissement des budgets.

Preuves minimales :

- cas 60 / 59,6 / 52,8 mm avec plateau 1 mm : aucun conteneur agrandi ;
- plan minimal avec et sans plateau : mêmes dimensions de conteneurs lorsque le
  placement reste compatible ;
- réservation localisée intersectée : retry borné ou timeout inconnu ;
- aucune encoche créée dans le plan minimal ;
- plan minimal matérialisable sans finition.

Sortie : `implemented-product`, `automated-validated`, puis intégration.

## 7. P64-L09S-B — vérité du cycle et couleurs

Objectif : rendre le résultat métier et les actions immédiatement lisibles.

Travail :

- dériver le stop reason de la vraie sortie de finition ;
- supprimer `Projet accepté` pour un échec ou une absence de plan final ;
- distinguer succès, timeout, résiduel, certificat rejeté et stale ;
- conserver les cinq budgets de calcul et finition réactifs ;
- appliquer bleu à Calculer, orange ou violet à Finaliser et vert à
  Matérialiser ;
- garder un état désactivé accessible et visible.

Preuves minimales :

- finalisation échouée : aucun message ni événement de succès ;
- finalisation réussie : plan final et identités présents ;
- changement de chaque budget : niveau et durée adjacente synchrones ;
- couleurs de base et états désactivés couverts par tests DOM.

## 8. P64-L09S-C — fermeture rectangulaire globale

Objectif : remplacer la croissance gloutonne comme autorité par une partition
globale complète.

Travail :

- construire la décomposition orthogonale depuis le plan minimal ;
- énumérer des enveloppes finales rectangulaires admissibles ;
- sélectionner une enveloppe par conteneur avec SCIP ou une recherche exacte
  interne bornée ;
- imposer une couverture exacte du volume imprimable ;
- optimiser équilibre absolu, équilibre relatif et déformation ;
- conserver le résultat déterministe sous deadline.

Le principe historique de P57 est réutilisé comme oracle conceptuel et comme
fixture simple, pas comme solveur global.

Preuves minimales :

- anciennes partitions simples : fermeture complète retrouvée ;
- plan multi-étages : fermeture complète sans déplacer le minimal ;
- contraintes asymétriques Auto/Cible/Fixe ;
- égalité de faisabilité avec des répartitions concurrentes et choix plus
  équilibré ;
- timeout : minimal conservé et aucune fausse fermeture.

## 9. P64-L09S-D — annexes XY composites bornées

Objectif : fermer les résiduels non rectangulaires sans créer de corps visible
supplémentaire.

Travail :

- produire des cellules d'annexe depuis la même décomposition ;
- les attribuer à un propriétaire adjacent admissible ;
- certifier contact par face verticale, bas Z et connexité ;
- minimiser nombre, faces et volume des annexes ;
- étendre le certificat de plan final et son digest ;
- refuser tout résiduel sans propriétaire valide.

Preuves minimales :

- cas en L nécessitant exactement une annexe ;
- deux propriétaires possibles : choix déterministe et équilibré ;
- contact par arête, point ou face Z seule rejeté ;
- annexe qui toucherait une cavité/réservation rejetée ;
- corps final unique après union abstraite.

Le lancement du Goal vaut acceptation humaine de ce périmètre composite borné.

## 10. P64-L09S-E — CAD IR, unions et encoches exactes

Objectif : matérialiser exactement le plan final rectangulaire ou composite.

Travail :

- représenter corps principal, annexes et unions dans le CAD IR ;
- unir avant les coupes dépendantes de la forme finale ;
- créer les encoches uniquement sur les corps qui atteignent et chevauchent un
  plateau/livret ;
- respecter épaisseur et ordre de plusieurs réservations ;
- préserver la scène précédente si une union ou une coupe échoue ;
- maintenir la matérialisation minimale sans annexe ni encoche artificielle.

Preuves minimales :

- un composant utilisateur par conteneur final ;
- volumes et bounds du certificat égaux au CAD IR ;
- plateau de 1 mm : coupe seulement sur les corps finaux concernés ;
- plusieurs plateaux/livrets : ordre et profondeurs exacts ;
- échec d'union : aucune scène partielle publiée.

## 11. P64-L09S-F — durcissement de bout en bout

Objectif : prouver le parcours complet avant Fusion.

Corpus :

- fixture publique simple héritée de P57 ;
- fixture publique multi-étages ;
- fixture plateau sans croissance minimale ;
- fixture nécessitant une annexe XY ;
- cas public 28x30 ;
- régression anonymisée reproduisant les mécanismes du cas humain récent, sans
  donnée personnelle.

Parcours obligatoires :

1. calcul minimal ;
2. matérialisation minimale ;
3. finition rectangulaire ou composite ;
4. matérialisation finale ;
5. échec et timeout à chaque frontière ;
6. stale après mutation ;
7. relecture des digests et du certificat de couverture.

F ne lance aucun benchmark et n'installe rien dans Fusion. Il prépare seulement
le package, les fixtures, le préflight et la recette de P64-L09S-V si toutes les
preuves passent.

## 12. P64-L09S-V — gate Fusion humaine

Codex :

- installe le commit intégré exact ;
- vérifie version, runtime, marqueurs, fixtures et réglages ;
- fournit seulement les manipulations Fusion restantes.

Thomas observe :

- budgets immédiatement réactifs ;
- trois boutons colorés et états honnêtes ;
- cas complexe avec plateau sans conteneur allongé au calcul ;
- matérialisation minimale fidèle ;
- finition complète, équilibrée et sans vide imprimable ;
- éventuelle annexe fondue dans son conteneur ;
- encoches uniquement sur les corps finaux concernés ;
- matérialisation finale fidèle ;
- message d'échec honnête sur un cas négatif.

Cette gate ne valide ni impression, ni tolérance, ni résistance mécanique.

## 13. Certificat final obligatoire

Le certificat de finition doit au minimum porter :

- digest du plan minimal source ;
- domaine imprimable et vides techniques exclus ;
- décomposition de cellules et version ;
- propriétaire de chaque cellule ;
- enveloppe principale et annexes par conteneur ;
- contacts, connexité et unions ;
- réservations et coupes associées ;
- volume ajouté absolu et relatif ;
- résiduel imprimable final, obligatoirement nul pour un succès ;
- méthode, budget, temps, stop reason et déterminisme ;
- digest du plan final et du CAD IR attendu.

## 14. Arrêts honnêtes

Le Goal peut s'arrêter seulement pour :

- conflit Git réel ou risque pour un travail étranger ;
- test non réparable dans la mission atomique ;
- ambiguïté non résolue par ADR-0089 ;
- extension du modèle composite, des tolérances ou des mécanismes ;
- impossibilité d'obtenir une preuve automatisée fidèle ;
- gate humaine P64-L09S-V.

Un résultat algorithmique négatif documenté est une sortie valide de mission,
mais le Goal n'est complet que lorsque le parcours positif demandé existe de
bout en bout.

## 15. Clôture Git de chaque mission

Ordre obligatoire :

```text
status
-> tests ciblés
-> suite pertinente puis complète
-> git diff --check
-> revue du diff
-> commit atomique
-> fetch origin --prune
-> vérification de origin/main
-> intégration directe non conflictuelle dans main
-> push
-> vérification du SHA distant
-> nettoyage de la branche devenue inutile
```

Le worktree étranger qui possède la branche locale `main` n'est jamais modifié.
Un push fast-forward `HEAD:main` depuis la branche de mission est autorisé après
vérification exacte.

## 16. Prompt `/goal` canonique

Thomas lance lui-même le Goal avec l'objectif suivant :

```text
Exécute le Goal P64-L09S décrit par
docs/P64_L09S_END_TO_END_GOAL_RUNBOOK.md.

Objectif : rendre impeccable le parcours complexe de bout en bout : calcul
minimal sans déformation liée aux plateaux, finalisation complète et équilibrée
de tout le volume imprimable, annexes XY soudées bornées si nécessaire,
matérialisation fidèle, UX honnête et gate Fusion finale.

Accepte ADR-0089 par ce lancement. Travaille une mission à la fois, A à F, avec
tests, documentation, commit et intégration directe dans main après chaque lot.
Ne redemande aucun GO entre A et F. Préserve tous les worktrees étrangers.
N'exécute aucun benchmark ni holdout et n'installe Fusion qu'en préparation de
la gate V. Arrête-toi à P64-L09S-V pour mon observation humaine.
```

## 17. Modèle conseillé

- Optimal : `gpt-5.6-sol`, raisonnement `xhigh`, en raison du couplage solveur,
  certificat, géométrie composite, CAD IR, Fusion et preuves longues.
- Option économique : `gpt-5.6-terra`, raisonnement `high`, acceptable pour un
  lot documentaire ou UI isolé, mais déconseillée pour C à E où une erreur de
  modèle coûterait probablement une reprise complète.

<!-- P64-L09S-0167-RUNBOOK -->
## Reprise corrective apres le KO humain de 0.1.66

Le package `0.1.66` est `human-KO` et `do-not-run`. La reprise `0.1.67` protege le minimum canonique par axe et applique la sequence suivante :

1. construction minimale dense au sol quand une partition guillotine certifiee existe ;
2. solveur 3D SCIP pour la faisabilite complexe lorsque ce chemin rapide ne suffit pas ;
3. fermeture rectangulaire globale ;
4. croissance continue d'abord vers `+Z`, bornee par les reservations superieures ;
5. extensions XY composites bornees si le residuel persiste ;
6. post-certification complete avant publication et materialisation.

Une variante interne peut reorganiser ses cavites, mais ne peut reduire aucune dimension de l'enveloppe minimale canonique source. Si une reutilisation incrementale ne respecte plus ce contrat, elle doit demander un calcul global explicite.

<!-- P64-L09S-0167-PREPARED -->
## Preparation Fusion 0.1.67 confirmee

- statut : `prepared-not-human-observed` ;
- commit installe : `832c9d5` ;
- preflight : `85c578d051b83fcd71b6b3c6eeaed7601748b1b95e5e942377faf9f52ef3e528` ;
- package/manifeste/reglages/marqueur : verifies ;
- cas humain obligatoire : projet recent a 28 conteneurs, avec controle du minimum `76 x 76 x 31.8 mm` ;
- `fusion-validated=false` et `print-validated=false` jusqu'au verdict humain.

<!-- P64-L09S-0169-RUNBOOK -->
## Reprise corrective apres le KO humain de 0.1.68

Le package `0.1.68` est `human-KO` et `do-not-run`. Le candidat `0.1.69`
applique la sequence suivante :

1. construire uniquement les enveloppes minimales canoniques ;
2. traiter plateau et livret comme des prismes virtuels superieurs interdits ;
3. pour les grands cas reserves, construire des piles legales puis ranger leurs
   bases sur le fond sous une borne de 1024 etats ;
4. recertifier le plan minimal avec le certificat BGIG commun ;
5. fermer globalement depuis ce plan minimal original ;
6. utiliser les annexes XY bornees seulement si la fermeture continue ne suffit
   pas ;
7. unir les corps finaux, puis appliquer uniquement les coupes de reservation
   qui les concernent ;
8. publier un succes seulement avec un `finalized_plan` courant, recertifie et
   un residuel nul.

La progression reste locale dans la palette et recoit un seul evenement de fin
du worker. Le budget choisi reste stable ; la deadline globale ne modifie pas
son identite.

Automatisation : `910/910`, `CasLimite01/02` verts, un test SCIP natif ignore
sous Python 3.10. Frontiere suivante : gate Fusion humaine `0.1.69`.
`fusion-validated=false`, `print-validated=false`.
