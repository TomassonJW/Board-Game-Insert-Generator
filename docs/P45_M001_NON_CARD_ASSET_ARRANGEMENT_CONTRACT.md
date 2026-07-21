# P45-M001 — Disposition locale et interface unifiée des piles d'assets

Statut : accepté par décision humaine P45-M001V le 2026-07-21, avec le
composant unifié Pile / Basculer. Aucun runtime, schéma ou comportement
public n'est modifié par ce contrat.

ADR : [ADR-0073](DECISIONS/ADR-0073-locked-asset-pose-and-local-arrangement-intents.md).

Capability principale : `C-GEOMETRY`. Capabilities associées : `C-ASSET`,
`C-USABILITY`, `C-QUALITY`. P64 reste propriétaire de `C-SOLVER` et
`C-LAYOUT` au niveau boîte.

## 1. Résultat produit attendu

Une personne choisit comment les occurrences d'un asset non-carte peuvent être
rangées dans leur conteneur sans autoriser le moteur à renverser implicitement
l'objet. P45 produit ensuite une frontière bornée de dispositions locales
certifiables ; P64 choisit une disposition locale et un placement global.

Le contrat ne promet ni optimum mathématique, ni solution globale, ni ergonomie
physique validée. Un volume positif reste insuffisant pour conclure qu'une
disposition existe.

## 2. Vocabulaire normatif

- `AssetPose` : correspondance entre les axes physiques mesurés de l'asset et
  les axes locaux X/Y/Z de rangement. Elle détermine notamment quel axe reste
  vertical.
- `ArrangementIntent` : préférence fonctionnelle pour répartir les occurrences
  d'un même asset dans le repère local du conteneur.
- `AssetOccurrence` : une unité comptée, sans nouvelle mesure physique.
- `LocalArrangementCandidate` : disposition complète et immuable d'occurrences
  et de cavités dans une enveloppe minimale locale.
- `LocalArrangementCertificate` : preuve logicielle locale, distincte du
  certificat global P64.

La pose et la disposition sont orthogonales. Empiler des occurrences sur Z ne
change jamais leur pose.

## 3. Verrou absolu de pose et de Z

1. P45 ne permute jamais X ou Y avec Z pendant une recherche automatique.
2. Une rotation automatique de 90° autour de Z peut échanger X et Y seulement
   si la pose résolue l'autorise.
3. Changer l'axe physique vertical exige une action utilisateur explicite sur
   la pose de rangement ; cette décision précède toute analyse locale.
4. `vertical_stack_z_v1` déplace des occurrences le long de Z mais conserve
   leurs dimensions orientées et leur axe vertical.
5. P64 peut tourner un conteneur complet de 90° dans le plan XY. Il ne peut ni
   renverser une cavité, ni réinterpréter la pose d'un asset.

Les orientations P62 déjà résolues pour les cartes restent inchangées. Le futur
contrôle de pose des assets non-cartes devra être additif, explicite et soumis à
sa propre compatibilité ; P45-M001 n'ajoute aucun champ au projet.

## 4. Intentions de disposition

### `auto_balanced_v1` — Automatique équilibrée

- génère plusieurs candidats locaux bornés : grille, lignes, étagères et piles
  compatibles avec la pose verrouillée ;
- conserve le candidat canonique historique en premier ;
- privilégie après contraintes dures une enveloppe compacte, un aspect XY
  modéré et une hauteur raisonnable ;
- peut répartir la quantité entre plusieurs piles XY ;
- ne transforme jamais la recommandation locale en choix global définitif.

La cible « Z proche de la moitié ou des deux tiers de X » est une intuition de
forme, pas une contrainte universelle. Elle peut seulement contribuer à une
métrique d'aspect explicitée lorsque les dimensions sont comparables.

### `linear_xy_v1` — En ligne

- place toutes les occurrences sur un seul niveau Z ;
- conserve une ligne locale canonique ; l'orientation monde X ou Y est choisie
  ensuite par la rotation globale XY de P64 ;
