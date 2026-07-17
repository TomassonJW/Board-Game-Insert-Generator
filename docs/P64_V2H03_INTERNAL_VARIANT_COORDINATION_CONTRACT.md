# P64-V2H03 — Variantes internes bornées et sélection globale

Statut : contrat d'architecture accepté le 2026-07-18 ; runtime non commencé.

ADR :
[ADR-0070](DECISIONS/ADR-0070-internal-container-variant-ownership.md).

Capability principale : `C-SOLVER`. Capabilities associées : `C-GEOMETRY`,
`C-ASSET`, `C-LAYOUT`, `C-QUALITY` et `C-USABILITY`.

## 1. But et preuve attendue

P64-V2H03 doit permettre à un conteneur multi-cavités de présenter plusieurs
enveloppes locales certifiables, puis laisser le placement global choisir leur
combinaison. Le lot corrige la pré-sélection locale d'une enveloppe unique ; il
ne promet pas que tout volume positif possède une disposition.

Une réussite produit exige un plan complet certifié par le validateur commun.
Une recherche épuisée reste `no_solution_within_budget`. Le cas dense réel peut
rester non résolu si aucune variante autorisée et aucun placement du budget ne
passent le certificat.

## 2. Frontières de responsabilité

### P45 / frontière géométrique locale

P45 possède :

- la sémantique des dispositions `standard/auto`, `rangée` et `colonne
  verticale` ;
- les futures formes de cavité, profils ergonomiques et contraintes d'usage ;
- les règles permettant à un producteur sémantique de déclarer deux dispositions
  équivalentes ;
- la certification locale des cavités, cloisons, parois, fonds et contenus.

P64-V2H03B peut construire la frontière technique et un producteur correctif
rectangulaire, mais ne rend aucune mission P45 active et n'expose aucun mode
P45 dans la palette.

### P64 / recherche globale

P64 possède :

- les profils d'effort et caps de recherche ;
- l'expansion paresseuse des options de variantes pendant le placement ;
- la comparaison des familles baseline, greedy et beam ;
- le certificat global, la fermeture continue minimale et le classement final ;
- la vérité du résultat, la télémétrie et les motifs d'arrêt.

P64 ne déplace jamais une cavité, ne modifie pas son jeu et ne fabrique pas une
variante à l'intérieur d'une stratégie de placement.

## 3. Contrat interne minimal

La représentation cible reste interne et immuable. Les noms exacts peuvent être
adaptés au code existant, mais les informations suivantes sont obligatoires :

```text
ContainerInternalVariant
  container_group_id
  variant_id
  geometry_digest
  producer_id + producer_version
  canonical: bool
  minimum_outer_envelope_mm
  cavity_layout (repère minimum_outer_envelope.local)
  wall_thickness_mm + floor_thickness_mm
  local_cost_breakdown
  provenance / aliases
  local_certificate
```

Le contrat est distinct de `bgig.project.v1`. Aucune variante n'est persistée
comme choix utilisateur dans P64-V2H03. Le plan sélectionné transporte déjà la
géométrie réelle des cavités ; la traçabilité de variante utilise les structures
internes et le diagnostic existant sans changer le format source du projet.

## 4. Identité canonique

`geometry_digest` est calculé avec une sérialisation déterministe contenant :

- l'identifiant stable du conteneur et la version du contrat ;
- l'enveloppe extérieure minimale ;
- paroi, cloison interne et fond minimaux ;
- le repère local ;
- les cavités triées par identifiant stable, avec contenu source, origine,
  dimensions, forme rectangulaire résolue, quantité et jeu effectif par axe ;
- toute contrainte locale qui change la constructibilité.

Ne participent pas au digest : ordre d'énumération, temps, libellé humain,
index temporaire, score global ou origine dans la boîte.

Règles :

1. deux producteurs donnant la même géométrie pour le même conteneur produisent
   un seul candidat et plusieurs alias de provenance ;
2. une rotation globale 0/90 est une option P64 et non une variante locale ;
3. un miroir n'est jamais supposé équivalent ;
4. la déduplication ne traverse pas deux `container_group_id` distincts ;
5. la variante canonique actuelle garde un identifiant et une provenance
   stables indépendants des nouvelles variantes.

## 5. Producteurs autorisés dans le premier incrément

### `canonical_v1`

- reproduit exactement la géométrie retenue avant P64-V2H03 ;
- est toujours générée, certifiée et placée en tête de frontière ;
- conserve les chemins et fixtures H03R, H06, H07, V2H01 et V2H02.

### `bounded_rectangular_relayout_v1`

- réutilise les compartiments rectangulaires, dimensions, quantités et jeux
  déjà résolus ;
- peut varier ordre, rangées, étagères et largeur cible sous caps explicites ;
- ne change jamais l'orientation physique source d'un asset ;
- ne crée ni cavité, ni feature, ni corps, ni réservation ;
- reste un producteur technique sans libellé utilisateur P45.

