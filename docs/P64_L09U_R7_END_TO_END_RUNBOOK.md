# P64-L09U-R7 — placement canonique, pile automatique et grille 0,1 mm

## Objectif

Corriger les défauts humains de 0.1.77 sans perdre la profondeur et les accès
confirmés :

1. position automatique utile, déterministe et compatible avec toutes les
   parois canoniques ;
2. pile automatique petit-dessous, grand-dessus ;
3. intervalles Z et opérations soustractives exacts, sans plaque ni surplomb ;
4. coordonnées et dimensions produit canoniques sur une grille de `0,1 mm`.

## Autorités

- `docs/P64_L09U_R6_V_0177_HUMAN_KO_EVIDENCE.md` ;
- ADR-0099 à ADR-0102 ;
- les ADR R7 à créer avant les changements structurants ;
- les deux projets personnels et le journal humain, strictement en lecture
  seule.

## Invariants

- Profondeur calibrée et micro-chevauchements R6 conservés.
- Parties sous et hors plateau accessibles.
- Cavités figées en identité, X/Y, orientation et profondeur.
- Réservations virtuelles, jamais corps utilisateur ou supports artificiels.
- Fonds, parois, appuis et enveloppes canoniques conservés.
- BRep transitoire, zéro Combine rectangulaire, rollback et respiration
  conservés.
- Aucune nouvelle valeur physique.
- Aucun benchmark, holdout, corpus ou tournoi solveur.
- Aucun mode manuel de plateau/livret dans R7.

## Missions atomiques

### R7-A — verdict humain et trace initiale

- Classer 0.1.77 `human-KO`, `do-not-run`.
- Rejouer `CasLimite02+` et `CasLimite02++` en lecture seule.
- Séparer plan minimal, candidats XY, score, enveloppes de paroi, régions,
  intervalles Z, finalisation, CAD IR et plan Fusion.
- Localiser la première divergence.

### R7-B — contrats et ADR

- Définir le score automatique robuste.
- Définir l'enveloppe de paroi finale recertifiée.
- Définir l'ordre automatique par empreinte réellement orientée et la
  compatibilité de `stack_order`.
- Définir la grille produit `0,1 mm`, ses frontières de quantification, ses
  migrations et ses digests.

### R7-C — placement et parois

- Générer uniquement des positions sur la grille produit.
- Favoriser les encoches utiles et centrées au-dessus de matière intérieure.
- Rejeter les fragments de paroi, les bords de boîte gratuits et les
  séparations inférieures au minimum.
- Recertifier la pose contre les corps finalisés sans la déplacer.

### R7-D — pile et matérialisation

- Ordonner automatiquement petit-dessous, grand-dessus.
- Conserver empreintes et intervalles locaux exacts jusqu'au plan Fusion.
- Refuser les micro-coupes et les volumes additifs hors enveloppe finale.
- Prouver que l'aperçu, la CAD IR et le plan Fusion racontent la même pile.

### R7-E — quantification et migrations

- Quantifier les positions candidates et les dimensions dérivées publiées au
  dixième.
- Garder un epsilon interne plus petit pour les comparaisons/topologies.
- Invalider ou migrer explicitement les artefacts et digests historiques.
- Mesurer le nombre de candidats et le temps des replays autorisés, sans
  benchmark interdit et sans promettre un gain non observé.

### R7-F — gate automatisée et candidate Fusion

- Lancer les tests ciblés puis la suite autorisée complète.
- Vérifier les SHA personnels avant/après.
- Intégrer seulement avec tests verts et diff relu.
- Installer et vérifier la nouvelle candidate.
- Ouvrir une nouvelle gate humaine ; garder
  `fusion-validated=false`, `print-validated=false`.

## Régressions publiques minimales

- paroi résiduelle `0,4 mm` rejetée sous minimum `1,2 mm` ;
- centrage/encoche utile préféré ;
- décalage au dixième ;
- distance au bord de boîte ;
- deux empreintes séparées et séparations canoniques ;
- pile forcée petit-dessous/grand-dessus ;
- absence d'encoche `0,5–0,6 mm` ;
- absence de plaque ou surplomb ;
- conservation des cavités R6 ;
- propagation identique jusqu'au plan Fusion.

## Arrêt

Le programme s'arrête après installation de la candidate. La nouvelle gate
Fusion reste humaine.

`fusion-validated=false`, `print-validated=false`.
