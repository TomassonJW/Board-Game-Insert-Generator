# 2026-07-15 — P44-M005 création pilotée et presets

## Décision d’implémentation

La barre Créer devient un flux unique : preset, destination, Ajouter. Le
raccourci local + reprend le preset choisi pour le conteneur ouvert. Cette
projection s’appuie sur les données déjà présentes ; elle n’ajoute ni bridge ni
schéma.

## Frontières

Les presets personnels restent locaux, atomiques, importables et exportables.
Leur édition est différée. Les compléments restent en quarantaine.

## Validation

Package 0.1.28 ; tests automatisés et gate P44-M005V requis.
