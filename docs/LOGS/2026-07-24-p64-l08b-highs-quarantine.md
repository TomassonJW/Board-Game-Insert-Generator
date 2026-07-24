# 2026-07-24 — P64-L08B : quarantaine HiGHS hors du parcours Auto

La mesure tripliquée sur les sept cas de régression montre que HiGHS ne couvre
pas les cas à réservation, fermeture continue ou densité traités comme 3D. Sur
les cas où il est effectivement exécuté, il ajoute environ 34 à 53 ms P50 aux
cas rapides et ne produit aucune proposition sur les deux cas de variantes.

La lane de sol est donc retirée du parcours Auto et Deep. Ce n'est pas une
suppression du matériel d'audit : le binaire verrouillé, le contrat hors ligne et
le script de diagnostic restent disponibles pour la comparaison P64-L08, sans
allégation de solvage 3D.
