# P44-M004 — Composition conteneur / contenu et modes de taille

Date : 2026-07-14
Statut : implemented, automated-validated, human-fusion-gate-required
Package cible : palette Fusion 0.1.25

## Précondition et intention

P44-M003V est acceptée par P44-M003V Fusion OK 0.1.24 - commit 7b71d01.
P44-M004 rend lisible le modèle existant : un contenu possède
container_group_id et s’affiche dans la carte de son conteneur parent. Ce n’est
pas une migration vers un arbre récursif.

Capabilities : C-FUSION-UI, C-MODULE, C-QUALITY.
Milestone : fondation UX V0.2 P44.
Gate de sortie : P44-M004V, observation Fusion humaine.

## Périmètre livré

- container_groups reste la collection de parents et contents la collection
  plate ; la palette les projette par container_group_id.
- Le nom éditable devient le titre principal de la carte conteneur et de la
  carte enfant. Aucun second titre permanent n’est affiché.
- Les éléments sont rendus dans leur conteneur ; le rattachement n’est plus un
  champ permanent. L’action secondaire Déplacer vers… reste disponible.
- Une carte conteneur expose un seul mode de taille Auto, Cible ou Fixe. Les
  projets historiques dont les axes divergent restent visibles sous
  Personnalisé, dans Compatibilité historique par axe.
- Le contrôle global discret demande confirmation. Il refuse Cible ou Fixe
  lorsqu’un conteneur n’a pas les trois dimensions explicites requises : il
  n’invente aucune valeur.
- Solidité, la paroi minimale et le fond minimal restent visibles ; les calculs
  restent dans Détails calculés repliés.
- Les identifiants DOM sont fondés sur les identifiants métier, y compris dans
  les cartes enfants, afin de préserver focus, caret, détails et scroll.

## Invariants et exclusions

Aucun schéma, loader, roundtrip, bridge Python, solveur, tolérance, géométrie,
CAD IR, scène Fusion automatique ou complément historique ne change. Le cœur
Python reste sans adsk. Il n’existe ni conteneur de conteneur, ni couleur
personnalisable, ni barre de création persistante dans ce lot. Les jeux par
objet restent P44-M008/P44-M009 ; les réglages toujours visibles, le cycle
document et le diagnostic restent P44-M006.

## Preuves automatisées attendues

- DOM : projection parent/enfant, déplacement secondaire, modes unifiés et
  compatibilité historique.
- Roundtrip/bridge : absence de nouvelle action ou mutation de format.
- Transport de palette et préparation P66 : package exact 0.1.25.
- Syntaxe JavaScript, suite Python complète, compileall, frontière adsk,
  exemple CLI et git diff --check.

## Gate humaine P44-M004V

Dans Fusion, vérifier le package 0.1.25 avec au moins deux conteneurs et des
éléments : parentage visuel, renommage, déplacement secondaire, conservation du
focus après modification, modes Auto/Cible/Fixe, cas historique Personnalisé et
confirmation du mode global. Aucun élément, aucune origine, aucun calcul ni
aucune scène ne doit apparaître ou changer sans action explicite.

Retour OK attendu : P44-M004V Fusion OK 0.1.25 - commit <sha>.