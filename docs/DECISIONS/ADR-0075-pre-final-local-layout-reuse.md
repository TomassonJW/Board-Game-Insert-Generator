# ADR-0075 — Réutilisation locale pré-finalisation d’un agencement minimal

## Statut

Acceptée le 2026-07-22 après observation humaine de P64-L03R-C dans Fusion et
confirmation explicite du comportement attendu. Cette décision ouvre
P64-L04A ; elle ne transforme pas l’observation en retour P64-L03R-V positif et
ne vaut aucune validation Fusion ou
impression. Le parcours isolé L03R-V est supersédé par la gate combinée L04V.

## Date

2026-07-22

## Cartes liées

- `P64-L04A — Réutilisation locale à enveloppe fixe` ;
- `P64-L04B — Effort Approfondi anytime et borné` ;
- `P64-L04C — Retour UX des opérations longues` ;
- `P64-L04V — Gate Fusion du cycle incrémental` ;
- `P64-C01/C02` pour la capacité post-finalisation, qui reste distincte ;
- `P45` pour la géométrie et le certificat local du conteneur.

## Contexte

P64-L01 à L03R-C séparent désormais analyse locale, calcul minimal,
finalisation optionnelle et matérialisation. L’observation humaine du package
0.1.57 confirme une nette amélioration du placement minimal, mais révèle un
manque produit : après ajout ou modification d’un élément dans un conteneur
déjà placé, BGIG rend systématiquement le plan global obsolète même lorsqu’une
nouvelle disposition locale tient dans exactement la même enveloppe extérieure.

ADR-0072 traite un autre cas : convertir une capacité issue d’un plan finalisé
en nouvelle cavité ou baie. Le besoin présent intervient avant toute
finalisation. Il réutilise les variantes minimales et les cavités rectangulaires
déjà certifiées ; il ne transforme aucun surplus solide de finition.

Contraintes non négociables :

- aucune recherche de placement monde pendant une édition locale ;
- aucun déplacement silencieux d’un conteneur ou complément existant ;
- enveloppe locale et orientation monde strictement inchangées ;
- certificat local puis certificat global reconstruits ;
- échec fail-closed avec demande explicite de calcul global ;
- scène Fusion seulement désynchronisée, jamais régénérée automatiquement ;
- aucune nouvelle sémantique P45, valeur physique, tolérance ou migration ;
- `unknown` n’est jamais promu en compatible.

## Options

### Option A — Toujours rendre le plan global obsolète

- Avantage : invalidation simple.
- Inconvénient : relance inutile du solveur et perte d’une disposition monde
  déjà certifiée.
- Risque : le produit paraît incapable d’utiliser un volume local évident.

### Option B — Garder l’ancien plan sans recertification

- Avantage : réponse immédiate.
- Inconvénient : contenu, cavités, digests et certificat ne correspondent plus
  à la source.
- Risque : matérialisation d’un plan faux.

### Option C — Tenter une insertion locale bornée puis recertifier le plan fixe

- Avantage : le placement monde reste stable lorsque la nouvelle géométrie
  locale tient réellement dans l’enveloppe existante.
- Inconvénient : nouveau chemin de certification et télémétrie dédiée.
- Risque : confondre une tentative locale avec une promesse de réussite.

## Décision

Retenir l’option C.

### Pipeline normatif

```text
édition locale d’un conteneur
  -> nouvelle frontière locale certifiée
  -> tentative de conserver les cavités existantes et d’insérer les nouvelles
  -> sinon réagencement local borné dans la même enveloppe
  -> certificat local P45
  -> placements monde recopiés bit-à-bit
  -> certificat global P64 rejoué sans recherche
       -> succès : nouveau minimal_layout courant
       -> échec : ancien plan stale, Calculer l’agencement requis
```

Une réussite annonce `placement_reused: true` et
`global_solver_invocation_count: 0`. Elle ne dit jamais « aucun calcul » : les
dérivations et certificats locaux/globaux ont bien été rejoués.

