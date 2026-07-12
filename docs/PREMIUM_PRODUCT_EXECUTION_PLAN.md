# Plan d execution - BGIG premium

> Surface utilisateur supersedee par ADR-0055 : add-in Fusion et palette embarquee
> uniquement. Toute mention du Studio web ci-dessous est historique.

> Document historique, remplace pour l'ordre d'execution par
> `docs/CANONICAL_PRODUCT_VISION.md`, `docs/MVP_EXECUTION_PLAN.md` et ADR-0047.
> Le 2026-07-12, la sequence P33/P34 a ete reconnue prematuree : aucune mission
> esthetique ou couvercle ne redevient active avant les gates V0.1 puis V0.2.

## Statut

Historique depuis l'objectif utilisateur du 2026-07-11. Ce plan ne pilote plus
les prochaines missions et n'autorise jamais une validation Fusion ou impression
sans preuve correspondante.

## Resultat cible

BGIG permet a une personne de decrire un jeu reel, voir son rangement evoluer,
comparer des propositions, choisir un style fonctionnel, materialiser de vrais
bacs dans Fusion, exporter puis mesurer une impression. Le systeme explique a
chaque etape ce qui est pret, experimental ou non valide.

```text
Jeu reel -> Boite + inventaire -> Intentions + reservations
-> Propositions comparables -> Edition live -> Bacs fonctionnels
-> Palette Fusion -> Export/preprint -> Impression + mesures
```

## Contrat de parcours

### 1. Composer dans le Studio

Le Studio est la surface principale. Il commence par la boite, les composants et
les intentions, pas par les fichiers CAD, les policies ou les chemins locaux.

### 2. Voir et decider en direct

Chaque changement met a jour sans attendre : prevalidation, vue 2D de boite,
reservations, modules, collision et statut de preparation. Les calculs plus
couteux sont declenches explicitement ou avec debounce, jamais a chaque frappe
dans Fusion.

### 3. Materialiser une geometrie fonctionnelle

Une selection P21 doit etre projetee en bacs : volume externe, parois, fond,
logements, aides de prise applicables et statut de fabrication. Un simple bloc
enveloppe reste un artefact technique, jamais le resultat utilisateur.

### 4. Inspecter dans Fusion

La palette Fusion affiche un resume clair : design recu, modules crees,
avertissements utiles, statut fabrication et actions `Previsualiser`,
`Mettre a jour`, `Exporter`. Les identifiants, chemins CAD et diagnostics bruts
restent dans le mode expert.

### 5. Fabriquer et apprendre

L export et le manifeste indiquent explicitement : non verifie, a slicer,
imprime non mesure, mesure OK/KO. Aucun bouton ne promet une impression reussie
sans mesures.

## Parametrage vivant

| Famille | Entrees visibles | Reponse live attendue | Statut cible |
| --- | --- | --- | --- |
| Projet | boite, couches, reservations, assets | vue boite, capacite et conflits | P30 |
| Fonction | dimensions, allocations, locks, priorites | apercu et proposition recalculee | P30-P31 |
| Geometrie | parois, fond, logement, prise | preview de bac et blockers | P31 |
| Forme | rayon, chanfrein, style d encoche, proportion | preview sans cacher les limites | P33 |
| Esthetique | labels, typographie, gravure, theme | variante visuelle non destructive | P33 |
| Mecanique | aucun, couvercle pose, coulissant, clip | contraintes, jeux et risques explicites | P34 experimental |

Un apercu live n implique pas de regenerer le document Fusion a chaque frappe.
Le Studio rend le plan immediatement ; Fusion applique une selection explicite
par une action volontaire `Mettre a jour la scene`.

## Jalons executables

| Lot | Valeur livree | Preuve | Gate |
| --- | --- | --- | --- |
| P29 | plan premium, ADR, P28 requalifie | docs, tests de pilotage | aucune |
| P30 | Studio recentre, vue boite live, parcours novice | tests TypeScript + inspection navigateur | choix visuel structurant |
| P31 | projection selection -> vrais bacs | tests moteur/CAD IR + Fusion | premiere geometrie de bac depuis P21 |
| P32 | palette Fusion concise, dialogue expert replie | tests bridge + smoke Fusion | premiere palette Fusion |
| P33 | tokens visuels et forme parametrique | tests de contraintes + review visuelle | langage visuel |
| P34 | contrats couvercles/mecanismes experimentaux | ADR, tests abstraits, prototype cible | mecanisme + impression |
| P35 | jeu reel, export, slicer, mesures | manifeste, protocole, photos/mesures | validation physique |

## Principes non negociables

- Le moteur Python reste la source de verite et ne depend pas de Fusion.
- Une scene Fusion ne recalcule ni layout, ni score, ni tolerance.
- Toute valeur qui peut fragiliser la piece est reliee a des contraintes visibles.
- Les controles experts existent, mais ne sont jamais la premiere experience.
- Les propositions sont explicables ; les statuts `explorable`, `preprint` et
  `print-validated` ne sont jamais confondus.

## Sortie de P28

P28 est conserve comme preuve de raccord CAD IR, mais son observation utilisateur
est `KO produit/UX` : message incomprehensible et blocs non fonctionnels. Il ne
sera ni promu ni utilise comme demonstration. P31 le remplace par une preuve de
geometrie fonctionnelle.

## Gates restantes

1. `P30-GATE` : accepter le langage visuel et le premier flux Studio avant de
   le coder.
2. `P31-GATE` : accepter la strategie de projection de modules selectionnes vers
   des bacs fonctionnels.
3. `P32-GATE` : smoke humain de la palette Fusion.
4. `P34/P35` : mecanismes et validation physique.