# P64-L04R1 — Preuve du correctif de cache négatif

Date : 2026-07-22
Statut : automated-validated

## Reproduction d'origine

Sur « Mon insert », une session fraîche produit
deep_extension_exhausted_without_incumbent en environ 8 secondes. Avant R1,
le second calcul identique était un cache hit en 4 ms et l'interface affichait
0 s. Le cache mélangeait donc durée de restitution et durée de recherche.

## Preuves après correction

- staged : 11/11 tests OK, dont cache négatif non stocké et succès certifié réutilisé ;
- bridge : 24/24 tests OK avec result_timing terminal ;
- DOM : 35/35 tests OK avec Recherche, Cache, Recherche initiale et Restitution cache ;
- Ruff ciblé : OK ;
- py_compile ciblé : OK ;
- syntaxe JavaScript extraite : OK ;
- suite complète : 651/651 tests OK en 143,528 s ;
- frontière adsk et diff-check vérifiés avant intégration.

Aucun solveur, budget, lane, classement, certificat, schéma projet, manifest,
finaliseur, CAD IR ou comportement de scène n'est modifié.
