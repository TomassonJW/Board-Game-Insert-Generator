# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P4-M000 - Prepare Fusion 360 integration gate report

Statut : `ready`.

Pourquoi maintenant :

- le moteur Python pur charge, valide, place, applique les tolerances et produit
  des rapports Markdown/JSON ;
- les profils d'impression et le protocole de calibration existent ;
- la prochaine phase concerne Fusion 360, qui est protegee par gate humaine ;
- aucune integration Fusion executable ne doit etre commencee sans validation.

Objectif :

- preparer un rapport de gate Fusion 360 indiquant etat du moteur, readiness,
  manques, risques, options techniques, recommandation et criteres d'acceptation.

Contraintes :

- ne pas importer `adsk` ;
- ne pas creer d'adaptateur Fusion executable ;
- ne pas exporter STL/3MF ;
- ne pas pretendre que les sorties sont imprimables ou physiquement validees.

Validation attendue :

- suite unitaire du coeur ;
- relecture documentaire ;
- `git diff --check`.

## Missions a ne pas lancer tout de suite

- Integration Fusion 360 executable sans validation humaine de la gate `Premiere
  integration Fusion 360`.
- Premier export STL/3MF sans gate humaine dediee.
- Modification des valeurs de tolerance par defaut sans gate humaine dediee.
- Modules composites complets sans gate humaine dediee.
- Cavites complexes tant que les parois minimales et clearances ne sont pas
  formalisees.

## Fin de chaque mission

Avant de terminer :

- mettre a jour `docs/STATUS.md` ;
- mettre a jour `docs/BACKLOG.md` ;
- remplacer cette liste par les prochaines actions reelles ;
- ajouter une ADR si une decision structurante a ete prise ;
- ajouter une entree de log si l'orientation ou le statut a change ;
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances ;
- committer proprement si le depot a ete modifie.