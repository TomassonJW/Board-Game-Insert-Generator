# Journal — préparation du Goal P64-L09T

## Date

2026-07-27.

## Déclencheur

Thomas accepte la stratégie hybride de finition et demande d'intégrer tous les
objectifs au pilotage, puis de déléguer le Goal complet dans un nouveau
clavardage avec `gpt-5.6-sol` en raisonnement très élevé.

## Faits humains enregistrés

- La jauge 0.1.69 est fluide et constitue un acquis.
- Les cas de base 01 et 02 sont fortement améliorés.
- `CasLimite01+` calcule mais ne finalise pas ; le certificat composite produit
  rejette le candidat.
- `CasLimite02+` calcule mais la fermeture brute préalable échoue même avec un
  petit ajout.
- Le placement actuel favorise trop les piles.
- Le mode automatique des plateaux ne fait que centrer.
- Une coupe de plateau peut laisser une paroi trop fine près d'une cavité.
- La réutilisation automatique après édition doit être supprimée.

## Décisions

- 0.1.69 devient `human-KO`, avec acquis positifs conservés.
- ADR-0093 est acceptée.
- P64-L09T devient le programme correctif actif.
- Une seule finition automatique immédiate : extensions rectangulaires puis
  annexes soudées.
- L'interface annexe/propriétaire a un jeu nul ; tous les jeux externes restent
  normatifs.
- Les corps minimaux, cavités et poses de réservations sont figés avant la
  finition.
- La priorité aux couches basses est globale et lexicographique, pas gloutonne.
- Les origines X/Y de plateaux/livrets quittent le parcours normal.
- Les cales séparées, séparateurs sans fond et conteneurs générés rejoignent
  P64-F03 comme capacités différées.

## Programme

P64-L09T-A à G couvre :

1. recalcul explicite ;
2. diagnostics d'arrêt ;
3. réservations automatiques et parois minimales ;
4. priorité aux couches basses ;
5. fermeture hybride réelle ;
6. certificat et CAD composites ;
7. durcissement, package, installation et préparation de gate.

P64-L09T-V reste une observation humaine et ne vaut pas impression.

## Frontières

- North Star inchangée.
- Aucune valeur physique ou tolérance modifiée.
- Aucun benchmark ou holdout.
- Aucun code produit dans la mission de pilotage.
- Aucun projet ou journal personnel versionné.
- Aucun worktree étranger modifié.
