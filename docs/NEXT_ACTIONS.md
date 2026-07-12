# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055.

## Derniere mission terminee

P59 - materialisation CAD et synchronisation de scene, suivie des correctifs
runtime P60 0.1.7 et 0.1.8.

## Derniere preuve humaine

Le runtime 0.1.8 charge maintenant le projet, execute les boutons projet, calcule
une partition, affiche le resultat reel et materialise les bacs dans Fusion.
Cette observation leve les anciens KO de bootstrap et de transport QT. Elle ne
clot pas encore P60 : regeneration, inspection/export et absence de doublon
doivent encore etre confirmes sur le package courant.

## Mission courante

P60 - acceptance du vrai MVP, avec P60-UX-01 comme finition du parcours de creation Fusion-only, package 0.1.9.

Livrables implementes :

- palette initiale/minimale 1280 x 1100 ;
- presets moteur editables Jetons, Cartes sleevees, Des et Pions ;
- creation explicite Bac vide, Bloc plein / cale et Separateur ;
- dimensions finales X/Y/Z de chaque bac visibles en mode simple, avec valeur
  automatique si le champ reste vide et validation par le moteur ;
- packaging et tests d installation du nouveau module pur project_presets.py.

## Prochaine action prete

Installer le commit 0.1.9 exact puis rejouer P60 dans Fusion :

1. verifier les presets et leurs valeurs modifiables ;
2. creer un bloc plein et confirmer qu il ne contient aucune cavite ;
3. fixer une dimension finale de bac, recalculer et verifier le resultat ;
4. materialiser, regenerer sans doublon, inspecter puis exporter ;
5. confirmer la taille initiale de la palette.

## Mission suivante apres acceptation P60

P61 - contrat d empilement vertical explicite.

P61 commencera par une ADR et un contrat pur : etages Z, ordre bas/haut,
nombre de bacs, surfaces porteuses, hauteur cumulee et diagnostics. Aucun
empilement implicite ni duplication silencieuse de contenu ne sera introduit.

## Releases bloquees

P61 et P44 a P50 restent bloques jusqu a l acceptation humaine P60. P47 a P50
restent aussi bloques jusqu a l acceptation de P46.

## Gate humaine active

P60 uniquement. Le contrat reste docs/P60_FUSION_MVP_ACCEPTANCE.md et le
preparateur reste scripts/fusion/prepare_p60_mvp_acceptance.ps1. Codex installe
et verifie l add-in exact ; Thomas ne realise que les observations dans Fusion.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes. print-validated: false reste obligatoire.