- n'empile aucune occurrence et échoue honnêtement si la ligne ne tient dans
  aucune orientation XY autorisée ;
- ne crée pas deux variantes locales qui ne diffèrent que par la rotation
  globale de 90° du conteneur.

### `vertical_stack_z_v1` — Empilé verticalement

- conserve la pose physique verrouillée et superpose les occurrences le long
  de Z ;
- utilise une seule pile par défaut ; une limite de hauteur ou un nombre de
  piles futur doit être explicite, jamais déduit silencieusement en changeant de
  mode ;
- échoue localement si quantité, jeux, accès ou hauteur admissible rendent la
  pile invalide ;
- ne bascule pas automatiquement vers `auto_balanced_v1` ou `linear_xy_v1`.

Les libellés utilisateur évitent « colonne », ambigu entre Y et Z :
`Automatique`, `En ligne`, `Empilé verticalement`.

## 5. Quantité, cavités et cloisons

Chaque candidat couvre exactement le multiensemble demandé. Une implémentation
future peut modéliser une cavité agrégée ou plusieurs sous-cavités si leur
équivalence fonctionnelle est certifiée, mais elle ne peut ni perdre ni inventer
des occurrences.

Le comportement actuel reste normatif au premier incrément runtime futur :

- jeu asset-cavité issu d'ADR-0063 ;
- jeux externes des conteneurs globaux selon ADR-0064 ;
- `layout.default_wall_thickness_mm` puis override
  `container_groups[].wall_thickness_mm` ;
- même minimum pour parois extérieures et cloisons internes ;
- aucun nouveau paramètre de cloison avant contrat additif et preuve physique.

## 6. Frontière locale produite par P45

Pour chaque asset et conteneur touchés, P45 produit zéro ou plusieurs candidats :

```text
SemanticLocalArrangementCandidate
  container_group_id
  source_asset_id
  intent_id + intent_version
  resolved_pose_id + pose_digest
  occurrence_count
  geometry_digest
  minimum_outer_envelope_mm
  cavity_layout
  wall_thickness_mm + floor_thickness_mm
  local_metrics
  provenance
  local_certificate
```

Les candidats s'adaptent à `ContainerInternalVariant` d'ADR-0070. P64 ne lit
pas `intent_id` pour inventer une règle ; il consomme uniquement géométrie,
coûts déclarés, provenance et certificat.

Une même géométrie issue de plusieurs producteurs est dédupliquée par digest et
conserve tous ses alias. Une rotation globale XY ne crée pas un nouveau digest
local. Les miroirs restent distincts sauf équivalence sémantique certifiée.

## 7. Certificat local P45

Le certificat est fail-closed et vérifie au minimum :

- pose résolue identique pour toutes les occurrences ;
- aucune permutation X/Y vers Z non autorisée ;
- couverture exacte de la quantité ;
- dimensions, jeux et formes résolues inchangés ;
- cavités contenues et non superposées ;
- parois, cloisons et fond conformes aux minima hérités ;
- contraintes propres à l'intention respectées ;
- repère local, digest et provenance cohérents ;
- absence de corps, cale, séparateur ou réservation inventés.

Il ne certifie pas boîte, réservations supérieures, support, retrait global,
résiduel, stabilité réelle, imprimabilité ou confort de prise.

## 8. Contraintes dures avant score

Un candidat est rejeté avant tout classement si l'une des conditions suivantes
échoue : pose, quantité, dimension finie positive, jeux, parois, fond,
non-recouvrement, intention demandée ou axes Fixe du conteneur.

Les limites de boîte et réservations peuvent annoter un candidat comme
`compatible`, `conditional`, `incompatible` ou `unknown`, mais le certificat
global reste autoritaire. `unknown` ne signifie jamais compatible.

## 9. Métriques locales explicables

Le vecteur minimal contient séparément :

