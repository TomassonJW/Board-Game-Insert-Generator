# 2026-07-31 — P64-L09W-D-Q

Mission : réduire causalement les `bounded_unknown` de C sans modifier la
géométrie validée ni augmenter les budgets.

Décision :

- retenir le repli SCIP sur enveloppes minimales pour les projets sans élément
  plat, après échec des voies internes et rejet exact
  `MINIMAL_ENVELOPE_EXPANDED` ;
- préserver le délai global, les budgets, les dimensions et les certificats ;
- accepter le passage borné vers certifié dans l'évaluateur de performance,
  tout en gardant l'identité produit gelée pour les résultats déjà prêts ;
- ne pas lancer les 400 ouverts : le plafond causal est 348/400, sous 380/400 ;
- conserver le holdout E scellé.

Preuve :
`docs/P64_L09W_D_Q_MINIMUM_ENVELOPE_SCIP_FALLBACK_EVIDENCE.md`.
