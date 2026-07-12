# Contrat executable des enveloppes extensibles

Statut : implemente par P55.

## Objet

Le contrat bgig.expandable_envelope_contract.v1 se place entre la derivation
des logements P39 et le futur solveur de partition P57. Il rend executables les
quatre notions distinctes imposees par ADR-0054 :

1. cavites calibrees depuis les assets, quantites et jeux ;
2. arrangement local stable de ces cavites ;
3. enveloppe exterieure minimale construite avec parois et fond minimaux ;
4. enveloppe exterieure finale, proposee ou verrouillee, qui ne peut qu agrandir
   l enveloppe minimale.

P55 ne place pas les bacs dans la boite et ne produit aucune geometrie CAD.

## Extension additive de bgig.project.v1

Chaque entree container_groups accepte trois champs optionnels. Leur absence
conserve les projets P37 existants.

| Champ | Defaut | Semantique |
| --- | --- | --- |
| expansion_axes | x/y/z a true | Autorise ou interdit l augmentation de l enveloppe finale sur chaque axe. |
| locked_outer_dimensions_mm | x/y/z a null | Fixe une dimension exterieure finale positive sur un axe. |
| surplus_preference | balanced | Preference future du solveur : balanced, walls ou floor. |

Les valeurs de paroi et fond du groupe restent des minima. Les champs de P55 ne
modifient ni content_clearance_mm, ni les dimensions des assets.

## Modele pur

derive_expandable_envelope_contract retourne, pour chaque groupe constructible :

- cavity_layout dans le repere stable minimum_outer_envelope.local ;
- minimum_outer_envelope_mm ;
- final_outer_envelope_mm ;
- minimum_envelope_origin_in_final_mm ;
- la distribution explicite du surplus sur gauche/droite, avant/arriere et sous
  l enveloppe minimale ;
- les contraintes normalisees, blockers, warnings et invariants.

L expansion X/Y est repartie autour du repere minimal. L expansion Z place le
surplus sous ce repere. Les origines locales et dimensions des cavites dans le
repere minimal restent identiques. P57 pourra choisir les dimensions finales et
les placements conjoints, mais ne devra pas recalculer silencieusement cet
arrangement.

## Invariants

- une enveloppe finale est superieure ou egale au minimum sur X/Y/Z ;
- un axe non extensible reste exactement a sa dimension minimale ;
- une dimension verrouillee est respectee et ne peut pas etre sous le minimum ;
- l enveloppe finale reste dans les limites unitaires de la boite ;
- changer uniquement l enveloppe finale laisse cavity_layout identique ;
- aucun groupe vide ne recoit une fausse cavite ou une enveloppe automatique ;
- automatic_body_count vaut toujours zero ;
- jeux internes et externes restent du vide, jamais du materiau absorbe ;
- aucun statut Fusion ou impression n est produit.

## API locale

La route loopback POST /api/project-v1/derive-envelopes accepte soit un projet
V1 ou migrable directement, soit un objet contenant project et
final_outer_dimensions_by_group, indexe par identifiant de bac.

Les erreurs de schema ou de contraintes sont retournees comme erreurs de draft
locales. Le contrat reste sans I/O, sans dependance externe et sans import Fusion.

## Limite de mission

P55 prouve le contrat individuel cavite/minimum/final. Il ne prouve pas qu un
ensemble de bacs ferme le volume complet. La partition, les jeux entre bacs, les
alignements, le support de pile et le diagnostic global appartiennent a P57,
apres implementation de l editeur P56.
