# P64-L09R-E — Preuve de progression et réactivité

Date : 2026-07-25

Statut : `implemented-product`, `automated-validated`.

## Portée livrée

- La zone d’activité se trouve dans la barre inférieure, immédiatement au-dessus des trois actions produit, sur toute la largeur disponible.
- Au repos, l’attribut `hidden` applique `display:none` : aucun espace et aucun dernier état terminal ne subsistent.
- Le rendu se rafraîchit toutes les 1 000 ms.
- Calcul minimal et finition affichent le temps écoulé sur leur budget total réel : 3, 10, 20, 60 ou 180 secondes.
- La matérialisation utilise une jauge indéterminée et un libellé de phase CAD réel ; aucun pourcentage ni délai n’est inventé.
- La publication normale, le rejet, le timeout de transport ou l’erreur retirent immédiatement l’activité du rendu.

## Séparation des threads

- `palette_worker.py` reçoit uniquement une copie de la demande JSON et des chemins convertis en chaînes.
- Seuls `solve_project` et `finalize_project` sont exécutés dans le worker.
- Le module worker n’importe pas `adsk`, ne publie rien vers HTML et ne synchronise aucun objet CAD.
- La palette interroge le registre une fois par seconde ; ce heartbeat ne rappelle jamais le solveur.
- Le callback Fusion reste seul à envoyer la réponse vers la palette.
- `materialize_project` et `regenerate_project` restent dans le callback Fusion autorisé, puis passent par la synchronisation CAD existante.

## Rejets sûrs

- Une seule voie calcul/finition peut être active ; un second lancement est rejeté avec l’identité de l’opération conservée.
- Les autres mutations du pont projet ou document sont refusées pendant le travail pur au lieu de courir contre l’état partagé. Les sauvegardes, validations et réglages différés sont relancés après la fin.
- Au retour, le thread Fusion compare la révision et un digest SHA-256 couvrant le projet, les réglages solveur et le budget de finition.
- Toute différence produit `stale_or_cancelled` avec `source_identity_changed`; le résultat n’est pas appliqué et une validation courante est replanifiée.

## Preuves automatisées

- Worker : hors-thread appelant, données pures, double lancement fail-closed, changement de projet rejeté et changement du budget de finition rejeté.
- DOM : emplacement exact, pleine largeur, absence terminale, cinq budgets, jauges bornée et indéterminée, rafraîchissement et polling à 1 000 ms.
- Transport : routage calcul/finition vers le worker, polling sans travail métier et matérialisation conservée sur le callback Fusion.
- Régressions : pont projet, cycle staged, activité, résultat et synchronisation CAD restent verts.

## Validation

- Tests ciblés : 130/130 OK.
- Syntaxe JavaScript extraite : `node --check` OK.
- Compilation Python : OK.
- Suite complète : 867/867 en 243,972 s ; un test natif ignoré sous Python 3.10.
- Tests documentaires : 2/2 OK ; `git diff --check` : OK.

## Limites et non-objectifs

- Aucune observation visuelle dans Fusion n’est revendiquée ; la réactivité réelle du runtime sera observée à P64-L09R-V.
- Aucun benchmark de solveur, package Fusion, réglage Fusion, tolérance, valeur physique ou fait d’impression n’est produit.
- P64-L09R-F doit maintenant durcir les cas représentatifs et préparer le dossier de gate avant toute manipulation humaine.