### Frontière P45/P64

P45, via la frontière locale commune, possède la position des cavités dans le
conteneur et son certificat local. P64 possède la conservation des placements
monde et le certificat du plan complet. Le premier producteur incrémental reste
strictement rectangulaire et technique ; il ne revendique aucun mode
`Automatique`, `En ligne` ou `Empilé verticalement` de P45-M001.

### Conditions de tentative

La tentative est autorisée seulement si :

1. un `minimal_layout` courant et certifié existe ;
2. la boîte, les réservations supérieures, les réglages solveur et l’ensemble
   des corps monde sont inchangés ;
3. les changements source restent localisables dans des conteneurs existants ;
4. chaque conteneur touché peut produire ou sélectionner une variante certifiée
   dont l’enveloppe est exactement celle déjà placée ;
5. les compléments et tous les placements monde restent identiques ;
6. le certificat global commun accepte le nouveau plan.

Une modification de l’enveloppe, une nouvelle boîte, un nouveau conteneur, un
complément modifié, une réservation différente ou une certification échouée
impose `global_solve_required`.

### Identité et lifecycle

Le plan réutilisé est un nouvel artefact : nouveau digest, nouvelle révision
source et nouvelle provenance. L’ancien plan n’est jamais rebaptisé courant.
Toute CAD IR ou scène matérialisée devient `desynchronized`. La mise à jour de
Fusion reste une action explicite et conserve les règles d’ADR-0074.

### Observation Approfondi et UX

La même revue humaine constate que Normal est actuellement plus fiable sur le
cas observé qu’Approfondi, dont le timeout est trop long, et qu’aucun retour
d’attente suffisant n’indique l’activité du calcul ou de la matérialisation.
Ces défauts sont réels mais distincts : P64-L04B devra rendre Approfondi
anytime, conserver l’incumbent Normal et respecter une limite stricte ;
P64-L04C devra afficher étape, temps écoulé et activité sans faux pourcentage.
Ils ne sont pas inclus dans P64-L04A.

## Conséquences

### Positives

- ajout local possible sans bouleverser un puzzle monde déjà certifié ;
- comportement cohérent avec l’état incrémental L01 ;
- source, plan, CAD et scène conservent des identités exactes ;
- fallback global explicite et testable.

### Négatives

- davantage de statuts et de provenance dans l’orchestrateur ;
- les premiers producteurs restent rectangulaires et peuvent produire des faux
  négatifs ;
- une modification locale peut toujours exiger un solve global.

### Risques et mitigations

- faux espace libre : insertion conservatrice et certificat local fail-closed ;
- ancien placement accepté avec une enveloppe différente : égalité exacte des
  dimensions locales et monde ;
- stale masqué : nouvel artefact et nouvelle révision obligatoires ;
- déplacement implicite : comparaison bit-à-bit des placements monde ;
- confusion avec C02 : contrats et statuts séparés pré/post-finalisation.

## Alternatives refusées

- considérer l’espace visible comme une preuve sans contrôle des parois ;
- modifier directement la cavité ou le plan matérialisé ;
- lancer automatiquement le solveur global si la tentative locale échoue ;
- ouvrir C01/C02 avant les politiques de finalisation dont ils dépendent ;
- inclure dans le même lot la refonte d’Approfondi et l’animation UX.

## Suivi

- Contrat exécutable :
  `docs/P64_L04_INCREMENTAL_LOCAL_REUSE_CONTRACT.md`.
- P64-L04A livre le cœur, l’orchestration, la palette et les preuves
  automatisées de localité.
- P64-L04B est `automated-validated` ; P64-L04C reste le lot `ready` séparé.
- P64-L04V observera dans Fusion succès local, fallback explicite, scène stale
  et mise à jour sans doublon.
- `fusion-validated: false`, `print-validated: false`.