Tout autre producteur exige soit une extension contractuelle bornée, soit une
décision P45 si sa différence porte une intention fonctionnelle ou une forme.

## 6. Certificat local

Le certificat local est fail-closed. Il vérifie au minimum :

- couverture exacte du multiensemble de contenus demandé ;
- dimensions, quantités, formes résolues et jeux inchangés ;
- cavités contenues dans `minimum_outer_envelope` ;
- absence de recouvrement des cavités et cloisons internes cohérentes ;
- parois et fond au moins égaux aux minima déjà résolus ;
- origines exprimées dans le repère local déclaré ;
- aucun corps automatique et aucun contenu inventé ou perdu ;
- digest correspondant exactement au payload certifié.

Il ne vérifie pas :

- la boîte, les jeux externes globaux ou la marge sous couvercle ;
- les réservations supérieures ;
- support, retrait, fermeture du résiduel ou conservation globale ;
- une ergonomie ou une imprimabilité non mesurée.

Une variante rejetée porte des codes stables et reste absente de la frontière
consommable par P64.

## 7. Frontière bornée et coût local

La frontière élimine d'abord les doublons et les variantes dominées. Une
variante A domine B uniquement si A n'est pire sur aucun axe local contracté et
est meilleure sur au moins un : enveloppes X/Y/Z, volume, aspect ou complexité
du layout. La dominance ne compare jamais une propriété non mesurée.

Le coût local ordonne :

1. variante canonique ;
2. enveloppe et axes contraignants ;
3. volume et aire ;
4. écart d'aspect ;
5. nombre de rangées/cloisons ;
6. producteur puis digest stable.

Ce coût pilote génération, caps et ordre d'expansion. Il ne remplace pas le
score public du plan complet.

## 8. Sélection globale sans produit cartésien

Le solveur ne matérialise jamais
`variants(c1) × variants(c2) × ... × variants(cn)`.

Un état de recherche contient seulement :

- les conteneurs déjà placés ;
- pour chacun, la référence de variante choisie ;
- les espaces/points extrêmes, appuis et réservations déjà calculés ;
- les conteneurs restants et leurs petites frontières locales ;
- le budget consommé et les bornes nécessaires.

Quand un participant est développé, P64 énumère au plus
`max_variant_options_per_expansion` variantes certifiées, puis leurs rotations
et positions autorisées. Les bornes de volume, axes et réservation peuvent
couper une option avant reconstruction, mais le validateur commun reste
autoritaire.

La fermeture continue minimale de P64-V2H01 s'applique après placement complet,
sur l'enveloppe correspondant à la variante choisie. Elle ne change jamais de
variante et ne déplace jamais les cavités.

## 9. Lanes de compatibilité et fallback

Ordre normatif du premier runtime :

1. exécuter le portefeuille canonique inchangé : baseline dirigée, greedy,
   `legacy_ems_v1`, puis `bridge_ems_v2` ;
2. si au moins un plan canonique autorisé est certifié, conserver le résultat
   historique et ne pas lancer la lane corrective multi-variantes ;
3. sinon exécuter les lanes multi-variantes du profil demandé ;
4. unir seulement les candidats complets certifiés, dédupliquer et appliquer le
   classement public existant ;
5. si aucune lane n'aboutit, retourner `no_solution_within_budget` avec les caps
   réellement atteints.

Cette règle limite P64-V2H03 à un fallback correctif. Une future comparaison de
variantes sur un projet déjà résolu relèvera d'un contrat produit séparé, en
coordination avec P45.

## 10. Budget et monotonie

Le budget variantes comporte au minimum :

- `max_generated_variants_per_container` ;
- `max_certified_variants_per_container` ;
- `max_retained_variants_per_container` ;
- `max_variant_options_per_expansion` ;
- `max_variant_assignment_states` ;
- `max_variant_placement_trials`.

Règles obligatoires :

- toutes les limites sont finies, non négatives, sérialisables et observables ;
- Rapide ⊆ Normal ⊆ Approfondi pour producteurs, variantes et limites ;
- Normal exécute d'abord la lane Rapide inchangée, puis sa lane additionnelle ;
- Approfondi conserve les lanes Rapide et Normal avant sa lane additionnelle ;
- une solution d'une lane moins profonde reste candidate dans les profils plus
  profonds ;
- le temps de garde ne participe pas au digest ;
- aucun cap numérique n'est promu avant mesure des fixtures P64-V2H03B ;
- atteindre une limite ne prouve jamais l'impossibilité.

Les budgets H07/V2H02 existants ne sont pas modifiés par P64-V2H03A. Le tableau
numérique initial sera un livrable de P64-V2H03B, revu avant le branchement C.

## 11. Télémétrie et traçabilité

Le diagnostic doit pouvoir exposer, sans reconstruire le DOM éditable :

- producteurs exécutés et version ;
- variantes générées, rejetées localement, dédupliquées et retenues par
  conteneur ;
