# Contrat de derivation des bacs V0.1

## But

`bgig.container_derivation.v1` transforme un projet utilisateur V0.1 en une
liste de bacs necessaires et de leurs logements. C est un resultat de calcul,
pas un format que l utilisateur doit ecrire a la main.

Le contrat repond a la question : « de quelle taille minimale chaque bac doit
il etre pour contenir les pieces qui lui sont associees ? »

Il ne repond pas encore a : « ou placer chaque bac dans la boite ? »

## Entree

L entree est un `bgig.project.v1` valide, ou un projet P23 migrable. Pour chaque
ligne de `contents`, le moteur utilise :

- `shape_kind` et `dimensions_mm` ;
- `quantity` ;
- `container_group_id` ;
- `content_clearance_mm`, sinon le jeu global ;
- les parois et le fond du bac, sinon les reglages globaux.

`layout_clearance_mm` n est pas applique ici : c est le jeu entre bacs, donc la
responsabilite de P41.

## Sortie utile

Chaque element de `containers[]` contient :

- son `container_group_id` et son nom lisible ;
- son statut : `ready`, `blocked` ou `pending_fill_resolution` ;
- ses dimensions internes et externes minimales ;
- un logement par famille de pieces, avec son origine locale ;
- la capacite de pile, le nombre de piles et les dimensions du logement ;
- des avertissements et blocages actionnables.

Un groupe vide reste `pending_fill_resolution` : P41 pourra le dimensionner
depuis un bac vide ou un volume de remplissage demande.

## Regles de calcul

Pour les ronds, carres, rectangles, cubes, pions et formes sur mesure, les
dimensions de ligne decrivent une piece unitaire. La quantite est repartie en
piles verticales dans la hauteur utilisable, puis les piles sont organisees dans
une petite grille XY. Aucun plafond metier n est fixe sur cette quantite.

Pour les cartes, `z` est l epaisseur totale du paquet mesure. La quantite est
affichee mais ne multiplie pas cette hauteur.

Les formes rondes, carrees, cubes et pions gardent une enveloppe rectangulaire
prudente en V0.1. Il ne s agit pas d une promesse de cavite ronde imprimee.

Les logements d un meme bac sont disposes en lignes deterministes, separees par
une paroi interne de l epaisseur choisie. Le resultat privilegie une empreinte
equilibree sans faire de solveur global ni de backtracking.

## Statuts

| Statut | Signification | Action utilisateur |
| --- | --- | --- |
| `ready` | Le bac minimal tient individuellement dans les limites de la boite. | Continuer ; P40/P41 verifieront le projet complet. |
| `blocked` | Une largeur, profondeur ou hauteur necessaire depasse la boite. | Corriger les mesures, le groupement ou la quantite. |
| `pending_fill_resolution` | Un groupe vide attend un remplissage ou un separateur. | Le laisser vide ou l associer a un complement. |

Un statut `ready` ne signifie ni placement final, ni resultat Fusion, ni
validation d impression.

## API locale et UI

`POST /api/project-v1/derive-containers` recoit directement le projet et
retourne le plan. Le Studio l appelle depuis `Construire mes bacs`, puis montre
les dimensions et blocages dans le langage utilisateur.

## Handover

- P40 reserve les plateaux et livrets au-dessus des bacs derives.
- P41 place tous les bacs, applique le jeu entre bacs et ferme le volume.
- P42 materialise le resultat retenu en CAD IR puis Fusion.
- V0.2 peut modifier les formes ergonomiques sans changer la saisie V1.
- V0.3 ajoute les couvercles seulement apres V0.2.
