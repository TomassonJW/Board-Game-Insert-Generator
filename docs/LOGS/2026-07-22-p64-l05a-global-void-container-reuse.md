# Journal — P64-L05A insertion dans le vide global — 2026-07-22

## Déclencheur

Le retour humain L04V confirme que l’insertion d’un asset dans un conteneur
existant fonctionne, mais que l’ajout d’un nouveau conteneur dans un volume
global manifestement disponible invalide encore le plan. Le solve depuis zéro
peut ensuite échouer à retrouver le plan matérialisable.

## Décision

ADR-0076 accepte une exception bornée à ADR-0075 : exactement un nouveau
conteneur peut être inséré à voisins figés, puis le plan complet est recertifié.
Les zones résiduelles affichées ne sont pas considérées comme une preuve.

## Livraison

- producteur pur et déterministe à positions de contact ;
- identité, provenance, caps et raisons d’arrêt versionnés ;
- tentative L05A après L04A dans la synchronisation staged ;
- bridge validate_project et retour palette dédié ;
- tests purs, staged, bridge et DOM ;
- fallback global explicite, aucune scène automatique.

## Périmètre préservé

Aucun solveur, lane, budget Deep, schéma projet, géométrie P45, tolérance,
finalisation, CAD IR, scène ou valeur physique n’est modifié. Le projet
personnel de Thomas reste hors dépôt et inchangé.

## Suite

P64-L05B est la prochaine mission unique : capturer un SolverCaseBundle
versionné depuis un bouton DEV explicite, sans auto-modification du solveur.
