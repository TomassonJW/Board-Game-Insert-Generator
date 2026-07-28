# 2026-07-28 — P64-L09U-R8-B décision du pipeline soustractif

- ADR-0105 est acceptée selon le modèle produit explicite donné par Thomas.
- La géométrie positive des conteneurs est finalisée et figée avant toute
  opération liée aux plateaux ou livrets.
- La passe plate ne produit que des différences booléennes.
- Le certificat impose `0 mm³`, `0` corps et `0` union positifs liés aux
  éléments plats.
- L'intervalle du plan Fusion devient l'intervalle exécuté par la BRep.
- Aucun solveur, budget, valeur physique, package ou code produit n'est changé.
- R8-B est `done-architecture`; R8-C devient `ready`.
- `fusion-validated=false`, `print-validated=false`.

Décision :
`docs/DECISIONS/ADR-0105-conteneurs-finalises-et-encastrements-strictement-soustractifs.md`.
