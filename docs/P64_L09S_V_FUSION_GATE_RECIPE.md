# P64-L09S-V - recette de gate Fusion humaine 0.1.67

## Statut

- Gate : obligatoire, humaine, non encore observee.
- Package : `0.1.67`.
- Preparateur canonique : `scripts/fusion/prepare_p64_l09sv_gate.ps1`.
- Ancienne gate 0.1.65 : `human-KO`, `do-not-run`.
- Benchmark/holdout : interdits.
- Impression : `print-validated=false`.

Codex installe le package, la fixture et les reglages avant de demander une action a Thomas. Thomas ne lance aucune commande PowerShell.

## Fixture preparee

`p64-l09sv-01-recent-tray-composite.bgig.json`

Elle reproduit les dimensions structurantes du defaut recent :

- boite 200 x 150 x 60 mm ;
- hauteur utile 59,6 mm ;
- plateau 100 x 80 x 1 mm ;
- enveloppe minimale du conteneur 23,2 x 23,2 x 31,6 mm ;
- aucune compensation Z liee au plateau ;
- fermeture finale composite avec annexes XY et encoches exactes.

Le recu local `p64-l09sv-preflight-summary.json` contient aussi le contrat exact observe a Z=21,2 : sommet 52,8, plan du plateau 58,6, gap 5,8, croissance artificielle 0.

## Actions restantes dans Fusion

1. Recharge completement BGIG 0.1.67 et ouvre Atelier de rangement.
2. Verifie les couleurs : Calculer bleu, Finaliser orange, Materialiser vert ; les etats desactives doivent rester explicites.
3. Ouvre la fixture preparee, calcule en Normal et verifie que l'enveloppe minimale reste 23,2 x 23,2 x 31,6 mm, sans support artificiel.
4. Materialise l'artefact minimal : les cavites restent ouvertes et le plateau n'etire aucun corps.
5. Finalise en Normal : exige un `finalized_plan` courant, un residuel imprimable nul et aucun message de faux succes.
6. Materialise l'artefact final : un composant utilisateur par proprietaire, annexes soudees, encoche plateau et prise exactes.
7. Reprends ensuite le projet local exact a 18 conteneurs, boite 60 / utile 59,6 / sommet minimal 52,8, puis repete les etapes 3 a 6. Le corps 31,6 mm ne doit jamais redevenir 38,4 mm.
8. Renvoie `OK` ou `KO` avec captures, identite de scene et diagnostics visibles.

## Criteres OK

- calcul minimal certifie et materalisable sans finition obligatoire ;
- aucune croissance liee a une reservation ;
- budget adjacent reactif ;
- finalisation complete, actuelle et recertifiee ;
- zero residuel imprimable hors vides techniques certifies ;
- unions avant coupes ;
- un seul composant utilisateur par proprietaire ;
- encoches seulement sur les corps qui atteignent leur plan et chevauchent l'empreinte ;
- scene materialisee depuis l'identite exacte de l'artefact final ;
- aucun faux `Projet accepte` ou `finalized_plan_ready` sur echec.

## Criteres KO

Tout ecart geometrique, residuel non nul, faux succes, composant annexe separe, corps minimal etire, encoche sur mauvais corps, identite stale, erreur Fusion ou absence de marqueur 0.1.67 rend la gate `human-KO`.

La gate ne vaut jamais validation d'impression : `print-validated=false`.

<!-- P64-L09S-0167-RECENT-KO -->
## Cas complexe recent obligatoire pour 0.1.67

Ouvre le projet complexe recent qui a invalide `0.1.66`, puis verifie :

1. le conteneur dont le minimum canonique est `76 x 76 x 31.8 mm` ne devient jamais `53.6 x 76 x 31.8 mm` ni toute autre enveloppe inferieure sur un axe ;
2. le calcul aboutit avec les plateaux sans creer de porteur artificiel ;
3. la finalisation ne se termine pas apres environ deux secondes avec un faux echec de recherche approfondie ;
4. la finalisation publie un plan courant recertifie et un residuel imprimable nul ;
5. le bouton de materialisation n'est active qu'apres ce succes reel ;
6. la materialisation conserve les volumes, les unions et les encoches attendus.

Tout rabotage d'un minimum, residuel imprimable, faux succes UI, composant supplementaire ou encoche hors cible vaut `human-KO` immediat.

<!-- P64-L09S-0167-PREPARED -->
## Preparation Fusion 0.1.67 confirmee

- statut : `prepared-not-human-observed` ;
- commit installe : `832c9d5` ;
- preflight : `85c578d051b83fcd71b6b3c6eeaed7601748b1b95e5e942377faf9f52ef3e528` ;
- package/manifeste/reglages/marqueur : verifies ;
- cas humain obligatoire : projet recent a 28 conteneurs, avec controle du minimum `76 x 76 x 31.8 mm` ;
- `fusion-validated=false` et `print-validated=false` jusqu'au verdict humain.
