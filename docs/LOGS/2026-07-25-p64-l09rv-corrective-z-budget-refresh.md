# 2026-07-25 — P64-L09R-V correctif Z et budget

## Contexte

La gate Fusion 0.1.64 a été suspendue après deux observations de Thomas : un plateau de 1 mm rendait introuvable un plan pourtant inférieur de 6,8 mm à la hauteur utile, et le budget de calcul ne rafraîchissait pas toujours sa durée adjacente.

## Décision appliquée

- conserver ADR-0088 sans nouvelle décision d’architecture ;
- résoudre le plan minimal SCIP puis appliquer une compensation Z exacte, bornée et recertifiée au seul conteneur admissible sous la réservation ;
- garder le modèle couplé comme repli dans la deadline restante ;
- redessiner immédiatement les réglages de calcul avant leur persistance asynchrone ;
- distinguer le paquet correctif par la version 0.1.65.

## Résultat automatisé

Le cas local exact repasse en `solution_found` avec 18 placements, sommet à 59,6 mm, plan certifié et matérialisable. Le contrôle natif CPython 3.14 passe. Le dry-run du préparateur 0.1.65 passe sans écrire dans AppData.

Le commit `2dbc272` est publié sur `origin/main`, puis le préparateur réel installe 0.1.65 avec runtime, fixtures, réglages et marqueurs correctifs vérifiés. Aucun snapshot local, benchmark, holdout, recalibrage physique ou fait impression n’est ajouté. La correction reste à observer dans Fusion avant acceptation de P64-L09R-V.

## Référence

Voir `docs/P64_L09R_V_CORRECTIVE_0165_EVIDENCE.md` et la recette `docs/P64_L09R_V_FUSION_GATE_RECIPE.md`.