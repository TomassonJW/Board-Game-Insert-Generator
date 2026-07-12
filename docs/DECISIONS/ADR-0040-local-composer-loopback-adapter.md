# ADR-0040 - Local composer UI and loopback adapter

## Statut

Supersede pour le MVP par ADR-0055. Conserve comme decision historique du prototype P23.

## Date

2026-07-10

## Carte liee

- `P23-M001 - Spike app locale de composition`

## Contexte

Le moteur BGIG expose des plans P19, un placement P20 et un portefeuille P21, mais le parcours utilisateur reste compose de JSON, CLI et commandes Fusion de developpement. ADR-0036 a ete validee pour demarrer une surface locale de conception, Fusion restant adaptateur CAD/export.

P23 doit livrer une premiere experience locale, offline et testable sans Fusion. Elle doit utiliser le moteur comme source de verite et ne doit pas introduire de cloud, authentification ou nouvelle logique de placement dans l interface.

## Options

### Option A - Palette Fusion persistante

- Principe : UI HTML/JS dans Fusion.
- Avantages : contexte CAD immediat.
- Inconvenients : lifecycle Fusion, tests hors Fusion faibles, couplage UX/CAD.
- Risques : scene Fusion prise comme source de verite.
- Cout de maintenance : moyen a eleve.
- Compatibilite MVP : limitee au public deja expert Fusion.
- Facilite de test : faible.

### Option B - App locale React sans adaptateur Python

- Principe : UI frontend qui reimplemente les calculs ou ne lit que des exports statiques.
- Avantages : mise en route frontend rapide.
- Inconvenients : double representation ou absence d edition executable.
- Risques : divergence entre UI et moteur.
- Cout de maintenance : eleve a moyen terme.
- Compatibilite MVP : insuffisante.
- Facilite de test : moyenne.

### Option C - App locale React/Vite avec adaptateur Python loopback

- Principe : React/TypeScript/Vite pour l interaction ; adaptateur Python standard-library sur `127.0.0.1` pour convertir le draft en contrats moteur, produire P21 et exporter une selection.
- Avantages : UX independante du CAD, moteur unique, pas de dependance backend lourde, testable hors Fusion.
- Inconvenients : deux processus locaux pendant le developpement ; packaging a traiter plus tard.
- Risques : contrat HTTP mal versionne ou CORS trop ouvert.
- Cout de maintenance : modere et borne.
- Compatibilite MVP : forte.
- Facilite de test : forte avec tests Python HTTP et build TypeScript.

## Decision

Adopter l option C comme premiere tranche de la trajectoire hybride approuvee :

- `frontend/` contient une app React/TypeScript construite par Vite.
- `src/board_game_insert_generator/local_composer.py` est un adaptateur loopback, non un nouveau moteur ; il reutilise strictement les dataclasses, P20, P21 et CAD IR existants.
- L API locale est versionnee `bgig.local_composer.v0`, accepte seulement JSON, limite la taille des requetes et autorise CORS uniquement pour les origines Vite locales connues.
- Le navigateur importe et telecharge les projets/drafts ; le serveur ne propose ni lecture arbitraire de fichiers ni ecriture de projet distante.
- Les exports P23 sont une selection JSON explicite et une CAD IR metadata-ready. Fusion ne materialise rien automatiquement.

Cette decision autorise les dependances frontend React/React DOM, TypeScript, Vite et plugin React. Elle n autorise ni framework backend lourd, ni cloud, ni materialisation Fusion du plan selectionne.

## Consequences

### Positives

- Les utilisateurs disposent d un parcours clair : boite, assets, contraintes, variantes, selection et exports locaux.
- Les invariants moteur restent testables sans navigateur et l UI ne recalcule aucun placement.
- La frontiere future vers Fusion reste une selection explicite dans la CAD IR.

### Negatives

- Le developpement local demarre un serveur Python et Vite.
- Le packaging desktop et la persistence de projet avancee restent hors P23.

### Risques

- Toute evolution du draft doit rester versionnee et couverte par tests de conversion vers le moteur.
- Une API loopback ne doit jamais devenir une surface reseau publique ; elle est limitee a `127.0.0.1`.
- Les scores P21 restent des proxies et l UI doit conserver leurs limites visibles.

## Alternatives refusees

- Palette Fusion : reportee, car elle ferait de Fusion le centre de l experience prematurement.
- Reimplementation TypeScript du solveur : refusee, car elle dupliquerait la logique metier.
- FastAPI/serveur web complet : non necessaire pour le spike local et ajouterait une dependance backend structurante.

## Suivi

- P23 : adapter HTTP, draft versionne, frontend, tests de contrat et build livres. La recette HTTP loopback est passee ; l inspection visuelle automatisee reste a rejouer dans un runtime navigateur non bloque par le sandbox Windows.
- Gate distincte avant toute materialisation Fusion d une variante selectionnee.
- Gate physique maintenue avant toute promesse d ergonomie ou d impression.