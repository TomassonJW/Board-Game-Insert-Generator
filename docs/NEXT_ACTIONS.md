# Next Actions

Derniere mise a jour : 2026-07-03

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici.

## Mission suivante recommandee

### 1. P3-M003 - Ajouter des profils d'impression

Statut : `ready`.

Pourquoi maintenant :

- `P3-M001` a ajoute la classification explicite des faces ;
- `P3-M002` applique maintenant les regles de tolerance depuis ces roles ;
- les valeurs par defaut n'ont pas change ;
- les rapports exposent les tolerances appliquees et leurs raisons.

Objectif :

- ajouter des profils d'impression explicites qui se resolvent en
  `ToleranceProfile` visible, sans cacher les valeurs finales.

Contraintes :

- ne pas modifier les valeurs par defaut sans gate humaine separee ;
- ne pas presenter un profil comme valide physiquement ;
- garder le coeur Python independant de Fusion 360 ;
- ne pas lancer Fusion 360, STL ou 3MF.

Validation attendue :

- tests unitaires loader/validation/rapport ;
- exemple CLI Markdown et JSON ;
- documentation des profils et de leurs limites physiques.

## Missions a ne pas lancer tout de suite

- Modification des valeurs de tolerance par defaut sans gate humaine dediee.
- Generation Fusion 360 de blanks tant que `P4-M000` n'a pas produit de rapport
  de gate.
- Cavites complexes tant que les parois minimales et clearances ne sont pas
  formalisees.
- Modules composites complets tant que `P6-M001` n'est pas cadree.
- Assistant de conception tant que plusieurs strategies et profils ne sont pas
  stabilises.
- Packaging produit tant que des exemples imprimes reels ne sont pas
  disponibles.

## Fin de chaque mission

Avant de terminer :

- mettre a jour `docs/STATUS.md` ;
- mettre a jour `docs/BACKLOG.md` ;
- remplacer cette liste par les prochaines actions reelles ;
- ajouter une ADR si une decision structurante a ete prise ;
- ajouter une entree de log si l'orientation ou le statut a change ;
- lancer les tests disponibles ou expliquer pourquoi ils n'ont pas ete lances ;
- committer proprement si le depot a ete modifie.