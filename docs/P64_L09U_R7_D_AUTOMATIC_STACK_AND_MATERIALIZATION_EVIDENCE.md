# P64-L09U-R7-D — preuve d'empilement automatique exact

Date : 2026-07-28.

Statut : `automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## Règle appliquée

L'ordre automatique est calculé du bas vers le haut à partir de l'empreinte
orientée avec jeu :

1. aire croissante ;
2. grand côté croissant ;
3. petit côté croissant ;
4. épaisseur totale croissante ;
5. type puis identifiant stables.

Le `stack_order` historique est conservé dans `source_stack_order`, mais il ne
pilote plus silencieusement l'automatisme. La sortie publie :

- `stack_order` automatique ;
- `source_stack_order` ;
- `automatic_stack_key_v1` ;
- `stack_order_migration` ;
- `manual_stack_mode_implemented=false`.

Le futur mode manuel reste possible par un mode explicite distinct. Il n'est
pas implémenté dans R7.

## Cas forcé anonymisé

Régression publique :

- grand plateau `140 × 160 × 4 mm`, source `stack_order=0`, rotation `0°` ;
- petit livret `110 × 155 × 2 mm`, source `stack_order=1`, rotation `90°` ;
- boîte `240 × 180 × 70 mm`, hauteur utile `69,8 mm`.

Résultat automatique :

```text
bas : livret, aire orientée avec jeu 17 369,44 mm²
haut : plateau, aire orientée avec jeu 22 761,44 mm²
```

Dans la zone de recouvrement :

```text
livret : Z [63,8 ; 65,8] mm
plateau : Z [65,8 ; 69,8] mm
```

Ces intervalles exacts portent les mêmes identifiants dans le plan minimal, la
CAD IR et le plan Fusion. Hors recouvrement, chaque élément conserve son propre
intervalle local ; aucune profondeur globale artificielle n'est appliquée.

## Replays personnels en lecture seule

### CasLimite02++

- SHA-256 avant/après :
  `83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743`
- ordre source : plateau `0`, livret `1`.
- ordre automatique bas-vers-haut : livret `0`, plateau `1`.
- migration des deux entrées : `legacy_overridden_by_automatic`.
- intervalle de recouvrement livret : `[63,8 ; 65,8] mm`.
- intervalle de recouvrement plateau : `[65,8 ; 69,8] mm`.
- certificat final de matière : réussi.
- volume additif résiduel au-dessus des corps finaux : `0 mm³`.
- certificat reçu par le plan Fusion : oui.

### CasLimite02+

- SHA-256 avant/après :
  `5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc`
- replay complet réussi avec le même contrat automatique.
- volume additif résiduel au-dessus des corps finaux : `0 mm³`.

## Validation

```text
Ran 75 tests in 17.661s
OK
```

Les tests couvrent l'ordre forcé, la migration du champ historique, les paliers
locaux, les cavités R6, la CAD IR, le plan Fusion et l'absence de volume additif
résiduel.

La scène Fusion réelle reste une gate humaine.