- volume et aire de l'enveloppe minimale ;
- efficacité cavités/enveloppe ;
- pénalité d'aspect XY ;
- hauteur ;
- nombre de piles, rangées et cloisons ;
- compatibilité connue par axe et réservation ;
- complexité de layout.

Ces métriques servent au Pareto, à la diversité et à l'ordre d'expansion. Elles
ne prouvent ni ergonomie, ni matière réellement consommée, ni qualité
d'impression. Un éventuel score UI est une projection décomposée, jamais une
valeur magique ni une limite moteur au top 3.

## 10. Responsabilité P64 inchangée

P64 conserve : voie canonique, EMS historique, greedy, beam, profils d'effort,
budgets monotones, progressive widening, sélection globale et certificat du
plan complet. Il choisit au plus une variante locale certifiée par conteneur.

P64 ne change jamais pose, intention, cavités ou cloisons. Une recherche épuisée
reste `no_solution_within_budget`; aucune marge volumique positive ne devient
une promesse de placement.

## 11. Compatibilité et évolution du schéma

P45-M001 est documentaire : aucun champ n'est ajouté à `bgig.project.v1`.

Une mission runtime future devra proposer une migration additive :

- absence du champ = comportement canonique historique bit-à-bit ;
- intention explicite = nouveau producteur P45 versionné ;
- valeur inconnue = refus explicite, jamais fallback silencieux ;
- export/import/roundtrip préservent le choix ;
- ancien projet non modifié tant que la personne ne choisit rien.

## 12. UX progressive future

Le parcours normal expose au plus un contrôle compact par asset :
`Automatique`, `En ligne`, `Empilé verticalement`. La pose verticale verrouillée
est visible sans diagnostic technique. Toute modification invalide seulement
l'analyse locale concernée selon ADR-0071 ; elle ne lance pas un solve global.

Un détail replié peut montrer candidats, métriques, compatibilités et rejets.
Trois représentants visibles au plus ne limitent jamais la frontière moteur.

## 13. Fixtures obligatoires avant runtime

1. parité d'un projet historique sans intention ;
2. asset asymétrique prouvant l'absence de permutation X/Y vers Z ;
3. ligne tenant seulement après rotation globale XY ;
4. ligne trop longue rejetée sans fallback silencieux ;
5. pile Z valide avec pose inchangée ;
6. pile Z trop haute rejetée ;
7. auto avec plusieurs candidats Pareto, dont le meilleur local crée un
   cul-de-sac global et une alternative permet un plan P64 ;
8. quantité exacte et cloisons héritées ;
9. réservation supérieure annotée localement puis tranchée globalement ;
10. monotonie Rapide/Normal/Approfondi et non-régression dense H03C.

## 14. Découpage après décision

- `P45-M001V` : acceptée le 2026-07-21 avec `Pile` / `Basculer` unifiés ;
- `P64-L01` : états, digests et invalidation, désormais `ready` ;
- futur lot P45 runtime : schéma additif, producteurs sémantiques, certificat et
  fixtures, après contrat de migration ;
- gate Fusion P45 distincte avant P46.

## 15. Acceptation enregistrée

Thomas accepte les principes suivants le 2026-07-21 :

1. pose physique et disposition sont deux choix distincts ;
2. Z ne change jamais sans action explicite de pose ;
3. les trois intentions et leurs absences de fallback silencieux ;
4. le candidat local n'est pas pré-sélectionné avant P64 ;
5. le premier lot suivant est P64-L01, sans UI ni forme P45 runtime.

## 16. Hors scope absolu

- code, UI, schéma ou migration ;
- forme non rectangulaire, encoche, arrondi, chanfrein ou fond ergonomique ;
- recalibration de jeu, paroi, cloison ou fond ;
- changement de solveur, budget, méthode ou résultat dense ;
- cales, séparateurs ou corps automatiques ;
- P46, P47-P50, P64-F01/F02/C01-C03 ;
- scène Fusion ou matérialisation ;
- revendication `fusion-validated` ou `print-validated`.

