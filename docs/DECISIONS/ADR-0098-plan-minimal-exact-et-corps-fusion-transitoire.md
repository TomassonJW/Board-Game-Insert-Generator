# ADR-0098 — Plan minimal exact et corps Fusion transitoire

## Statut

Acceptée par la demande corrective de Thomas le 2026-07-27.

Cette décision prépare une nouvelle gate Fusion. Elle ne vaut ni validation
Fusion, ni validation d'impression.

## Contexte

La gate humaine de 0.1.72 montre quatre divergences liées :

- le plan final affiché et la scène Fusion ne correspondent pas ;
- des cavités hautes paraissent déplacées, agrandies ou approfondies ;
- une fermeture sans plateau s'arrête sur un résiduel non attribué ;
- la matérialisation peut devenir très longue puis échouer sur
  `Combine1 / ALL_TOOL_BODY_REFERENCE_LOST`.

Le diagnostic hors Fusion établit que :

- la finalisation pouvait choisir automatiquement un autre plan minimal
  certifié que celui sélectionné ;
- l'aperçu réduisait un corps composite à son rectangle englobant et
  recalculait les cavités avec un ancien repère ;
- certaines cellules de jeu externe en Z étaient prises pour du volume
  imprimable, tandis qu'une annexe pouvait couvrir plusieurs cellules sans
  toutes les retirer ;
- les centaines d'opérations logiques du CAD IR devenaient des outils
  persistés puis des features Combine dépendantes de leurs références.

## Options

### Option A — Tolérer un minimum alternatif et corriger seulement l'affichage

Cette option laisse le résultat final changer silencieusement de disposition.
Elle ne résout ni l'identité des cavités ni la fragilité Fusion.

### Option B — Conserver les Combine et tenter de réparer leurs références

Cette option maintient une longue chaîne paramétrique et reste exposée à la
perte de corps-outils pendant la construction ou la recomputation.

### Option C — Figer le minimum exact et persister un corps booléenné complet

Cette option garde le cœur et le CAD IR comme autorités, mais rend l'identité
du plan explicite et compacte l'exécution physique Fusion en un corps par
module.

## Décision

Retenir l'option C.

### 1. Le plan final part du minimum sélectionné

La finalisation :

- reçoit un seul candidat, le plan minimal courant ;
- conserve son digest, ses placements et ses cavités gelées ;
- n'essaie aucun minimum alternatif automatiquement ;
- échoue explicitement si ce plan exact ne peut pas être certifié.

Une future sélection de variantes reste une décision utilisateur distincte
sous ADR-0096.

### 2. L'aperçu utilise la géométrie composite réelle

Chaque propriétaire est projeté à partir de ses prismes `cad_origin_mm` et
`cad_size_mm`. Les cavités utilisent leurs poses monde gelées. Les volumes
d'accès sont affichés séparément et ne changent pas la cavité calibrée.

### 3. La fermeture préserve tous les jeux externes

Les annexes peuvent absorber plusieurs cellules résiduelles seulement si elles
les couvrent entièrement. Un jeu entre propriétaires reste vide sur X, Y ou Z.
Si une cellule mélange matière imprimable et jonction de jeux, elle est scindée
avant attribution. Le jeu interne entre un propriétaire et son annexe peut être
supprimé ; aucun jeu externe ne l'est.

### 4. Un support tardif peut être inséré sous une pile

Le solveur de piles peut rencontrer un corps plus large après avoir construit
une pile plus étroite. Il peut l'insérer dessous et décaler la pile existante,
à condition de recertifier appuis, jeux, hauteur, réservation et priorité
plancher d'abord.

### 5. Fusion reçoit un corps rectangulaire complet par module

Pour chaque module :

1. créer le cœur comme BRep transitoire ;
2. appliquer toutes les unions rectangulaires sur ce BRep ;
3. appliquer toutes les coupes rectangulaires sur le résultat ;
4. persister une seule fois le corps final dans une BaseFeature ;
5. exécuter ensuite les features spécialisées restantes.

Aucune feature Combine paramétrique n'est créée pour ces unions et coupes.
Le CAD IR conserve séparément chaque opération logique, son identité, ses
mesures et son ordre.

### 6. La réactivité réelle reste une preuve humaine

L'adaptateur rend la main à Fusion entre deux modules afin de permettre le
rafraîchissement de l'application. Cette respiration n'est pas :

- une progression déterminée par commande ;
- une estimation de temps restant ;
- une annulation coopérative.

Ces capacités restent dans ADR-0095 et un lot ultérieur.

## Conséquences

- 0.1.72 est `human-KO`, `do-not-run`.
- 0.1.73 devient la candidate corrective.
- Les cavités ne sont ni déplacées ni redimensionnées après gel.
- Les valeurs physiques canoniques restent inchangées.
- Une géométrie rectangulaire Fusion plus compacte remplace la chronologie
  Combine, mais doit encore être observée dans Fusion réel.
- `fusion-validated=false`, `print-validated=false` jusqu'au verdict humain.

## Alternatives refusées

- Recentrer ou redimensionner les cavités pendant la finition.
- Masquer la divergence de l'aperçu sans corriger l'identité du plan.
- Conserver un minimum alternatif implicite comme optimisation.
- Augmenter silencieusement le budget de finition.
- Transformer plateaux ou livrets en corps de support.
- Déclarer la performance Fusion validée depuis des mocks hors Fusion.
