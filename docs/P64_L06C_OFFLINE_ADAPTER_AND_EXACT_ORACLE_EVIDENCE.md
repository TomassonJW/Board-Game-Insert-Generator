# P64-L06C — preuve des comparateurs offline et du petit oracle exact

## Résultat

L06C livre deux adapters sans dépendance externe, une sortie commune compacte et
un petit oracle exact interne. Toute solution exposée est recertifiée à neuf par
BGIG. Le solveur produit et Fusion restent inchangés.

Statut : `implemented-core`, `automated-validated`.

`fusion-validated: false`. `print-validated: false`.

## Livrables

- `solver_benchmark_adapters.py` : protocole, adapter courant, oracle exact et
  recertification commune ;
- `test_solver_benchmark_adapters.py` : portée, exactitude, refus, caps,
  déterminisme et digest fail-closed ;
- contrat `P64_L06C_OFFLINE_ADAPTER_AND_EXACT_ORACLE_CONTRACT.md`.

## Protocole réellement exposé

Le registre contient exactement deux candidats :

| Candidat | Rôle | Dépendance externe |
| --- | --- | ---: |
| `current_bgig_minimal_layout` | résultat borné du solveur courant | 0 |
| `internal_exact_floor` | référence exacte pour petits cas sur un niveau | 0 |

Le rapport ne contient pas le projet complet. Il conserve seulement les identités,
statuts, limites, compteurs, certificat frais, résumé de solution et digest.

## Preuve de recertification

Le cas historique `simple-quick` est résolu par le solveur courant puis son
candidat est reconstruit depuis les placements. Le certificat minimal commun est
recalculé et accepté. Le même plan recertifié une seconde fois reste accepté.

Une solution rejetée ne pourrait pas apparaître comme solution du benchmark : le
statut deviendrait `certificate_rejected`.

## Preuve du petit oracle exact

Sur les 64 cas discovery, six entrent entièrement dans le périmètre exact déclaré :

- 4 cas faisables par construction ;
- 2 cas impossibles par borne stricte ;
- 6/6 résultats conformes aux vérités indépendantes du corpus ;
- aucune réponse `bounded_unknown` avec les caps par défaut ;
- chaque réponse positive porte un certificat BGIG frais.

Le cas `discovery-e-005` produit un placement certifié sans rotation. Le cas
`discovery-b-002` est prouvé impossible. Une autre preuve fixe est reconnue avant
la préparation produit grâce aux bornes hauteur, empreinte, volume ou aire.

Le rapport répété de `discovery-e-005` est strictement identique, digest compris.
L'oracle de construction du corpus n'est pas consommé par l'adapter ; il sert
uniquement à l'assertion indépendante du test.

## Refus et caps observés

- `discovery-b-007` est refusé explicitement à cause de sa réservation et de sa
  portée hors modèle ;
- un plafond volontaire de 1 état transforme `discovery-e-005` en
  `bounded_unknown` ;
- le solveur courant refuse un cas interdisant la rotation, car ce contrôle
  n'existe pas dans le schéma projet ;
- une modification du projet sans mise à jour du digest est rejetée avant calcul.

Aucune de ces situations n'est présentée comme une impossibilité générale.

## Validation automatisée

- tests ciblés L06C : 9/9 OK ;
- corpus et adapters réunis : 18/18 OK ;
- audit exact discovery dans le test : 6/6 vérités retrouvées ;
- garde documentaire : 2/2 OK ;
- alignement Fusion-only : 6/6 OK ;
- suite complète : 707/707 OK en 184,570 s ;
- Ruff ciblé : OK ;
- `py_compile` ciblé : OK ;
- `git diff --check` : OK avant staging.

## Limites

- l'oracle exact ne couvre ni plusieurs niveaux, ni réservations, ni plusieurs
  variantes locales, ni plus de quatre conteneurs ;
- il prouve la faisabilité du modèle T0 déclaré, pas l'optimalité générale du
  solveur produit ;
- le solveur courant ne peut pas honorer une interdiction de rotation non exposée ;
- les cas incrémentaux exigent un incumbent explicite pour l'adapter courant ;
- aucun résultat de holdout n'est ouvert ;
- aucune nouvelle capacité n'est revendiquée sur le cas dense 11 × 34.

## Suite

P64-L06D peut maintenant exécuter le tournoi progressif : régressions et CI,
puis discovery, au plus trois hypothèses, tuning, choix unique, holdout et soak
seulement si utile.
