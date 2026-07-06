# ADR-0022 - Fusion command UI and explicit asset sizing

## Statut

Accepte pour implementation, validation Fusion manuelle requise.

## Date

2026-07-07

## Carte liee

- `P11-M003 - Corriger le sizing asset-first et ajouter une commande UI Fusion minimale`

## Contexte

Les smoke tests P11-M001/P11-M002 ont montre que la chaine Fusion fonctionne pour
les modules asset-first et multi-layer, mais l'experience restait trop
orientee developpeur : generation CAD IR en PowerShell, copie ou edition de
`cad_ir_path.txt`, puis edition de `exploded_view_mode.txt` pour changer de mode.

Le smoke test P11-M002V a aussi revele une ambiguite dimensionnelle : certains
modules Fusion semblaient utiliser des dimensions imprimees/tolerancees, tandis
que les modules asset-first multi-layer affichaient les spans bruts de grille
(`90 x 90 x 10 mm`, `60 x 60 x 20 mm`) comme bodies. Le produit doit distinguer
clairement occupation de grille, enveloppe asset-fit et corps imprimable.

## Options

1. Garder les fichiers texte locaux comme interface principale.
2. Ajouter une UI Fusion minimale avec champ chemin et choix de mode, tout en
   gardant les fichiers texte comme valeurs par defaut.
3. Construire une UI produit complete dans Fusion pour charger et modifier les
   configs BGIG.

## Decision

Retenir l'option 2.

L'add-in enregistre une commande Fusion `Generate Board Game Insert` qui expose :

- `CAD IR JSON path` comme champ texte ;
- `Generation mode` comme choix `compact_only` / `compact_and_exploded` ;
- un resume rappelant que Fusion consomme la CAD IR sans recalculer layout,
  clearances ou tolerances.

Les fichiers `cad_ir_path.txt` et `exploded_view_mode.txt` restent supportes
comme valeurs par defaut heritees, mais ne sont plus le flux utilisateur normal.

Pour les placements asset-first, `size_mm` devient l'alias de la taille de corps
imprimable generee. Les spans de grille sont transportes separement par
`theoretical_grid_origin_mm` et `theoretical_grid_extent_mm`. Fusion doit creer
la geometrie depuis `printable_body_origin_mm` / `printable_body_size_mm` quand
ces champs sont presents.

## Consequences

Effets positifs :

- le flux Fusion devient utilisable sans edition manuelle de fichiers texte ;
- les dimensions observees dans Fusion correspondent au corps imprimable genere,
  pas a la reservation de grille ;
- les rapports Markdown/JSON rendent l'ecart grille / asset-fit / printable
  visible ;
- l'extension reste additive pour la CAD IR V0.

Risques et limites :

- la commande UI doit etre smoke-testee dans Fusion ; les tests automatises ne
  couvrent que les helpers hors Fusion et la presence du code de commande ;
- les anciens smoke tests qui attendaient `30 x 30 x 10 mm`, `90 x 90 x 10 mm`
  ou `60 x 60 x 20 mm` comme tailles de bodies asset-first doivent etre relus :
  ces valeurs representent maintenant des spans de grille ;
- les clearances peripheriques et inter-modules par face ne sont pas encore
  appliquees au plan asset-first genere ; elles restent explicites a `0.0` dans
  `clearance_applied` pour eviter une fausse promesse.

## Alternatives refusees

Laisser les fichiers texte comme interface principale est refuse : c'est utile
pour debug, mais trop fragile pour la premiere experience utilisateur.

Construire une UI complete de configuration BGIG dans Fusion est refuse : cela
melangerait moteur produit et adaptateur CAD, et depasserait le perimetre de la
mission.

## Suivi

- Smoke test humain `P11-M003V` requis dans Fusion.
- Nouvelle gate avant UI produit plus complete, solveur plus automatique,
  modules composites, geometres courbes, fillets ou exports STL/3MF.
