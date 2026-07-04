# Asset Model Strategy

## Objectif

Le produit cible est asset-first : l'utilisateur doit pouvoir decrire le materiel
reel a ranger avant ou a la place de modules manuels. Le moteur pourra ensuite
proposer des modules, cavites et reservations.

## Etat actuel

- Le JSON V0 decrit surtout des modules demandes.
- `functional_type` distingue cartes, cartes sleevees, tokens, meeples, des,
  free et other.
- Les cavites peuvent representer des receptacles simples, mais aucun modele
  d'asset autonome n'existe encore.

## Concepts cibles

- `Asset` : element ou groupe a ranger, avec dimensions exactes ou approximees.
- `AssetQuantity` : quantite, pile, deck, sac, set ou groupe.
- `ContainmentIntent` : ranger, caler, separer, rendre accessible, exposer.
- `ReservationAsset` : board, livret, regle, plateau ou composant non imprime.
- `DerivedModuleRequest` : module propose depuis des assets, distinct d'un module manuel.

## Invariants

- Un asset n'est pas un module imprimable.
- Un module est une proposition de contenant ou de support pour un ou plusieurs assets.
- Les dimensions approximatives doivent rester signalees dans les rapports.
- Les assets ne doivent pas introduire de dependance SaaS ou IA obligatoire.

## Prochaines missions possibles

1. `P9-M001 - Specifier le schema asset-first` : docs + exemples non executes.
2. `P9-M002 - Charger des assets JSON sans generation de modules` : moteur pur.
3. `P9-M003 - Generer des demandes de cavites depuis assets simples` : gate si schema public change.

## Gates

- Gate architecture si le schema JSON public devient incompatible.
- Gate ergonomique humaine avant de declarer les assets faciles pour non-experts.
