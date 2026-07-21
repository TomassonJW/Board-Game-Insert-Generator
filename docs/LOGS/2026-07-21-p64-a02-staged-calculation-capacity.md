# Journal P64-A02 — calcul étagé et capacité réutilisable

Date : 2026-07-21

## Mission

Transformer les propositions produit validées en architecture et pilotage
exécutables, sans modifier le runtime, le schéma, les valeurs physiques ou la
gate Fusion active.

## Préflight Git

- worktree dédié : C:\Users\janko\.codex\worktrees\3698\BGIG ;
- branche mission : codex/p64-a02-staged-calculation-capacity ;
- base vérifiée au démarrage : cec3318e3714614497afff0c5b434a8653fcdc27 ;
- origin/main identique après fetch --prune ;
- checkout principal et autres worktrees étrangers laissés intacts.

## Arbitrage inscrit

ADR-0071 retient une boucle en cinq états : source, analyse locale, agencement
global, plan finalisé et scène matérialisée. Les analyses locales sont
incrémentales ; le solve global et la finalisation deviennent des actions
explicites après leurs futures gates.

ADR-0072 accepte une carte de capacité éphémère, avec deux objets séparés :

- InternalOpportunityZone : capacité potentielle dans l'enveloppe inchangée d'un
  conteneur existant ;
- BoxReserveBay : volume monde volontairement réservé pour un futur conteneur.

La proposition post-solve est faisable et utile sous ces limites : elle peut
éviter une nouvelle recherche de poses, jamais la recertification. Un nouveau
conteneur sans baie réservée impose un solve global.

## Garde-fous

- le top 3 est une shortlist UX, jamais une limite moteur ;
- les scores classent seulement des variantes déjà certifiées ;
- P45 possède les sémantiques et formes locales ; P64 possède la recherche et le
  certificat global ;
- les jeux externes de conteneurs restent globaux ;
- aucun nouveau paramètre de cloison, default ou valeur physique ;
- aucun asset, séparateur, conteneur, corps ou cale automatique ;
- aucune scène avant matérialisation explicite ;
- une marge positive reste une condition nécessaire, pas une disposition ;
- no_solution_within_budget reste honnête ;
- fusion-validated: false et print-validated: false pour P64-A02.

## Pilotage livré

- deux ADR et deux contrats/programmes normatifs ;
- roadmap L01-L03, F01-F03 et C01-CV ;
- backlog détaillé avec dépendances, acceptation et gates ;
- pilotage courant, next actions, status, capabilities et gates synchronisés ;
- architecture, solveur, géométrie, tolérances, UX Fusion et qualité amendés ;
- garde-fou documentaire automatisé pour les quatre nouvelles sources.

La seule action courante reste P64-V2H03V 0.1.55. Aucune mission runtime nouvelle
n'est ouverte.

## Vérifications

- git diff --check : OK avant journal ;
- test documentaire ciblé : 2/2 OK ;
- suite complète : 571/571 OK en 160,087 s ;
- compileall src tests : OK ;
- frontière adsk du cœur : OK.

Le worktree neuf ne contient pas de .venv ; les preuves Python ont utilisé
C:\Program Files\Python310\python.exe via le wrapper Windows gardé. Une première
invocation ciblée par nom de module a confirmé que tests n'est pas un package ;
la preuve correcte a été relancée par unittest discover.

## Suite

1. observation humaine P64-V2H03V ;
2. clôture documentaire H03 ;
3. requalification P44-V ;
4. cadrage P45-M001 ;
5. seulement ensuite, ouverture éventuelle de P64-L01.
