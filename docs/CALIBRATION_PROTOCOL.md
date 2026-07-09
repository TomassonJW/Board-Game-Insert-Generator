# Calibration Protocol

## Objectif

Ce protocole decrit comment valider physiquement les valeurs de tolerance par
impression reelle, sans confondre les presets logiciels avec une preuve
materielle.

Il sert a mesurer les jeux principaux avant de modifier des valeurs par defaut,
de recommander un profil d'impression ou de declarer un comportement stable.

## Statut

Statut actuel : `prevu` et `a valider par impression reelle`.

Le moteur Python pur sait calculer et rapporter les tolerances, mais il ne genere
pas encore de coupons imprimables, STL, 3MF ou composants Fusion 360. Les coupons
ci-dessous sont donc une specification de validation, pas un livrable CAD deja
produit par le depot.

## Preconditions

Avant d'executer une calibration physique :

- noter le profil logiciel teste : `default`, `pla_standard`, `petg_standard`,
  `fast_draft`, `fine_detail` ou profil surcharge ;
- noter l'imprimante, le filament, la buse, la hauteur de couche, le slicer et
  les reglages importants ;
- imprimer les coupons dans l'orientation prevue ;
- mesurer avec un pied a coulisse suffisamment precis ;
- garder les fichiers source et les mesures avec la date.

## Coupons a preparer

| Coupon | Mesure cible | Champs concernes | Critere OK indicatif |
| --- | --- | --- | --- |
| Fit box strip | insertion contre une paroi de boite | `peripheral_clearance_mm`, `printer_compensation_mm` | insertion sans forcer, pas de flottement excessif |
| Neighbor gap pair | deux modules adjacents | `module_gap_mm`, `printer_compensation_mm` | separation mesurable, modules manipulables sans coincer |
| Lid height stack | hauteur sous couvercle | `vertical_lid_clearance_mm` | couvercle ferme sans pression sur le module |
| Card pocket gauge | cartes non sleevees | `card_clearance_mm` | insertion/retrait fluide sans bascule excessive |
| Sleeved card pocket gauge | cartes sleevees | `sleeved_card_clearance_mm` | sleeve non comprimee, retrait possible |
| Token tray gauge | tokens carton | `token_clearance_mm` | prise possible, pas de blocage |
| Irregular piece gauge | meeples ou pieces irregulieres | `meeple_clearance_mm` | piece extractible sans forcer |
| Sliding interface gauge | couvercle coulissant futur | `sliding_lid_clearance_mm` | coulissement sans jeu destructeur |
| Hinge/clip gauge | mecanisme futur | `hinge_clearance_mm` | mouvement fonctionnel sans rupture |

Les coupons de couvercle, charniere et clip restent preparatoires tant que ces
mecanismes ne sont pas modelises par le moteur.

## Tableau de resultats

Copier ce tableau pour chaque session de calibration.

| Champ | Profil teste | Valeur logicielle | Mesure observee | Resultat OK/KO | Ajustement propose | Notes |
| --- | --- | ---: | ---: | --- | ---: | --- |
| `peripheral_clearance_mm` |  |  |  |  |  |  |
| `module_gap_mm` |  |  |  |  |  |  |
| `vertical_lid_clearance_mm` |  |  |  |  |  |  |
| `card_clearance_mm` |  |  |  |  |  |  |
| `sleeved_card_clearance_mm` |  |  |  |  |  |  |
| `token_clearance_mm` |  |  |  |  |  |  |
| `meeple_clearance_mm` |  |  |  |  |  |  |
| `sliding_lid_clearance_mm` |  |  |  |  |  |  |
| `hinge_clearance_mm` |  |  |  |  |  |  |
| `printer_compensation_mm` |  |  |  |  |  |  |

## Regles d'interpretation

- Une mesure isolee ne suffit pas a changer une valeur par defaut.
- Une valeur calibree est locale a une imprimante, un filament et des reglages.
- Une recommandation globale demande plusieurs impressions reproductibles.
- Toute modification des valeurs par defaut reste une gate humaine.
- Une validation par code ne remplace pas une validation par impression.

## Sortie attendue d'une session

Une session de calibration exploitable doit produire :

- contexte d'impression complet ;
- profil logiciel et overrides utilises ;
- photos ou notes d'ajustement si disponibles ;
- tableau de mesures rempli ;
- conclusion limitee : `OK local`, `KO`, `a retester`, ou `candidat pour profil`.

## Lien avec les futures gates

Ce protocole prepare les gates suivantes :

- modification des valeurs de tolerance par defaut ;
- premiere impression 3D reelle ;
- premier export STL/3MF ;
- premiere generation Fusion exploitable ;
- passage aux mecanismes de couvercle, charniere ou clip.

## P17 preprint check V0

P17 ajoute un protocole intermediaire avant calibration physique complete : `docs/PREPRINT_CHECK_PROTOCOL.md`. Il part d'un dossier `export_printables`, du manifeste JSON/Markdown et des STL exportes. Le statut reste `print_validated: false` tant qu'aucune impression mesuree n'est documentee.

Exemple de fiche remplissable : `examples/preprint_check_v0.json`.
