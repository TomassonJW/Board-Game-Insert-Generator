# 2026-07-28 — P64-L09U-R7 — KO humain et diagnostic initial

## Décision

La candidate Fusion 0.1.77 est classée `human-KO`, `do-not-run`.

La profondeur correcte des cavités, les micro-chevauchements et les accès
sous/hors plateau sont conservés comme acquis humains. Le statut global reste
`fusion-validated=false`, `print-validated=false`.

## Faits

- Le placement automatique peut laisser environ `0,4 mm` de matière au lieu du
  minimum canonique `1,2 mm`.
- `CasLimite02++` empile le grand plateau sous le petit livret à cause du
  `stack_order` historique.
- Le plan automatisé annonce néanmoins calcul, finalisation, CAD IR et
  matérialisation réussis.
- Des micro-coupes de prise de `0,5 mm` de large et `6 mm` de profondeur sont
  déjà présentes avant Fusion.
- Des dimensions dérivées au centième restent publiées malgré la nouvelle
  résolution produit `0,1 mm`.

## Première divergence

Le plan minimal des réservations est la première couche fautive :

- son score pénalise les recouvrements utiles ;
- son certificat de paroi ne couvre que les cavités ;
- son ordre vertical obéit d'abord à l'ancien `stack_order`.

La finalisation, la CAD IR et le plan Fusion propagent ensuite ce contrat
incomplet.

## Preuves

- `docs/P64_L09U_R6_V_0177_HUMAN_KO_EVIDENCE.md`
- `docs/P64_L09U_R7_END_TO_END_RUNBOOK.md`

Les SHA-256 des deux projets personnels sont restés identiques avant et après
les replays en lecture seule.

## Suite

R7-B formalise par ADR le placement, les enveloppes finales, l'ordre
automatique, la compatibilité historique et la grille produit `0,1 mm`.
