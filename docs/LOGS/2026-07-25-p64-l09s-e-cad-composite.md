# Journal - P64-L09S-E CAD composite et encoches exactes

## Changement de statut

La fermeture composite D est maintenant transformee en plan final courant. Le finaliseur combine le certificat produit rectangulaire avec coupes, le certificat de partition composite et le certificat de traduction CAD. Un echec de l'un de ces contrats bloque la publication.

## Chaine geometrique

Le CAD IR conserve un composant par proprietaire. Il cree le coeur, unit les annexes dans l'ordre de leurs parents, puis applique les cavites et les encoches plateau/livret. Les zones de prise supplementaires sont comptees comme vides techniques certifies afin de maintenir une conservation volumique honnete.

Le squelette Fusion verifie le Z bas commun, la vraie face verticale X/Y, le parent resolu et le repere global du corps composite. Son moteur d'execution existant realise les unions avant toute coupe.

## Validation

Les suites ciblees cycle etage, CAD IR, squelette Fusion, palette projet et refus composites passent. La suite autorisee complete passe a 820/820 avec un test SCIP natif ignore et 72 tests interdits exclus.

Aucune installation Fusion, aucune observation Fusion et aucune validation d'impression pendant E. `print-validated=false`.
