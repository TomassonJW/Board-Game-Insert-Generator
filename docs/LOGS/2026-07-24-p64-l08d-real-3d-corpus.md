# 2026-07-24 — P64-L08D corpus adversarial 3D

## Mission

Construire le corpus Gate A réellement 3D avant tout nouvel adaptateur ou run
de solveur externe.

## Résultat

- 40 cas de matrice sur 10 familles, plus une régression BGIG intacte ;
- 40 cas privés scellés avec les trois paliers et un négatif par famille ;
- témoins indépendants recertifiés en X/Y/Z ;
- appuis multiples, hauteurs hétérogènes, réservations basses/hautes, accès,
  fragmentation, variantes, rotations et affectation de contenus contrôlés ;
- source BGIG revue conservée `bounded_unknown`, avec dérivés annoncés ;
- aucun candidat exécuté et holdout toujours fermé.

## Décision

P64-L08D est `automated-validated`. P64-L08E devient la mission suivante. Le
corpus ne constitue pas un résultat de benchmark et ne promeut aucun moteur.

## Preuve

Voir `docs/P64_L08D_REAL_3D_CORPUS_EVIDENCE.md` et
`tests/fixtures/p64_l08d_real_3d_corpus.v1.json`.
