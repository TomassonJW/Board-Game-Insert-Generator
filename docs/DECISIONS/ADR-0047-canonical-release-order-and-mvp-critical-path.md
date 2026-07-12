# ADR-0047 - Ordre canonique des versions et chemin critique MVP

## Statut

Accepte par la clarification produit explicite du 2026-07-12.

## Contexte

Apres P32, le pilotage a rendu P33 puis P34 executables alors que le MVP ne
savait pas encore deriver simplement les bacs depuis les pieces, traiter une
pile de plateaux/livrets et affecter tout le volume utile. Le choix humain d'un
couvercle coulissant a ete interprete comme une priorite, alors qu'il ne
selectionnait qu'une option dans une gate presentee trop tot.

## Options

1. Continuer P34/P35 puis revenir au coeur produit.
2. Developper en parallele MVP, esthetique et mecanismes.
3. Verrouiller l'ordre V0.1 fonctionnelle, V0.2 formes, V0.3 couvercles.

## Decision

Retenir l'option 3.

- V0.1 couvre la boite, les tableaux dynamiques, les groupes de bacs, les
  plateaux/livrets, parois, jeu commun, remplissages et construction complete.
- V0.2 couvre formes et ergonomie apres acceptation V0.1.
- V0.3 couvre les deux familles de couvercles apres acceptation V0.2.
- Une mission d'une version ulterieure ne peut pas etre `ready` tant que la gate
  de sortie de la version precedente n'est pas acceptee.
- Les controles P33/P34 sont retires du parcours principal V0.1, tout en restant
  compatibles pour ne pas casser les anciens projets.
- P34 est archive comme exploration et son smoke Fusion n'est plus une action
  humaine active.
- Le modele utilisateur V0.1 exprime le regroupement par un `Bac cible` stable,
  pas par l'edition manuelle de candidats moteur.

## Consequences positives

- chaque mission ferme un ecart visible du MVP ;
- les rapports peuvent dire clairement quelle promesse utilisateur est acquise ;
- l'UI et le moteur convergent vers le meme contrat de boite complete ;
- les travaux esthetiques et mecaniques auront ensuite une base volumetrique
  correcte pour calculer leur impact.

## Consequences negatives

- P33 et P34 ne sont pas promus malgre leur code et leurs tests ;
- le schema doit migrer sans casser les drafts existants ;
- le solveur V0.1 est un lot plus difficile que les increments visuels recents ;
- la roadmap historique P0-P35 reste utile comme trace mais n'est plus un ordre
  d'execution.

## Alternatives refusees

- Continuer les couvercles : accentuerait la dette de priorite et reposerait sur
  des dimensions de bacs encore non resolues globalement.
- Trois axes en parallele : contraire a l'atomicite des missions et source de
  contrats divergents.
- Supprimer P33/P34 immediatement : migration destructive inutile ; leurs
  primitives et tests peuvent rester archives sans diriger le produit.

## Suivi

- `docs/CANONICAL_PRODUCT_VISION.md` porte la promesse.
- `docs/MVP_EXECUTION_PLAN.md` porte les lots P36-P50.
- `docs/NEXT_ACTIONS.md` ne peut contenir qu'une mission du chemin V0.1 tant que
  P43 n'est pas accepte.
- La checklist de version doit etre relue avant chaque selection autonome.
