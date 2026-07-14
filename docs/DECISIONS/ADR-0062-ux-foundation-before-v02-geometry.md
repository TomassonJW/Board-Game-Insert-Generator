# ADR-0062 - Fondation UX avant les geometries V0.2

## Statut

Proposee le 2026-07-14 ; decision humaine P67-V requise.

## Date

2026-07-14

## Cartes liees

- P67-M000 - Capture et cadrage de la revue UX
- P67-V - Arbitrage humain post-MVP
- P44-M001 a P44-V - Fondation UX proposee
- P45 - Formes et ergonomie geometrique
- P46 - Acceptation V0.2

## Contexte

Le MVP V0.1 Fusion-only est accepte dans Fusion sur le package 0.1.20. La
premiere revue post-MVP observe toutefois une dette structurelle avant l ajout
de nombreux parametres geometriques : cartes volumineuses, champs egalement
etires, sections qui se referment pendant la saisie, six onglets qui separent
des objets lies, elements affiches loin de leurs conteneurs et cycle de document
incomplet.

Le defaut de fermeture est concret : la palette reconstruit les listes HTML
apres chaque evenement `change`. La reponse derivee asynchrone reconstruit aussi
plusieurs vues. Focus, details ouverts et contexte de scroll ne forment donc pas
encore un socle fiable pour les futurs controles de rayons, encoches, fonds et
couvercles.

ADR-0060 a accepte une divulgation progressive locale et ADR-0061 a place
P44-P46 sur la V0.2 formes/ergonomie. La revue P67 demande maintenant si P44
doit commencer par stabiliser l experience avant la geometrie. P69 doit rester
la revue exhaustive apres P50.

Contraintes :

- produit Fusion-only et palette embarquee ;
- coeur Python sans `adsk` ;
- schema et projets historiques preserves ;
- aucun changement de solveur, tolerance ou geometrie glisse dans un lot UI ;
- complements toujours en quarantaine sans contrat separe ;
- P44-P50 gardent leurs identifiants ;
- aucune qualification d impression.

## Options

### Option A - Geometrie V0.2 avant UX structurelle

- Principe : conserver P44 contrat, P45 geometrie, P46 gate, puis P69 pour l UX.
- Avantages : sequence initiale inchangée ; acces rapide aux formes.
- Inconvenients : nouveaux champs construits sur des composants instables ;
  refonte et tests a reprendre ensuite.
- Risques : surcharge cognitive, regressions de focus et dette de migration UI.
- Cout de maintenance : eleve a moyen terme.
- Compatibilite MVP : compatible, mais faible coherence produit.
- Facilite de test : mediocre tant que le DOM est reconstruit pendant la saisie.

### Option B - Correctif UI minimal puis geometrie

- Principe : corriger focus et compacite CSS, sans changer l architecture
  d information.
- Avantages : faible delai, risque technique borne.
- Inconvenients : conserve la separation Elements/Conteneurs, les six onglets
  et le cycle de document incomplet.
- Risques : deuxieme refonte necessaire peu apres.
- Cout de maintenance : moyen.
- Compatibilite MVP : excellente.
- Facilite de test : bonne pour le defaut local, insuffisante pour le parcours.

### Option C - Fondation UX bornee dans P44 puis geometrie P45

- Principe : stabiliser et densifier les composants, passer a quatre onglets,
  afficher les elements dans leurs conteneurs, completer le cycle projet et
  fermer P44 par une gate Fusion UX ; ajouter ensuite les formes dans P45.
- Avantages : composants durables, meilleur parcours novice, puissance expert
  conservee, moins de formulaires a jeter.
- Inconvenients : P44 change de sous-scope et V0.2 geometrie commence plus tard.
- Risques : refonte trop large si les missions ne restent pas atomiques.
- Cout de maintenance : plus faible apres la fondation.
- Compatibilite MVP : compatible si schema, solveur et CAD restent inchanges.
- Facilite de test : bonne avec missions et gates separees.

## Decision proposee

Retenir l option C, sous reserve de P67-V.

Le perimetre propose est :

1. P44-M001 stabilise focus, panneaux ouverts et scroll sans changement metier ;
2. les missions P44 suivantes traitent une cause a la fois : densite, quatre
   onglets, composition conteneur/contenu, creation/presets, document/diagnostic
   et calcul adaptatif ;
3. P44-V valide uniquement cette fondation dans Fusion ;
4. P45 porte les profils de cavite et geometries ergonomiques ;
5. P46 reste la gate de la V0.2 complete ;
6. P69 reste l audit exhaustif apres les couvercles P47-P50.

Cette proposition autorise un changement de presentation et de workflow dans
la palette apres acceptation. Elle n autorise pas encore :

- la reactivation des complements ;
- un schema de conteneurs imbriques ;
- une reservation de plateau sous les conteneurs ou servant de couvercle ;
- une nouvelle forme de cavite ;
- un changement de tolerance ou de solveur ;
- une materialisation Fusion automatique.

## Consequences

### Positives

- les parametres V0.2 seront ajoutes sur des composants plus stables ;
- la relation conteneur/contenu devient lisible sans migration du projet ;
- le parcours novice raccourcit, tandis que les diagnostics restent disponibles ;
- le cycle de fichier peut devenir un vrai workflow de document local ;
- P69 conserve une valeur distincte sur le produit enrichi.

### Negatives

- le mot `ergonomie` couvre temporairement ergonomie d interaction puis
  ergonomie physique ; les contrats devront toujours les distinguer ;
- P44 contiendra plusieurs missions atomiques avant la geometrie P45 ;
- ADR-0060 devra recevoir un amendement sur les details essentiels toujours
  visibles et l abandon du principe « un seul element developpe ».

### Risques

- refonte monolithique : mitigée par P44-M001...M007 et une cause par mission ;
- logique metier deplacee en JavaScript : interdite, projections Python gardees ;
- regression anciens projets : tests roundtrip, import et compatibilite requis ;
- calcul automatique instable : decision et mission separees, scene toujours
  explicite ;
- confusion avec P69 : P44-V reste une gate de fondation, pas un audit complet.

## Alternatives refusees

Aucune option n est encore refusee tant que P67-V n a pas tranche. La
recommandation documentee refuse seulement de traiter l option C comme deja
acceptee.

## Suivi

- Arbitrer D67-01 a D67-11 dans
  `docs/P67_POST_MVP_PRIORITIZATION_REPORT.md`.
- Si l option C est acceptee, amender ADR-0060 et ADR-0061 sans les effacer.
- Rendre uniquement P44-M001 `ready`, pas tout P44.
- Rediger le contrat fonctionnel P44-M001 avant toute modification runtime.
- Conserver P45, P46, P47-P50 et P69 bloques par leurs dependances.
