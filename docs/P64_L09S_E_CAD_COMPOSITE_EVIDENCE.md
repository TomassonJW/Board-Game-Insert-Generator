# Preuve P64-L09S-E - CAD IR composite, unions et encoches exactes

- mission: P64-L09S-E
- status: implemented-and-tested
- date: 2026-07-25
- resultat: finalized_plan composite courant, recertifie et materialisable
- fusion-observed=false
- print-validated=false

## Recertification produit

Le repli composite D n'est plus une simple proposition. E recertifie d'abord la partition brute avec les intersections exactes des reservations hautes, puis combine ce certificat produit avec le certificat volumique composite D et un certificat de traduction CAD.

Le certificat final impose notamment :

- `one_user_component_per_owner=true` ;
- `joins_precede_cuts=true` ;
- `printable_residual_volume_mm3=0` ;
- volume brut CAD egal au volume brut certifie ;
- volume final egal au volume imprimable hors reservations et vides techniques de prise certifies ;
- aucun plan final publie si l'un des certificats est invalide.

## CAD IR et Fusion

Chaque proprietaire composite devient exactement un composant utilisateur :

1. creation du prisme coeur ;
2. union topologique de chaque annexe par `join_rectangular_prism` ;
3. soustraction des cavites de contenu ;
4. soustraction des encoches plateau/livret exactes.

Les coupes sont derivees uniquement des corps finaux qui atteignent le plan haut et chevauchent l'empreinte demandee. Le repere geometrique global permet une coupe situee sur une annexe hors du coeur, tout en conservant les operations Fusion locales au composant.

Le squelette Fusion refuse une annexe avec parent non resolu, Z bas different, contact Z seul, contact par arete ou point, ou axe X/Y mensonger. Le moteur Fusion existant execute deja toutes les unions avant les coupes.

## Cas plateau recent

Le cas limite recent passe maintenant de la proposition D a un `finalized_plan` courant :

- un seul conteneur logique et un seul composant utilisateur ;
- au moins une annexe unie ;
- encoches plateau et prise transportees comme coupes non perforantes ;
- artefact final selectionnable et CAD IR `ready_for_fusion` ;
- plan Fusion pur construit sans recalcul metier ;
- residuel imprimable nul.

## Preuves automatisees

- cycle etage complet du cas plateau : 19/19 ;
- CAD IR historique et composite : 14/14 ;
- squelette Fusion : 90/90 ;
- palette projet : 29/29 ;
- garde positive et refus composites : 2/2 ;
- authorized_suite: 820/820 ;
- tests benchmark/holdout/tournament/corpus exclus : 72 ;
- test SCIP natif ignore sous Python 3.10 : 1.

Aucun benchmark ni holdout n'a ete lance. Aucun package Fusion n'a ete installe pendant E. La generation reste a observer pendant la gate humaine V.
