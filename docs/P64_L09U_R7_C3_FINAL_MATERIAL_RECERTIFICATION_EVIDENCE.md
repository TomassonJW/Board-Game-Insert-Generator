# P64-L09U-R7-C3 — preuve de recertification de la matière finale

Date : 2026-07-28.

Statut : `automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## Première divergence corrigée

Après C2, `CasLimite02++` ne publiait plus de micro-coupe sous `1,2 mm`, mais
la décomposition composite contenait encore `14` prismes de `0,8 mm`.

La cause était une couture entre :

- le bord réel des conteneurs à `0,4 mm` du bord de boîte ;
- une découpe autorisée à `1,2 mm` du bord de boîte.

La matière restante n'était donc que de `0,8 mm`. Le minimum automatique doit
tenir compte du jeu de boîte puis de la paroi :

```text
marge de découpe au bord = jeu boîte par côté + paroi minimale
                          = 0,4 + 1,2
                          = 1,6 mm
```

Cette correction ne change aucune valeur physique.

## Contrat exécuté

- le solveur reçoit les ancres `bord de matière + paroi minimale` ;
- toute composante de coupe positive sous `1,2 mm` est rejetée ;
- toute bande de matière résiduelle positive sous `1,2 mm` est rejetée ;
- la finalisation recertifie la même pose contre l'enveloppe composite finale ;
- un échec bloque la finalisation, sans déplacement silencieux ;
- un corps trop bas pour rencontrer une coupe supérieure n'est plus découpé en
  prismes artificiels par les coutures XY de cette coupe ;
- le certificat est propagé dans la CAD IR puis dans le plan Fusion.

## Régressions automatisées

Les tests ajoutés prouvent :

- rejet explicite d'une bande résiduelle de `0,8 mm` ;
- absence de découpage d'un corps inférieur hors intervalle Z ;
- propagation du certificat final jusqu'au plan Fusion ;
- rejet explicite d'une composante de coupe de `0,5 mm` ;
- conservation des cavités calibrées, micro-chevauchements et accès R6.

Résultat ciblé :

```text
Ran 66 tests in 17.998s
OK
```

## Replays personnels en lecture seule

### CasLimite02++

- SHA-256 avant/après :
  `83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743`
- pose :
  `board@0° x=43,9 y=6,1`,
  `booklet@90° x=41,9 y=11,1`.
- certificat final : réussi, `0` échec.
- prismes composites : `118` avant C3, `56` après C3.
- prismes sous `1,2 mm` : `14` avant C3, `0` après C3.
- coupes supérieures CAD IR : `45` avant C3, `18` après C3.
- coupes supérieures sous `1,2 mm` : `0`.
- certificat reçu par le plan Fusion : oui.

### CasLimite02+

- SHA-256 avant/après :
  `5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc`
- pose :
  `board@0° x=63,9 y=11,1`,
  `booklet@90° x=93,9 y=24,6`.
- certificat final : réussi, `0` échec.
- prismes composites : `59`; prismes sous `1,2 mm` : `0`.
- coupes supérieures CAD IR : `14`; coupes sous `1,2 mm` : `0`.
- certificat reçu par le plan Fusion : oui.

Ces mesures sont des compteurs de replay, pas un benchmark.

## Limite restante

L'ordre automatique de pile reste historique dans C3. Le lot R7-D doit imposer
petit-dessous/grand-dessus et vérifier les intervalles Z, l'aperçu, la CAD IR
et le plan Fusion.
