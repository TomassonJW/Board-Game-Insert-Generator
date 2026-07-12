# Audit du chemin produit - 2026-07-12

> Surface utilisateur supersedee par ADR-0055 : add-in Fusion et palette embarquee
> uniquement. Toute mention du Studio web ci-dessous est historique.

## Verdict

Le projet n'a pas regresse au sens ou les fondations auraient disparu. Il a
derive en priorite et en presentation. P33 et P34 ont ete engages alors que le
coeur de valeur V0.1 restait incomplet : regroupement simple des pieces par bac,
plateaux/livrets comme pile superieure, dimensionnement automatique des bacs et
fermeture explicite de tout le volume.

## Ce qui est deja utile

- moteur Python pur et teste ;
- inventaire dynamique de pieces dans le Studio ;
- dimensions de boite et reservations ;
- BoxFillPlan, collisions, couverture et regions libres ;
- placement greedy et variantes P20/P21 ;
- bridge CAD IR/Fusion ;
- bacs ouverts P31 observes dans Fusion ;
- palette Fusion secondaire P32.

Ces briques reduisent le travail restant. Elles ne forment pas encore le MVP
decrit dans la vision canonique.

## Ce qui manque au MVP

| Besoin canonique | Etat reel | Ecart |
| --- | --- | --- |
| Tableau pieces simple | Present en partie | Types limites et jargon interne encore visible |
| Choix du bac par ligne | Candidats et allocations experts | Pas de menu humain `Bac 1`, `Bac 2` |
| Dimensions de bac derivees | Candidats saisis manuellement | L'utilisateur doit encore pre-dessiner le module |
| Tableau plateaux/livrets | Reservations repliees en expert | Pas de quantite ni pile superieure automatique |
| Jeu commun entre volumes | Tolerances dispersees | Pas de contrat V0.1 unique dans le Studio |
| Paroi minimale par bac | Valeur technique par defaut | Pas de reglage produit par groupe de bac |
| Remplissage creux/plein/separateur | FreeVolume descriptif | Pas d'allocation ou de geometrie de fermeture du residu |
| Volume complet X/Y/Z | Greedy 2D par layer | Pas de recherche globale avec pile superieure et residus |
| Construction fonctionnelle | Bacs ouverts generiques | Logements et groupes utilisateur incomplets |
| UI vraiment user-first | Direction visuelle presente | Parcours encore structure par les objets internes |

## Pourquoi la trajectoire a derive

### 1. La roadmap n'avait pas de verrou de version

Le protocole choisissait la premiere mission `ready`, mais n'interdisait pas une
mission de version ulterieure tant que toutes les conditions de sortie V0.1
n'etaient pas satisfaites. P33 puis P34 ont donc pu devenir `ready` apres P32.

### 2. Une capability terminee a ete confondue avec une valeur produit terminee

Le projet validait correctement des briques techniques isolees, puis les faisait
avancer dans la roadmap. Une cavite Fusion ou une palette validee ne prouve pas
que l'utilisateur peut decrire et construire tout son rangement.

### 3. L'UI a copie le modele moteur

Le Studio expose encore les concepts `reservations`, `candidates`, allocations,
layers et preferences. Ils sont utiles techniquement, mais l'utilisateur pense
en pieces, bacs partages, plateaux et bouton de construction.

### 4. Les gains visibles ont masque le chemin critique

P33 donnait un effet visuel rapide et P34 une nouvelle geometrie observable.
Ces increments etaient plus faciles a isoler que le vrai solveur de boite
complete, mais ils n'etaient pas prioritaires pour le MVP.

### 5. La gate C a ete sur-interpretee

Le choix humain `C - Couvercle coulissant` repondait a une question de mecanisme
que le projet avait lui-meme mise au premier plan. Ce choix autorisait une option,
pas son passage devant les fonctions de base. L'ordre produit n'avait pas ete
demande clairement et a ete deduit a tort.

### 6. Les rapports etaient trop techniques

Les rapports mettaient en avant commits, tests, CAD IR et smoke Fusion, sans dire
assez directement : "le MVP ne sait toujours pas faire X". Cela a donne une
impression de progression superieure a la valeur reellement disponible.

## Traitement des travaux prematures

- P33 reste un prototype technique de preview, non une V0.2.
- ADR-0045 et le coupon P34 sont `superseded-for-product`.
- `join_rectangular_prism` peut rester comme primitive CAD testee ; elle n'impose
  aucun mecanisme futur.
- Les controles apparence/couvercle doivent etre retires du parcours principal
  V0.1, sans suppression destructive avant migration du schema.
- Aucun smoke P34 n'est demande a Thomas dans le chemin actif.

## Correction de gouvernance

ADR-0047 ajoute une regle de chemin critique : tant que la checklist de sortie
V0.1 n'est pas complete, seules les missions qui ferment un ecart V0.1 peuvent
etre `ready`. La meme regle s'appliquera entre V0.2 et V0.3.
