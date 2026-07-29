# P64-L09U-R8-E — preuve de la passe d’encastrement soustractive

Date : 2026-07-29.

Statut : `done-automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## But

R8-E applique le modèle produit retenu par ADR-0105 :

```text
corps imprimable avec éléments plats
  = conteneur finalisé sans éléments plats
  - union des encastrements locaux
```

Le conteneur finalisé est une entrée positive immuable. La passe plate ne peut
publier que des volumes négatifs.

## Artefact canonique

Le cœur Python pur publie :

- `bgig.flat_inset_subtraction_plan.v1` ;
- `bgig.flat_inset_subtraction_operation.v1` ;
- `bgig.subtractive_flat_inset_certificate.v1`.

Chaque opération porte :

- `boolean_operation=difference` ;
- `geometry_role=negative_volume` ;
- une attribution `flat_inset` ou `flat_grip` ;
- un propriétaire et un prisme positif cible ;
- un intervalle Z monde exact `[bottom, top]` ;
- `cut_plane_world_z_mm=top` ;
- une origine et une taille sur la grille produit `0,1 mm` ;
- les digests positif du propriétaire et de l’ensemble finalisé.

La grille produit reste `0,1 mm`. L’epsilon numérique reste séparé à
`0,0001 mm` et ne crée aucune nouvelle valeur physique.

## Certificat soustractif

Le certificat impose :

- volume positif attribuable aux éléments plats : `0,0 mm³` ;
- corps positif attribuable aux éléments plats : `0` ;
- union positive attribuable aux éléments plats : `0` ;
- opération positive attribuable aux éléments plats : `0` ;
- nouveau corps imprimable attribuable aux éléments plats : `0` ;
- opération positive après le début de la passe : `0` ;
- digest positif avant = digest positif après ;
- volumes négatifs disjoints et union négative exacte ;
- attribution complète des empreintes demandées.

Le validateur reconstruit l’artefact pur depuis les conteneurs finalisés et les
réservations. Une mutation aval, une union, un corps positif, un décalage
d’intervalle ou une divergence de digest ferme la chaîne sans publier de CAD
IR exécutable.

## Profondeurs locales

Les cellules XY atomiques sont dérivées des frontières des régions locales et
des prises. Pour chaque cellule, les intervalles couvrants doivent être
contigus, non superposés et déclarer exactement le même ensemble de
réservations.

La régression produit prouve les trois profondeurs :

- livret seul : `2 mm` ;
- plateau seul : `4 mm` ;
- recouvrement : `4 + 2 = 6 mm`.

## Une seule histoire jusqu’au BRep

- La finalisation fige d’abord `bgig.finalized_container_geometry.v1`.
- Le plan négatif est construit ensuite et lié au digest positif inchangé.
- La CAD IR reconstruit et valide ce plan, puis consomme ses opérations
  autoritaires. `top_inset_cuts` n’est plus qu’un miroir de compatibilité.
- Le plan Fusion exige la même opération `difference`, la même attribution et
  le même intervalle.
- Pour `[bottom, top]`, Fusion utilise `cut_origin.z=top` et
  `cut_size.z=top-bottom`.
- Le BRep transitoire construit donc exactement l’outil `[bottom, top]` avant
  le booléen `Difference`.

La régression enterrée conserve l’intervalle livret `[54,6 ; 57,6]` et refuse
son ancien déplacement vers le sommet `59,6`. Une seconde preuve BRep vérifie
directement `[63,8 ; 65,8]`, avec centre `64,8 mm` et hauteur `2 mm`.

## Préservations

- Les cavités calibrées et leurs poses restent inchangées.
- Les accès verticaux et la continuité vers les encastrements restent ouverts.
- Les parois et fragments de matière restent recertifiés.
- L’ordre automatique petit-dessous/grand-dessus reste inchangé.
- Les solveurs, lanes, candidats et budgets ne changent pas.
- Le BRep reste transitoire, dans une BaseFeature unique.
- Le rollback Fusion reste inchangé.
- Aucun chantier ADR-0095 à ADR-0097, aucune UI manuelle et aucun benchmark
  n’entrent dans R8-E.

## Vérifications

Compilation Python des modules touchés : `OK`.

Lot ciblé, sans benchmark ni holdout :

- plan soustractif pur ;
- profondeurs locales R3 ;
- finalisation composite et CAD ;
- réservations supérieures ;
- construction CAD IR et aperçu ;
- squelette Fusion ;
- matérialisation BRep ;
- calcul par étapes ;
- gates correctives et release ciblées ;
- durcissement de bout en bout ;
- contrat Fusion composite.

Résultat : `207/207` tests en `25,394 s`.

Tests de pilotage documentaire : `11/11`.

`git diff --check` : `OK`.

Les projets personnels n’ont pas été rejoués pendant R8-E. Leur état de
référence reste :

- `CasLimite02+` :
  `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` ;
- `CasLimite02++` :
  `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743`.

## Limite et suite

R8-E ferme le contrat automatisé de la passe plate, mais ne revendique aucune
nouvelle observation humaine dans Fusion :
`fusion-validated=false`, `print-validated=false`.

R8-F doit maintenant prouver la fidélité complète de l’aperçu à l’exécution,
rejouer les deux projets personnels en lecture seule et consolider les
régressions avant la candidate R8-G.
