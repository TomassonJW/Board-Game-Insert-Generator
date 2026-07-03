# Quality Rules

## Regles de conception

- Toutes les dimensions sont en millimetres.
- Les axes X, Y et Z doivent rester explicites.
- Le moteur pur ne depend pas de Fusion 360.
- Le JSON n'est pas le modele interne.
- Les tolerances ne sont pas codees en dur dans le layout.
- Les cellules theoriques ne sont pas des corps imprimables.
- Les modules composites ne recoivent pas de jeu entre primitives internes soudees.

## Regles de code

- Preferer des dataclasses typees et lisibles.
- Garder les erreurs comprehensibles pour un utilisateur technique.
- Tester le moteur hors Fusion.
- Eviter les dependances externes tant que la V0 n'en a pas besoin.
- Ne pas introduire de framework structurant sans ADR.
- Garder les fonctions petites et deterministes.

## Regles de configuration

- Aucun secret dans le depot.
- Les exemples doivent etre realistes mais non lies a des donnees sensibles.
- Les valeurs par defaut doivent etre prudentes.
- Les champs optionnels doivent avoir un comportement documente.

## Regles de validation

- Refuser les dimensions negatives ou nulles.
- Refuser une hauteur utile incoherente avec la boite.
- Refuser les quantites nulles.
- Signaler les layouts impossibles avec un message lisible.
- Ne jamais pretendre qu'un layout V0 est optimal.

## Regles de documentation

- Distinguer ce qui est implemente, prevu, hypothese ou a valider par impression.
- Documenter toute decision structurante par ADR.
- Garder les documents exploitables par un autre developpeur ou agent.
- Eviter la documentation decorative.
