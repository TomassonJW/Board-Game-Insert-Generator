# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Gate humaine active

### Gate - Premiere integration Fusion 360

Statut : `blocked`.

Decision demandee :

- valider ou refuser le passage vers la Phase 4 executable ;
- choisir le perimetre autorise pour la prochaine mission ;
- confirmer qu'aucune generation Fusion, aucun import `adsk` et aucun export
  STL/3MF ne sont autorises tant que le perimetre n'est pas explicitement valide.

Contexte :

- le moteur Python pur charge, valide, place, applique les tolerances et produit
  des rapports Markdown/JSON ;
- les profils d'impression et le protocole de calibration existent ;
- le rapport `docs/FUSION_360_GATE_REPORT.md` decrit l'etat actuel, les risques,
  les options et les criteres d'acceptation ;
- la prochaine progression touche Fusion 360, qui est protegee par gate humaine.

Options :

- Option 1 recommandee : autoriser seulement `P4-M001`, c'est-a-dire un contrat
  CAD-agnostic sans Fusion executable et sans import `adsk`.
- Option 2 : autoriser un squelette d'adaptateur non productif apres `P4-M001`.
- Option 3 : autoriser directement une premiere generation Fusion de blanks
  rectangulaires.
- Option 4 : reporter toute progression Phase 4.

Recommandation :

- choisir l'option 1 ;
- garder le coeur Python independant de Fusion ;
- stabiliser d'abord les objets CAD-agnostic, les axes, les unites, le nommage,
  les warnings et les criteres de validation.

Risques :

- duplication de logique layout/tolerance dans l'adaptateur Fusion ;
- confusion entre validation CAD et validation par impression reelle ;
- dette sur les conventions d'origine, d'axes, d'unites et de nommage ;
- debug plus lent si une integration executable commence avant contrat stable.

Fichiers concernes :

- `docs/FUSION_360_GATE_REPORT.md` ;
- `docs/FUSION_360_STRATEGY.md` ;
- `docs/HUMAN_GATES.md` ;
- `docs/BACKLOG.md` ;
- `docs/STATUS.md`.

Validation attendue de l'humain :

- repondre explicitement quelle option est validee ;
- si l'option 1 est validee, autoriser la mission `P4-M001 - Definir le contrat
  de representation intermediaire CAD` ;
- preciser si une future gate separee est souhaitee pour un squelette Fusion,
  une generation de blanks ou un export STL/3MF.

## Missions bloquees tant que la gate n'est pas validee

- `P4-M001 - Definir le contrat de representation intermediaire CAD`.
- Integration Fusion 360 executable.
- Premier export STL/3MF.
- Modification des valeurs de tolerance par defaut.
- Modules composites complets.

## Fin de chaque mission

Avant de terminer :

- mettre a jour `docs/STATUS.md` ;
- mettre a jour `docs/BACKLOG.md` ;
- remplacer cette liste par les prochaines actions reelles ;
- ajouter une ADR si une decision structurante a ete prise ;
- ajouter une entree de log si l'orientation ou le statut a change ;
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances ;
- committer proprement si le depot a ete modifie.