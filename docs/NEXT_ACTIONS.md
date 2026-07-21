# Next Actions

Dernière mise à jour : 2026-07-22

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` pour son périmètre
historique et `print-validated: false`. La surface MVP reste exclusivement
l’add-in Fusion 360.

P64-L03R-B et P64-L03R-C sont `automated-validated`. L’observation exploratoire
du package 0.1.57 confirme une forte amélioration du plan minimal, mais ne
constitue pas le retour formel `P64-L03R-V Fusion OK`. Elle a révélé trois
suites distinctes, formalisées par ADR-0075 et le contrat P64-L04 :

- réutiliser localement une enveloppe déjà placée ;
- rendre Approfondi anytime, borné et jamais moins utile que l’incumbent Normal ;
- rendre visibles les opérations longues sans faux pourcentage.

P64-L04A est `implemented-core`, `implemented-fusion-bridge`,
`implemented-fusion-ui` et `automated-validated` dans le package 0.1.58.
`fusion-validated: false`, `print-validated: false`.

## Dernier état réel

- une édition continue de recalculer uniquement ses dérivations locales ;
- si le conteneur modifié peut être recertifié dans l’enveloppe exacte déjà
  placée, un nouveau `minimal_layout` devient courant sans recherche globale ;
- les poses monde, orientations, dimensions extérieures et corps restent
  identiques ; les cavités existantes sont conservées lorsque possible ;
- un fallback peut choisir une variante locale déjà certifiée de même enveloppe,
  sans déplacer le conteneur ;
- un échec laisse l’ancien aperçu obsolète et demande explicitement
  `Calculer l’agencement minimal` ;
- toute CAD IR ou scène précédente devient désynchronisée ; aucune scène n’est
  modifiée automatiquement ;
- la palette expose le succès local, le fallback global requis, le producteur,
  les caps et les compteurs dans des détails repliés ;
- Approfondi garde les lenteurs et régressions observées : L04A ne les masque
  pas et ne modifie aucun budget de solveur ;
- l’indication d’attente pendant calcul et matérialisation reste absente ;
- le cas dense 11 × 34 reste `no_solution_within_budget`.

## Prochaine action recommandée

### P64-L04B — Approfondi anytime, incumbent Normal et deadline stricte

Objectif : rendre l’effort Approfondi utile sans perdre une solution déjà
certifiée par le préfixe Normal et sans timeout interminable.

Avant code, préciser le contrat de budget et d’arrêt, puis implémenter un lot
borné qui garantit :

1. Rapide reste préfixe de Normal et Normal préfixe d’Approfondi ;
2. le meilleur plan Normal certifié devient l’incumbent initial ;
3. chaque lane Deep améliore ou conserve cet incumbent ;
4. une deadline stricte et un arrêt coopératif conservent le meilleur résultat ;
5. un timeout Deep ne transforme jamais une solution Normal en
   `no_solution_within_budget` ;
6. budgets, temps, lanes tentées, incumbent et raison d’arrêt restent
   observables ;
7. aucun changement de schéma, valeur physique, finalisation ou scène ;
8. le cas dense ne reçoit aucune nouvelle revendication sans certificat.

Autorité :
`docs/DECISIONS/ADR-0075-pre-final-local-layout-reuse.md` et
`docs/P64_L04_INCREMENTAL_LOCAL_REUSE_CONTRACT.md`.

## Lot suivant déjà consigné

### P64-L04C — Attente et progression UX honnêtes

Après L04B, ajouter une activité immédiate pour analyse, calcul, finalisation et
matérialisation, avec étape courante et temps écoulé. Ne pas inventer de
pourcentage. Bloquer les doubles lancements ; n’exposer Annuler que pour les
opérations réellement coopératives.

## Gate humaine différée

### P64-L04V — Parcours incrémental et opérations longues

La prochaine revue Fusion est regroupée après L04B et L04C. Elle devra observer
le plan minimal, l’insertion locale sans mouvement monde ni solve global, le
fallback explicite, la scène désynchronisée puis remplacée sans doublon, et le
retour d’activité des opérations longues.

Le retour formel futur sera défini par le préparateur L04V. D’ici là, ne
revendiquer ni `fusion-validated` pour P64-L04, ni impression réelle.

## Lots verrouillés

- P64-F01A02 et F02A02 restent séparés : ils possèdent la finalisation du volume ;
- P64-C01/C02 restent post-finalisation et ne doivent pas absorber L04A ;
- P45 conserve formes, intentions et certificat local ;
- P46, P47-P50, P67-P69 et les valeurs physiques restent hors scope ;
- aucune résolution du cas dense n’est implicite.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans `main` lorsqu’aucune vraie gate humaine n’est active.
Une gate Fusion ne vaut jamais impression.


## Repères historiques conservés

- `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0` ;
- P44-M007 a livré le package `0.1.37` ;
- `P64-H01 Fusion OK 0.1.42 - commit 5865645` ;
- P44-VH02 reste un retour contextuel supersédé, sans promotion
  `fusion-validated` ;
- `P64-V2H03V Fusion OK 0.1.55` ;
- `P44-V Fusion OK 0.1.55 - commit 70d45c6`.
