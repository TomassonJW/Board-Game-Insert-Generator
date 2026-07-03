# ADR-0003 - JSON first, CSV and Sheets later

## Statut

Accepte.

## Contexte

Le projet doit commencer localement, sans service externe, avec un format humainement lisible et suffisamment structure pour decrire une boite, des tolerances et des modules.

CSV et Google Sheets seront utiles pour des utilisateurs non techniques ou pour des inventaires de composants, mais ils introduisent des decisions de mapping et de validation supplementaires.

## Options

1. JSON en premier.
2. CSV en premier.
3. Google Sheets en premier.
4. Interface graphique en premier.

## Decision

Utiliser JSON pour la V0.

CSV et Google Sheets seront ajoutes comme formats d'entree convertis vers le meme modele interne.

## Consequences

Positives :

- format local ;
- aucun service externe ;
- structure imbriquee naturelle ;
- exemples faciles a versionner ;
- validation simple.

Negatives :

- moins confortable qu'un tableur pour certains utilisateurs ;
- pas de commentaires natifs en JSON ;
- necessite une documentation claire.

## Alternatives refusees

Google Sheets en premier est refuse pour eviter une dependance externe prematuree. CSV en premier est refuse parce que la configuration contient des structures imbriquees qui deviennent vite fragiles en colonnes.