- raisons agrégées de rejet/dominance ;
- lanes exécutées et budgets associés ;
- états d'affectation et essais variante-placement ;
- références de variantes des candidats complets et du plan retenu ;
- digests et certificats local/global ;
- arrêt : fast path canonique, solution variante, cap, annulation ou entrée
  invalide.

Les noms techniques restent dans le diagnostic secondaire. Le parcours novice
continue d'afficher seulement méthode, effort, résultat et corrections utiles.

## 12. Fixtures déterministes obligatoires

P64-V2H03B doit figer les données avant de modifier le placement global :

1. **Parité canonique** : projets simple, H01, H02, H03R et V2H01 ; même
   variante canonique, mêmes cavités et même résultat historique.
2. **Déduplication** : plusieurs ordres producteurs donnent la même géométrie ;
   un seul digest est retenu avec toutes les provenances.
3. **Rotation globale** : une rotation X/Y n'est pas comptée comme variante
   locale supplémentaire.
4. **Cul-de-sac multi-cavités minimal** : les meilleurs choix locaux ne tiennent
   pas ensemble ; une combinaison alternative certifiée donne un plan global.
5. **Réservation localisée** : deux variantes locales valides n'ont pas la même
   compatibilité après placement sous une empreinte supérieure ; seul le
   certificat global tranche.
6. **Axes Auto/Cible/Fixe** : la variante ne contourne aucun axe fixe et la
   fermeture ne change pas de cavités.
7. **Jeux ADR-0064** : les jeux entre conteneurs et contre la boîte restent
   globaux ; les overrides asset/plateau/livret restent locaux.
8. **Cas dense anonymisé** : snapshot reproductible du mécanisme V2H02, sans
   chemin ou donnée locale. Le test prouve l'exercice réel des variantes et un
   résultat honnête ; il ne suppose pas une solution avant certification.
9. **Monotonie** : toute solution Rapide reste candidate en Normal et
   Approfondi ; les digests de lanes préservées restent stables.
10. **Budget/annulation** : arrêt borné et `stale_or_cancelled` sans résultat
    visible obsolète.

Un simple jeu de rectangles indépendants qui ne possède qu'une enveloppe par
conteneur ne satisfait pas le critère 4. La fixture doit contenir de vraies
cavités multiples et au moins deux enveloppes locales certifiées.

## 13. Découpage de livraison

### P64-V2H03A — Arbitrage et contrat

- Statut : `done` quand ADR-0070, ce contrat et le pilotage sont intégrés.
- Runtime : aucun.
- Validation : cohérence documentaire, liens, diff-check et tests de
  documentation.

### P64-V2H03B — Frontière locale, certificats et fixtures

- Statut après H03A : `ready`.
- Livrables : types immuables, digests, producteurs canonique/correctif,
  certificat local, frontière de Pareto, fixtures 1 à 8 et tableau de caps
  mesuré.
- Interdit : branchement dans la sélection publique, UI, schéma projet, formes
  P45 ou changement de résultat utilisateur.
- Acceptation : parité canonique bit-à-bit aux frontières publiques, génération
  déterministe et bornée, fixtures locales vertes, suite complète.

### P64-V2H03C — Sélection globale paresseuse

- Statut : `blocked-by-P64-V2H03B`.
- Livrables : lanes préservées, expansion variante-placement, budgets
  monotones, télémétrie, certificat global et fixtures 4 à 10.
- Acceptation : cul-de-sac minimal résolu, non-régressions denses, fallback
  canonique, aucune fausse impossibilité, suite complète et benchmarks bornés.

### P64-V2H03V — Gate Fusion éventuelle

- Statut : `blocked-by-P64-V2H03C`.
- Codex prépare l'add-in et la fixture ; Thomas observe seulement le résultat,
  le diagnostic secondaire, la stabilité de la palette et l'absence de scène
  automatique.
- Cette gate ne calibre aucune valeur et ne vaut pas impression.

## 14. Vérifications minimales des lots runtime

- tests ciblés dérivation/variantes/certificats/portfolio ;
- fixtures P64 historiques et nouvelles ;
- monotonie Rapide/Normal/Approfondi ;
- déterminisme des digests et budgets ;
- stale/annulation ;
- suite complète `unittest` ;
- `compileall` ;
- exemple CLI si une projection est touchée ;
- absence d'import `adsk` dans le cœur ;
- `git diff --check`.

## 15. Hors scope absolu

- modes ou champs P45 dans la palette ;
- formes non rectangulaires, arrondis, chanfreins, encoches ou fonds faciles à
  vider ;
- changement de valeurs physiques, tolérances, jeux ou defaults ;
- overrides externes par conteneur ;
- grille dense, solveur exact, dépendance externe ou preuve mathématique
  produit ;
- P46, P47-P50, P64-F02, P67-P69 ;
- corps, cale, scène ou matérialisation automatique ;
- revendication `fusion-validated` ou `print-validated` sans nouvelle preuve.
