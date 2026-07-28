# P64-L09U-R7-V — preuve humaine KO 0.1.78

Date : 2026-07-28.

Verdict : `human-KO`, `do-not-run`.

`fusion-validated=false`, `print-validated=false`.

## Résumé fidèle

La grille produit `0,1 mm`, le placement annoncé comme canonique et l'ordre
automatique annoncé ne suffisent pas à produire un insert correct dans Fusion.
Les deux cas humains aboutissent à une scène synchronisée, mais les éléments
plats provoquent encore de grandes plaques, des rails ou des appuis qui
recouvrent les conteneurs. Des cavités deviennent inaccessibles ou ne sont pas
creusées comme attendu. La géométrie comporte aussi des encoches parasites et
des surplombs non imprimables.

Le défaut est bloquant et systémique. Il ne doit pas être réduit à un problème
de rendu Fusion ou à un mauvais ordre local de pile.

## Observation A — calcul minimal beaucoup trop long

Journal lu sans écriture :

`C:\Users\janko\Documents\BGIG\projects\dev-action-logs\session-ms4u7ce6-pmfxthpp\events.jsonl`

Pour `CasLimite02+`, la même session montre :

| Effort | Recherche | Verdict |
|---|---:|---|
| Normal | `22 823 ms` | aucune solution certifiée |
| Approfondi intermédiaire | `61 799 ms` | aucune solution certifiée |
| Approfondi maximal | `90 991 ms` | solution trouvée |

Thomas a donc dû changer deux fois de profondeur et attendre environ
`175,6 s` de recherche cumulée avant d'obtenir un résultat utilisable. Le
dernier calcul seul prend environ une minute et demie. L'expérience humaine est
bien celle d'un calcul de près de trois minutes.

Pour `CasLimite02++`, le calcul approfondi maximal trouve une solution après
`87 192 ms`.

Les deux résultats sont incompatibles avec le rôle produit attendu du calcul
minimal : assembler des enveloppes minimales déjà connues dans le volume utile
de la boîte. Le correctif suivant doit d'abord mesurer les phases, les candidats
et les rejets avant de choisir un nouvel algorithme ou un nouveau budget.

## Observation B — plaque ou support ajouté sous les plateaux

Dans `CasLimite02+`, la palette annonce simultanément :

- `Plan final prêt` ;
- `Fusion : scène synchronisée` ;
- `Ajouts automatiques : 0`.

La scène Fusion montre pourtant une grande plaque ou un support sous le plateau,
avec des rails et des ponts minces autour de son empreinte. Cette matière :

- recouvre plusieurs conteneurs ;
- ferme ou gêne l'accès au récipient de cartes situé sous le plateau ;
- crée un grand surplomb non imprimable ;
- ne correspond ni au plan attendu ni à une simple encoche ;
- contredit directement `Ajouts automatiques : 0`.

Captures versionnées :

- `docs/EVIDENCE/P64_L09U_R7_V_0178/caslimite02plus-support-plate-over-cavities-1.png` ;
- `docs/EVIDENCE/P64_L09U_R7_V_0178/caslimite02plus-support-plate-over-cavities-2.png`.

SHA-256 des captures :

- `1D7810AE6F8D9D2F891153AE45A91C4392E2B5CEB7056B2FF066492A20EA4EE4` ;
- `4AB54A15C196BD6C9265F001E45E3E62F0D27D769763402AE3853C9FEDEF730D`.

## Observation C — empilement et cavités toujours faux

Dans `CasLimite02++`, la scène montre encore :

- une grande plaque supérieure couvrant une large partie de l'insert ;
- un long volume ou rail au bord de cette plaque ;
- une cavité qui paraît non creusée ou fermée ;
- des encoches parasites ;
- une composition qui ne raconte pas deux éléments plats uniquement encastrés
  dans des conteneurs déjà finalisés.

Capture versionnée :

`docs/EVIDENCE/P64_L09U_R7_V_0178/caslimite02plusplus-large-plate-and-closed-cavities.png`

SHA-256 :

`2804B142DD8B13FB08674DA1FEB17A3484ED79269256B43514F014F7D86A2C1C`.

## Contradiction de certification

La finalisation et la matérialisation elles-mêmes restent rapides :

| Projet | Finalisation | Matérialisation |
|---|---:|---:|
| `CasLimite02+` | `2 186 ms` | `783 ms` |
| `CasLimite02++` | `2 095 ms` | `815 ms` |

Les deux finalisations publient `finalized_plan_ready` et les deux scènes
publient `scene_synchronized`. Le problème n'est donc pas un arrêt ou une
erreur Fusion : le pipeline certifie et matérialise rapidement un contrat
géométrique humainement faux.

La première divergence exacte entre frontière minimale, finalisation, CAD IR,
plan Fusion et opérations BRep reste à localiser. Il est interdit de corriger
uniquement l'apparence finale.

## Modèle produit reformulé par Thomas

Le comportement recherché est séquentiel et strict :

1. la boîte fournit un volume utile connu ;
2. tous les conteneurs, plateaux et livrets ont une enveloppe minimale déjà
   calculée ;
3. `Calculer` cherche seulement comment assembler ces enveloppes minimales dans
   la boîte ;
4. `Finaliser` étend les conteneurs pour remplir la boîte, tout en réservant
   l'épaisseur future des éléments plats ;
5. à la fin de la finalisation, les corps imprimables sont les conteneurs
   finalisés ; aucun corps de support de plateau n'est ajouté ;
6. une passe postérieure applique les plateaux et livrets uniquement comme des
   soustractions dans les conteneurs concernés ;
7. chaque conteneur sous une empreinte est creusé de l'épaisseur exacte de la
   pile locale : par exemple `4 mm + 2 mm = 6 mm` dans la zone de recouvrement ;
8. les zones couvertes par un seul élément ne sont creusées que de l'épaisseur
   de cet élément ;
9. aucune paroi, plaque, rail, pont, fermeture, support ou volume positif ne
   peut être créé par un plateau ou un livret ;
10. les cavités existantes restent creusées et accessibles : une réservation
    supérieure ne peut jamais les reboucher.

Autrement dit, les éléments plats modifient les corps finalisés par différence
de matière. Ils ne deviennent ni des corps imprimables ni des générateurs de
matière.

## Acquis à préserver

- profondeur correcte des cavités, y compris les micro-chevauchements ;
- accès sous et hors plateau ;
- continuité directe plateau/cavité, sans matière intermédiaire ;
- identités, positions, orientations et profondeurs des cavités figées ;
- parois, fonds et jeux physiques inchangés ;
- grille produit `0,1 mm`, distincte de l'epsilon numérique ;
- BRep transitoire, rendu progressif, rollback global et respiration Fusion ;
- projets personnels strictement en lecture seule.

## Classement

La candidate 0.1.78 est désormais :

- `human-KO` ;
- `do-not-run` ;
- `fusion-validated=false` ;
- `print-validated=false`.

La prochaine mission est P64-L09U-R8. Son hand-off canonique est
`docs/P64_L09U_R8_SUBTRACTIVE_FLAT_INSETS_HANDOFF.md`.
