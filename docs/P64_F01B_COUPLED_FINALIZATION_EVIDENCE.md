# P64-F01B — fermeture couplée bornée et réparation locale

Date : 2026-07-24
Statut : implemented-product, automated-validated, fusion-validated=false,
print-validated=false.

## Résultat

Le plan minimal certifié devient l’incumbent de la finalisation. La fermeture
introduit les réservations supérieures avant toute expansion, distribue le
volume résiduel uniquement sur les axes Auto/Target, puis tente une réparation
locale déterministe si aucune croissance directe ne progresse. Itérations,
candidats, réparations et temps partagent un budget borné par profil.

Le plan fermé repasse ensuite dans le certificat produit commun : géométrie,
jeux, support matériel, cavités, fonds, réservations, retrait et conservation du
volume. La CAD IR ne peut sélectionner ce plan qu’après ce certificat final.

## Chaîne de vérité

1. le placement minimal certifié est reconstruit sans ajouter de corps ;
2. les variantes internes sélectionnées restituent leurs cavités exactes ;
3. la croissance ne modifie aucun axe Fixe ;
4. chaque proposition est revalidée contre la boîte, les collisions, les jeux,
   les réservations et le support matériel ;
5. une réparation locale déplace un seul corps vers une face de boîte ou une
   face voisine, puis exige une croissance qui réduit strictement le résiduel ;
6. la boucle s’arrête sur fermeture, stagnation, nombre d’itérations, nombre de
   candidats, nombre de réparations ou deadline ;
7. le certificat global reconstruit les parois, fonds, cavités et encastrements ;
8. seul l’artefact finalized_plan certifié est publiable quand une réservation
   active exige la finalisation.

## Échec borné

Une fermeture qui ne peut pas absorber le résiduel rend
no_solution_within_budget. Elle conserve l’incumbent, publie
partial_plan_published=false, garde materializable=false et ne matérialise rien.
Aucun rappel global n’a été nécessaire dans les cas admis ;
global_resolve_invocation_count=0 est enregistré explicitement.

## Orchestration et palette Fusion

- finalize_volume() utilise le moteur borné par défaut ;
- un projet sans réservation conserve la matérialisation minimale optionnelle ;
- un projet avec plateau/livret bloque la sélection du plan minimal et demande
  finalize_volume ;
- la palette enchaîne calcul minimal, finalisation, puis matérialisation ou
  régénération de l’artefact final exact ;
- l’identité de scène accepte désormais minimal_layout ou finalized_plan selon
  l’artefact réellement publiable ;
- un incumbent réservé n’est ni stocké comme witness publiable, ni exposé par
  current_minimal_partition().

## Preuves automatisées

- fermeture continue : 3/3, dont une réparation locale réellement appliquée ;
- orchestration staged : 14/14, dont réservation active, blocage du minimal,
  plan final certifié et provenance de l’incumbent ;
- pont palette/projet : 29/29, dont finalisation puis CAD IR finale et échec
  borné sans plan partiel ;
- contrat DOM palette : 39/39, dont routage finalize_project et identité
  finalized_plan ;
- suite complète : 851/851 en 233,473 s, avec 1 test natif CPython 3.14 ignoré
  sous Python 3.10 ;
- formatage Ruff et contrôles ciblés : OK.

Aucun benchmark, tuning, holdout, runtime natif, tolérance, valeur physique,
nouvelle pose ou sémantique de couvercle n’a été ajouté.

## Limites conservées

- la réparation locale actuelle explore des alignements de boîte et de voisins ;
- aucun second placement global n’est relancé dans ce lot : si la réparation
  locale échoue, le résultat reste borné et non matérialisable ;
- les enveloppes de mécanismes futurs restent à zéro tant qu’un certificat de
  fermeture distinct n’existe pas ;
- les objectifs équilibré et proportionnel appartiennent à la partie admissible
  de P64-F02B ; l’harmonisation modulaire reste différée ;
- aucune observation Fusion L09V ni impression réelle n’est revendiquée.
