# North Star

## Formulation courte

Transformer les assets reels, contraintes de boite et intentions d'usage d'un jeu
de societe en systemes volumetriques modulaires imprimables, tolerancees,
inspectables et iterables, sans enfermer la logique de conception dans Fusion 360.

La surface utilisateur du MVP est pourtant Fusion 360 lui-meme : BGIG est un
add-in autonome dont la palette embarquee porte le parcours complet. La logique
reste hors adsk ; l utilisateur, lui, ne quitte pas Fusion et ne lance aucun
serveur ou navigateur externe.

## Traduction produit canonique acceptee le 2026-07-12

La premiere promesse n'est pas un mecanisme avance. C'est un parcours complet :

`mesurer la boite -> lister les pieces -> choisir quels elements partagent un bac
-> lister plateaux et livrets -> construire un insert qui affecte tout le volume`.

L'ordre des releases est obligatoire :

1. V0.1 fonctionnelle complete ;
2. V0.2 formes et ergonomie ;
3. V0.3 couvercles.

La specification detaillee est `docs/CANONICAL_PRODUCT_VISION.md`. Une
exploration P33/P34 ne peut pas court-circuiter cet ordre.

## Vision longue

BGIG doit devenir un generateur intelligent d'inserts modulaires parametrables
pour jeux de societe. La cible n'est pas seulement de produire des petits trays
rectangulaires : la cible est de concevoir un systeme de rangement complet dans
le volume X/Y/Z de la boite.

Le moteur doit partir de donnees mesurables : dimensions internes, hauteur utile,
assets, boards, livrets, plateaux, contraintes de couvercle, preferences
d'accessibilite, tolerances et profil d'impression. Il doit ensuite produire des
propositions explicables de modules imprimables, cavites, etages, reservations,
volumes libres, ordre de retrait et sorties CAD.

## Product Pillars

1. `Asset-first design` : decrire d'abord le materiel reel, puis deriver modules
   et cavites quand c'est utile.
2. `Volumetric layout` : raisonner sur tout le volume de la boite, pas seulement
   sur une grille XY.
3. `Modular printable bodies` : produire des corps imprimables nommes,
   tolerancees, auditables et iterables.
4. `Cavities and ergonomic features` : modeliser logements, aides de prise,
   fonds arrondis et futures operations CAD sans confusion avec validation
   physique.
5. `CAD generation pipeline` : transporter les decisions du moteur vers Fusion
   ou d'autres adaptateurs sans recalcul metier.
6. `Human validation gates` : bloquer les decisions qui engagent la vision,
   Fusion reelle, l'impression ou l'ergonomie.
7. `Design language and aesthetics` : ajouter labels, gravures, textures et
   style seulement apres la robustesse fonctionnelle.
8. `Complete volume accounting` : les cavites restent calibrees et les
   enveloppes des bacs demandes absorbent le volume imprimable restant ; aucun
   corps automatique ni vide oublie.

## Invariant V0.1 de remplissage

Les assets dimensionnent les cavites, jamais le volume exterieur final des bacs.
Apres reservation des plateaux/livrets et des jeux techniques, les enveloppes des
bacs demandes sont agrandies pour occuper tout le volume imprimable. Le surplus
devient de la matiere dans les parois et fonds. Aucun micro-bac, bloc ou
separateur n est invente par le moteur.

## Definition du succes

Le produit est sur la bonne trajectoire quand :

- la palette embarquee dans Fusion permet de creer, sauvegarder, construire et
  materialiser un projet sans application web externe ;
- un utilisateur peut decrire les assets et contraintes d'un jeu reel ;
- le moteur distingue assets, modules, cavites, features, layers et reservations ;
- plusieurs propositions peuvent etre comparees avec raisons et limites ;
- la CAD IR transporte les decisions sans perte ni recalcul dans Fusion ;
- Fusion produit des vues inspectables compactes et, plus tard, eclatees ;
- les tolerances et geometries critiques sont validees par impression reelle ;
- un agent peut choisir une mission par capability, milestone, gate et validation.

## Coordination des variantes internes

Plusieurs dispositions internes d'un même conteneur peuvent être nécessaires
pour satisfaire le volume global, mais elles ne changent pas la North Star :
les assets et intentions d'usage définissent les cavités, puis le solveur choisit
parmi des variantes locales certifiées. P45 possède la sémantique et les formes ;
P64 possède la combinaison globale, les budgets et la vérité du résultat.

Une marge volumique positive reste une condition nécessaire et non une promesse
de disposition. Aucune variante ne peut modifier silencieusement un jeu, une
valeur physique, une cavité ou ajouter un corps.

## Ce que le projet doit apprendre a faire

### Court terme

- Stabiliser les cavites et features abstraites deja presentes.
- Decider par gate la premiere generation Fusion reelle de cavites simples.
- Garder les rapports et la CAD IR comme source d'audit.

### Moyen terme

- Introduire un modele d'assets autonome.
- Representer layers, reservations de boards/livrets et ordre de retrait.
- Produire des vues Fusion compactes et eclatees sans recalcul metier.
- Construire un premier raisonnement volumetrique X/Y/Z.

### Long terme

- Proposer plusieurs variantes scorees et expliquees.
- Gerer modules composites, empilement, supports, couvercles et mecanismes.
- Ajouter une couche esthetique parametrable.
- Fermer la boucle calibration -> impression -> ajustement de profils.

## Limites assumees

- Le solveur volumetrique 3D complet n'est pas implemente maintenant.
- Les valeurs de tolerance restent experimentales tant qu'elles ne sont pas
  validees par impression.
- Une validation Fusion ne vaut pas validation physique.
- Les generations de cavites, fillets, encoches, booleans, exports STL/3MF et
  mecanismes restent soumises a gates humaines.

## Lien de pilotage

La trajectoire est detaillee dans `docs/CAPABILITY_MAP.md`, puis declinee dans
`docs/ROADMAP.md`, `docs/BACKLOG.md`, `docs/NEXT_ACTIONS.md` et les gates.
