# P64-L09W-D-T — rejeu minimal tardif avec éléments plats rejeté

Date : 2026-07-31.

Statut : `increment-rejected`, `performance-hard-stop`,
`no-product-change-retained`, `holdout-sealed`.

## Résultat

Le troisième levier causal testé n'est pas retenu.

Il étendait aux projets avec éléments plats le rejeu SCIP D-Q sur enveloppes
minimales. Le rejeu restait strictement tardif : seulement après l'échec des
voies existantes et un rejet exact `MINIMAL_ENVELOPE_EXPANDED`, sous le même
délai global et sans budget ajouté.

Une sonde sur trois cas publics `common` confirme le mécanisme, mais le panel
sentinelle atteint une régression de temps dure à `15/16`. Le code candidat et
son test sont retirés. Le panel 48 et les 400 ouverts ne sont pas exécutés.

## Attribution causale

Après D-Q, le résiduel contient 24 cas `common` avec élément plat :

- 21 rejets SCIP `MINIMAL_ENVELOPE_EXPANDED` ;
- 3 rejets SCIP `TOP_INSET_AUTOMATIC_PLACEMENT_NOT_FOUND`.

D-T ciblait uniquement les 21 premiers. Le changement ne modifiait ni la
projection minimale, ni la certification commune, ni l'ordre des voies. Il
retirait seulement l'exclusion générale des projets avec éléments plats dans
la gate tardive déjà introduite par D-Q.

## Sonde causale

Trois cas publics bornés de C ont été exécutés une fois avec le candidat :

- `p64-l09w-discovery-021-1396347efa` :
  `bounded_unknown -> certified_solution`, calcul `1 532,788 ms`,
  finalisation et CAD IR prêtes ;
- `p64-l09w-discovery-027-2355a8af2f` :
  `bounded_unknown -> certified_solution`, calcul `8 495,436 ms`,
  finalisation toujours bornée ;
- `p64-l09w-discovery-045-c34db41e9d` :
  `bounded_unknown -> certified_solution`, calcul `1 892,546 ms`,
  finalisation toujours bornée.

Les médianes C à deux replays valaient respectivement `2 525,850 ms`,
`5 392,860 ms` et `2 868,566 ms`. La sonde établit un gain de certification,
pas un taux ni une promesse de performance globale.

## Tests ciblés

Avant la campagne :

- solveur minimal : `23/23`, OK ;
- solveur minimal, réservations supérieures, runner et seuils : `60/60`, OK.

Le test d'ordre prouvait que le rejeu minimum ne commençait qu'après la
projection sans élément plat, le passage courant SCIP et les voies internes.

## Arrêt sentinelle

Le checkpoint candidat atteint `15/16` :

- 15 gates fonctionnelles vertes ;
- zéro faux impossible ;
- zéro résultat prêt perdu ;
- zéro identité produit ou placement prêt modifié ;
- `tuning-388` reste `bounded_unknown`, médiane `22 554,134 ms`, sous sa
  limite `23 070,369 ms` ;
- `tuning-384` conserve son produit et son placement, mais mesure une médiane
  `28 782,506 ms` contre une limite gelée `28 699,258 ms`.

L'écart dur vaut `83,248 ms`, soit environ `0,290 %`. La voie D-T n'est pas
invoquée sur `tuning-384` (`external_invocation_count=0`) : cette observation
ne démontre pas que D-T cause l'écart. Le contrat impose néanmoins le rejet dès
qu'une borne gelée est franchie ; aucun rejeu opportuniste n'est autorisé.

La dernière sentinelle,
`p64-l09w-tuning-300-cf933fb090`, n'est volontairement pas exécutée.

Bindings locaux :

- bundle candidat :
  `54a4f0f706034a37c50f3e0d463db86cd447c0194f11ac724230214a082a4cf5` ;
- checkpoint `15/16` :
  `a3aaf4916136d8c7aacf732268edce1c66305ac2bb120958c697a4cc7cef9450` ;
- rapport partiel `15/16` :
  `aa26c12c935d2d78474e456c61ae6274f1c455a9936198a28ee3a1e7391ef38d`.

Le premier appel terminal a atteint son timeout externe à `654 s` alors que le
Python Fusion restait vivant. Aucun calcul n'a été relancé : le checkpoint a
été observé à `12` cas avec `tuning-388` actif, puis à `13` cas sans cas actif.
La reprise a chargé ces 13 résultats et exécuté uniquement les trois cas
restants jusqu'à l'arrêt de performance. Cette coupure appartient à la couche
terminal, pas au dépôt ni au verdict fonctionnel.

## Décision

D-T est rejetée et retirée. Aucun comportement produit, budget, certificat,
placement, valeur physique, finalisation ou CAD n'est conservé.

Le panel 48 et les 400 ouverts ne sont pas exécutés. E reste bloquée au plafond
causal retenu de D-Q, `348/400`, sous `380/400`.

La prochaine mission atomique doit mesurer un autre sous-groupe, en priorité
les neuf cas `stress` dont le témoin projeté est refusé, puis choisir un seul
code de rejet causal. Elle ne doit réintroduire ni le cache D-S ni l'extension
générale D-T.

## Holdout

Le holdout n'a été ni lu, ni ouvert, ni invoqué :

- `holdout_file_read=false` ;
- `opening_count=0` ;
- `solver_invocation_count=0`.

Aucune validation Fusion ou impression nouvelle n'est revendiquée.
