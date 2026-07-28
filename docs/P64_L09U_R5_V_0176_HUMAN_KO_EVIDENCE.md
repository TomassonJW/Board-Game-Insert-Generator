# P64-L09U-R5-V — preuve humaine KO 0.1.76

Date : 2026-07-28.

Verdict : `human-KO`, `do-not-run`.

`fusion-validated=false`, `print-validated=false`.

## Acquis humains conservés

- Le résultat est globalement beaucoup plus proche de la cible que 0.1.75.
- Les portions de cavité hors plateau ne sont plus recouvertes par des blocs
  solides.
- La plupart des cavités, y compris celles à cheval sous et hors plateau,
  gardent leur profondeur et restent accessibles.
- Calcul, finalisation et matérialisation restent rapides lorsque la
  finalisation trouve un plan.
- Les cavités gardent leur empreinte, leur position, leur orientation et leur
  identité.
- Le chemin BRep transitoire, le rendu progressif et le rollback restent
  acquis.

## Défaut A — micro-chevauchement de cavité

Le défaut est surtout visible dans `CasLimite02+`.

Dans `c4 / Bac cartes quatre`, une cavité d’asset de `10 mm` reste profonde de
`10 mm` dans sa partie hors plateau, mais ne mesure plus que `4,4 mm` dans sa
petite portion sous plateau. Les `6 mm` perdus correspondent exactement au
cumul du plateau `4 mm` et du livret `2 mm`. L’asset serait écrasé.

Le replay instrumenté localise la première divergence avant la CAD IR :

- la cavité chevauche réellement une région réservée sur environ `3,7 mm` ;
- son contrat final reste pourtant `open_top` à `69,8 mm` ;
- le corps imprimable local sous réservation s’arrête à `63,8 mm` ;
- la coupe Fusion ne peut donc retirer que les `4,4 mm` compris entre le fond
  de cavité et ce sommet local.

La profondeur déclarée reste inchangée, mais la profondeur réellement
intersectée avec le corps imprimable est fausse.

## Défaut B — plusieurs éléments plats

Le plateau `110 × 120 × 4 mm` et le livret `60 × 80 × 2 mm` ne produisent pas
un empilement local cohérent :

- `60 × 80 × 2` et `60 × 82 × 2` calculent, puis la finalisation s’arrête très
  tôt sur `xy_composite_residual_owner_not_found` ;
- `60 × 85 × 2` calcule et finalise rapidement, mais le plan de coupe ne
  conserve qu’une réservation responsable par cellule ;
- les régions minimales amont savent pourtant distinguer `4 mm`, `2 mm` et le
  cumul local `6 mm`.

Le replay `60 × 80` montre deux cellules résiduelles de
`0,4 × 0,4 mm`, pour `0,896 mm³` au total. Elles proviennent de la garde Z
conservative, qui applique le cumul des deux éléments à toute l’empreinte du
plateau même lorsque les empreintes sont disjointes.

## Projet personnel

Source lue sans écriture :
`C:\Users\janko\Documents\BGIG\projects\CasLimite02+.bgig.json`.

SHA-256 avant et après les replays `60×80`, `60×82` et `60×85` :

```text
5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC
```

Les variantes `60×82` et `60×85` ont été créées uniquement dans
`.codex-work`, relues avec leur SHA avant/après identique, puis supprimées.

## Suite

P64-L09U-R6 doit :

1. remplacer la garde Z globale conservative par l’union exacte des régions
   XY locales ;
2. conserver chaque intervalle Z d’élément plat jusqu’au plan Fusion ;
3. ancrer une cavité sur tout chevauchement XY réel supérieur à l’epsilon,
   même lorsqu’aucun volume de coupe supérieur n’existe encore ;
4. rejouer les trois dimensions du livret avant une nouvelle candidate.

La candidate 0.1.76 ne doit plus être exécutée.