## 17. Amendement accepté P45-M001V — composant unifié `Pile` / `Basculer`

Cette section est normative et remplace toute formulation antérieure incompatible
sur l'interface de pose. Elle n'ajoute encore aucun champ public ni runtime.

### Une seule grammaire pour tous les assets

Le même composant est destiné aux cartes et aux autres assets. Seul le sous-bloc
de sleeving reste propre aux cartes.

- `Pile` est une case à cocher indiquant que plusieurs unités identiques sont
  regroupées suivant leur axe physique d'épaisseur.
- Pour une carte nouvellement créée, `Pile` est cochée par défaut.
- Pour les autres types et les anciens projets, le default et la migration
  restent à fixer par un contrat additif afin de préserver le comportement
  historique.
- Lorsque `Pile` est cochée, l'interface expose X, Y, l'épaisseur unitaire, la
  quantité totale et le nombre souhaité d'unités par pile.
- `quantity_total` reste l'autorité et ne se confond jamais avec le nombre par
  pile. Si nécessaire, plusieurs piles sont formées ; la dernière peut être
  partielle et la partition doit couvrir exactement la quantité.
- Le sleeving modifie seulement l'épaisseur résolue des cartes selon son contrat
  existant ; il ne s'applique pas aux autres assets et n'absorbe pas les jeux de
  cavité.

`Pile` constitue ainsi un ou plusieurs groupes physiques. Elle ne décide ni leur
disposition dans le conteneur, ni leur placement dans la boîte.

### Pose explicite avec `Basculer`

- `Basculer` est une case à cocher commune à tous les assets empilables.
- Non cochée, la pile reste à plat : son épaisseur cumulée est portée par Z et
  ses dimensions de face restent en XY.
- Cochée, elle révèle `Poser sur : Grand côté / Petit côté`.
- Le choix désigne le côté d'appui, jamais le côté vertical : sur le grand côté,
  le petit côté devient vertical ; sur le petit côté, le grand devient vertical.
- L'épaisseur cumulée devient l'autre dimension horizontale.
- Aucune valeur `Automatique` n'est proposée dans ce contrôle et aucun solveur ne
  peut changer cette pose.

L'ancienne orientation carte `auto` reste un état de compatibilité en lecture
jusqu'à une migration explicite ; elle ne doit provoquer aucune réécriture
silencieuse. Les dimensions résolues et un schéma compact doivent rendre la pose
vérifiable avant solve.

### Séparation avec la disposition

`Pile` et `Basculer` produisent l'unité physique orientée. Les intentions
`Automatique`, `En ligne` et `Empilé verticalement` organisent ensuite une ou
plusieurs occurrences ou piles. L'intention avancée `Empilé verticalement`
translate des groupes déjà orientés le long de Z ; elle ne remplace jamais
`Pile`, le nombre par pile ou `Basculer`. Si un seul groupe ne lui donne aucun
effet, elle est masquée ou désactivée avec une raison lisible.

Toute modification de pile ou pose entre dans le digest local et invalide
seulement l'analyse concernée. P64 ne lit pas ces contrôles pour réinventer la
géométrie : il consomme les candidats P45 certifiés.

### Fixtures ajoutées au futur lot runtime

1. équivalence carte/non-carte du composant `Pile` hors sleeving ;
2. pile à plat, appui grand côté et appui petit côté avec axes exacts ;
3. quantité totale répartie en plusieurs piles, dernière pile partielle et
   couverture exacte ;
4. sleeving affectant seulement l'épaisseur résolue des cartes ;
5. ancienne orientation carte `auto` relue sans migration silencieuse ;
6. intention `Empilé verticalement` sans effet indisponible pour un seul groupe.

P45-M001V est fermée par cette acceptation. P64-L01 devient `ready`, sans ouvrir
dans ce lot le schéma, l'UI ou les formes runtime P45.
