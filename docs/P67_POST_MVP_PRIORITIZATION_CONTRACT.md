# P67 - Atelier humain de priorisation post-MVP

Statut : `blocked-by-p66`, `human-review-required`, `no-runtime-change`.

## Objectif

P67 est le sas humain entre le MVP V0.1 accepte et tout developpement V0.2.
Il ne renumerote pas P44 a P50 et ne code rien. Il produit une decision
explicite, commentee et actionnable sur les priorites produit apres usage reel
de la palette Fusion. Il ne remplace pas P69, qui sera la revue UI/UX exhaustive
apres P44-P50.

L ordre des cartes est semantique, pas numerique : P67 est execute apres P66,
puis seulement P44-M001 peut devenir `ready`. Les identifiants P44 a P50 restent
canoniques pour conserver leurs liens aux ADR, contrats, tests et historique Git.

## Preconditions

- P66 Fusion OK documente sur un commit et package identifies ;
- aucun statut `print-validated` ne doit etre infere ;
- captures, notes d usage et, si disponibles, premieres observations P68 ;
- depot propre et pilotage V0.1 clos avant de commencer la revue.

## Revue obligatoire

L atelier doit etre fait dans Fusion, sur un projet reel ou la fixture P66, avec
commentaires structures par ecran et par tache. Il couvre assez de parcours pour
prioriser V0.2 sans pretendre remplacer l audit exhaustif P69 :

1. **Demarrage et comprehension** : launcher Utilities, taille de palette,
   chargement, premier projet et vocabulaire.
2. **Parcours** : ordre Boite, Plateaux et livrets, Elements du jeu,
   Conteneurs, Reglages, Apercu ; navigation, densite Compact/Detaille et
   lisibilite sans mode avance global.
3. **Saisie des elements** : presets, cartes sleevees, orientations, dimensions
   resolues, groupes, erreurs et grande cardinalite.
4. **Plateaux et livrets** : comprehension de l encastrement, prise, ordre de
   retrait, profondeur de cavite et representation en coupe.
5. **Conteneurs et reglages** : minimum, Auto/Cible/Fixe, tailles calculees,
   tolerances XY/Z, parois, fonds, estimation et etat perime.
6. **Apercu et scene** : score explique, appuis, residuels, materialisation,
   regeneration, export, preservation non-BGIG et details techniques.
7. **Complements explicites** : confirmer que cales, separateurs et bacs vides
   restent masques du parcours normal ; evaluer ulterieurement leur vrai
   contrat de suggestion/confirmation, sans les reactiver implicitement.
8. **Ergonomie V0.2** : classer arrondis, chanfreins, encoches, fonds faciles a
   vider et contraintes de resistance selon valeur utilisateur, risque physique
   et impact solveur/CAD.

Chaque observation est classee : `bloquant`, `important`, `amelioration`,
`question`, `hors-scope`. Une capture annotee est recommandee pour chaque
probleme visuel ou spatial.

## Livrable humain attendu

Le rapport `docs/P67_POST_MVP_PRIORITIZATION_REPORT.md` doit contenir :

- contexte de test, projet, commit et package ;
- captures annotees ou references precises aux ecrans ;
- parcours observe et points de friction ;
- tableau priorise valeur / effort / risque / dependances ;
- decision sur le premier lot P44 ;
- decision explicite sur le devenir des complements explicites ;
- liste des changements exclus de V0.2 ;
- autorisation ou refus de rendre P44-M001 `ready`.

## Decisions attendues

P67 doit choisir, sans implementation simultanee :

1. le sous-scope P44 : invariants de resistance et formes autorisees ;
2. la priorite P45 entre coins, chanfreins, encoches et fonds ;
3. les criteres de preview et de gate Fusion P46 ;
4. si les complements meritent un futur lot dedie, avec quelle politique de
   suggestion, confirmation et dimensionnement ;
5. le perimetre de mesures P68 a utiliser pour les premiers prints.

## Sorties possibles

| Decision humaine | Effet |
| --- | --- |
| P67 accepte | P44-M001 devient `ready`; les retours P68 continuent d alimenter V0.2. |
| P67 a revoir | aucune carte V0.2 ne devient `ready`; rapport complete uniquement. |
| P67 reoriente V0.2 | ADR ou amendement de contrat avant toute implementation. |

## Interdits

- ne pas renumeroter P44 a P50 ;
- ne pas demarrer P44/P45/P46 dans la revue ;
- ne pas faire passer une observation Fusion ou une impression en validation
  globale sans protocole et mesures ;
- ne pas reactiver les complements par un ajustement local non decide ;
- ne pas transformer les commentaires UX en logique JavaScript ou adsk.
- ne pas presenter P67 comme la revue UI/UX exhaustive reservee a P69.
