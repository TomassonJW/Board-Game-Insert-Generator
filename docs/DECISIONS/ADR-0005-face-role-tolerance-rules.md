# ADR-0005 - Face-role tolerance rules

## Statut

Accepte.

## Date

2026-07-03

## Carte liee

- `P3-M002 - Apply tolerance rules from face classification`

## Contexte

`P3-M001` a ajoute une classification explicite des faces rectangulaires simples
sans changer les valeurs de tolerance par defaut ni les dimensions imprimables
existantes.

`P3-M002` doit maintenant utiliser ces roles pour calculer les offsets de facon
explicable. La gate humaine du modele de tolerance est validee pour ce perimetre,
avec trois contraintes : garder le coeur Python pur, ne pas changer les valeurs
par defaut et ne pas presenter les jeux comme valides physiquement.

Ce qui existe deja :

- `Cell` represente la reservation theorique de layout ;
- `PrintableBody` represente le corps imprimable apres offsets ;
- les roles de faces existent : `peripheral`, `neighbor`, `exposed`,
  `functional`, `internal`, `welded` ;
- les modules composites ne sont pas encore generes.

## Options

### Option A - Garder les offsets implicites

- Principe : continuer a convertir directement roles et axes en `FaceOffsets`.
- Avantages : changement minimal.
- Inconvenients : les rapports ne peuvent pas expliquer chaque offset.
- Risques : les futurs composites risquent de recreer une logique parallele.
- Cout de maintenance : faible maintenant, plus eleve ensuite.
- Compatibilite MVP : correcte mais peu explicable.
- Facilite de test : moyenne.

### Option B - Ajouter une application de tolerance par face

- Principe : convertir chaque `FaceClassification` en application explicite avec
  offset, source, regle et raison, puis deriver `FaceOffsets` de cette liste.
- Avantages : explicable, testable, compatible rapports et futurs composites.
- Inconvenients : ajoute un objet metier supplementaire.
- Risques : les valeurs restent abstraites tant qu'elles ne sont pas imprimees.
- Cout de maintenance : raisonnable.
- Compatibilite MVP : forte.
- Facilite de test : forte.

### Option C - Attendre le moteur complet de modules composites

- Principe : reporter les regles fines jusqu'a `P6`.
- Avantages : modele final potentiellement plus complet.
- Inconvenients : bloque la Phase 3 et laisse les offsets peu explicables.
- Risques : integration Fusion prematuree avec un contrat de tolerance faible.
- Cout de maintenance : eleve par report de dette.
- Compatibilite MVP : faible.
- Facilite de test : faible maintenant.

## Decision

Retenir l'option B.

Le coeur Python transforme chaque classification de face en
`FaceToleranceApplication`. Cette application porte :

- la face ;
- le role ;
- l'offset applique ;
- la source de tolerance ;
- l'identifiant de regle ;
- un indicateur `receives_clearance` ;
- la raison textuelle.

Regles retenues :

- `peripheral` : `peripheral_clearance_mm + printer_compensation_mm` ;
- `neighbor` : `module_gap_mm / 2 + printer_compensation_mm` ;
- `exposed` : aucun jeu, seulement `printer_compensation_mm` si non nul ;
- `functional` en `z_min` : aucun jeu, face ancree a Z=0 ;
- `functional` en `z_max` : `vertical_lid_clearance_mm` ;
- `internal` : aucun jeu ;
- `welded` : aucun jeu.

Cette decision n'autorise pas :

- le changement des valeurs par defaut ;
- la validation physique des jeux ;
- l'integration Fusion 360 ;
- les modules composites complets ;
- l'export STL/3MF.

## Consequences

### Positives

- Chaque offset devient explicable dans les rapports Markdown/JSON.
- Les tests peuvent verrouiller les faces qui ne recoivent aucun jeu.
- Les futurs modules composites pourront reutiliser la meme surface de regles.
- Les dimensions des exemples existants restent comparables.

### Negatives

- `PrintableBody` porte une metadonnee supplementaire.
- Les roles `internal` et `welded` sont testables comme regles, mais pas encore
  produits automatiquement par un moteur composite.

### Risques

- Les valeurs par defaut restent non calibrees physiquement.
- Les rapports plus riches peuvent etre confondus avec une validation physique ;
  la documentation doit continuer a marquer les jeux comme a valider par
  impression reelle.

## Alternatives refusees

- Offsets implicites : refuse car non explicable et fragile pour les composites.
- Moteur composite complet : refuse car hors perimetre de `P3-M002`.

## Suivi

- Tests unitaires sur les six roles de face.
- Rapports Markdown/JSON avec les tolerances appliquees.
- `P3-M003` pourra ajouter des profils d'impression sans changer les valeurs par
  defaut sans gate separee.
- Toute modification des valeurs par defaut reste soumise a gate humaine.