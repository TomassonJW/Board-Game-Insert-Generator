# 2026-07-13 - P64 runtime hardening

## Contexte

Le test utilisateur Fusion a revele quatre familles de defauts apres
l implementation automatisee P64 :

1. des configurations 4/5/6 bacs n etaient pas monotones ;
2. un bac haut empechait parfois toute pile voisine de bacs plus courts ;
3. les cavites sous les plateaux perdaient l epaisseur cumulee des plateaux ;
4. plusieurs conteneurs portant le meme nom pouvaient bloquer la synchronisation
   Fusion par conflit de nom de corps.

## Causes confirmees

- La revalidation d enveloppe comparait les dimensions locales d un corps tourne
  aux axes monde non permutes.
- Le solveur representait uniquement des tranches Z couvrant tout le plan XY.
  Il ne pouvait pas laisser un corps haut traverser plusieurs niveaux voisins.
- Les reservations superieures etaient coupees apres calcul de la profondeur de
  contenu sans compensation de la profondeur utile.
- Le nom du corps CAD derivait uniquement du libelle utilisateur.

## Decision

Le correctif reste dans ADR-0057 et ADR-0059 ; aucune nouvelle ADR n est requise.

- conserver les candidats historiques et leur priorite ;
- ajouter un repli borne de partitions en piles verticales ;
- projeter leurs bornes Z en intervalles globaux pour appui, retrait et apercu ;
- revalider les limites par groupe dans le repere local apres rotation ;
- ajouter a chaque cavite intersectee la profondeur cumulee maximale des
  reservations superieures, sous contrainte de fond minimal ;
- separer libelle utilisateur et nom technique Fusion unique ;
- ne creer aucun corps automatique et ne pas ajouter de solveur externe.

## Preuves

- 428 tests unitaires passent.
- La matrice cartes plus jetons construit 4, 5 et 6 bacs successivement.
- Le cas a 6 bacs utilise deux intervalles Z et conserve un corps haut traversant.
- Deux plateaux superposes produisent une compensation cumulee de 5 mm.
- Un projet a sept corps dont six partagent le libelle Bac cartes produit sept
  noms techniques uniques et passe generation_plan_from_cad_ir.
- Compilation Python et git diff --check passent.
- Un audit deterministe de 120 configurations aleatoires ne trouve aucune
  divergence ni fausse non-conservation.
- Le projet sauvegarde courant produit cinq corps, cinq cavites compensees et
  passe le planificateur Fusion hors ligne.

## Limites

- Le solveur reste heuristique, borne et non optimal garanti.
- La nouvelle recherche hybride enumere des partitions contigues bornees ; elle
  ne promet pas de trouver toute solution geometrique possible.
- Le correctif doit encore etre observe dans Fusion avant fusion-validated.
- Aucune impression reelle n est revendiquee.

## Suite

Installer le package Fusion 0.1.15, verifier les marqueurs installes, puis laisser
P65 comme prochaine mission ready avant la gate humaine P66.
