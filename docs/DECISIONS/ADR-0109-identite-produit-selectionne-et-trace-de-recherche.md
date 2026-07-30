# ADR-0109 — Séparer le résultat produit sélectionné de la trace de recherche

## Statut

Acceptée le 2026-07-30 pour clore le diagnostic `tuning-360` et rendre les
panels de performance P64-L09W interprétables.

## Contexte

Les replays C et D de `p64-l09w-tuning-360-c8628c8c54` ont publié trois valeurs
différentes sous le nom `functional_digest`. Les quatre observations historiques
conservent pourtant exactement le même placement, la même route sélectionnée et
le même statut certifié.

Cinq relectures exactes supplémentaires du cas ont ensuite produit des plans
identiques champ par champ. L'inspection du solveur montre que la limite de
temps globale peut interrompre la certification d'une voie non retenue après un
nombre variable de propositions. Cette quantité de travail exploratoire est
conservée dans `search_provenance`, puis incluse dans
`certifiable_payload_digest`.

Le digest complet reste utile : il prouve l'identité de l'artefact et de toute
sa trace. Il ne doit cependant pas être utilisé seul pour décider si le produit
sélectionné a changé.

## Options

### A — Augmenter les budgets jusqu'à stabiliser la trace

Refusée. Cette option masque le problème de mesure, augmente fortement le coût
et ne garantit pas la stabilité à une frontière de temps.

### B — Supprimer la provenance variable du plan complet

Refusée. La provenance et les compteurs sont utiles au diagnostic et à
l'explication des performances.

### C — Publier deux identités séparées

Retenue :

- `selected_product_digest` couvre, par liste autorisée, la géométrie retenue
  et ses contrats produit aval ;
- `execution_trace_digest` conserve l'ancien
  `certifiable_payload_digest` complet ;
- `deterministic` compare désormais le résultat produit sélectionné lorsque la
  nouvelle identité est disponible ;
- `execution_trace_deterministic` publie séparément la stabilité stricte de la
  trace ;
- `execution_route_deterministic` publie séparément la stabilité de la voie
  qui a livré ce produit ;
- les anciens checkpoints restent lisibles par repli sur leur ancien
  `functional_digest`.

## Décision

Une variation de trace sous limite de temps n'est pas une variation
fonctionnelle si le statut, le statut solveur, le produit sélectionné et le
placement restent identiques. La route sélectionnée est une donnée d'exécution :
deux voies peuvent certifier exactement le même produit.

La projection produit est volontairement une liste autorisée. Elle exclut le
digest complet, le résumé des candidats, l'identifiant de requête, les compteurs,
les durées et la provenance de recherche. Elle inclut les placements, les
réservations, les stages, les supports, les résiduels, la validation et les
certificats de géométrie/finalisation du résultat retenu.

Une variation du produit sélectionné reste un arrêt dur. Une variation de trace
ou de route est publiée et peut déclencher un diagnostic de performance, mais
elle ne peut plus être présentée comme un changement de géométrie.

## Conséquences

### Positives

- les panels permanents mesurent séparément qualité produit et comportement
  d'exécution ;
- le cas `tuning-360` n'est plus faussement classé comme géométriquement
  non déterministe ;
- aucune augmentation de budget n'est nécessaire ;
- les traces complètes restent disponibles.

### Limites

- les checkpoints C/D historiques conservent leur ancien nom de champ ;
- l'identité produit ne remplace ni le certificat commun ni le digest complet ;
- tout nouveau champ produit autoritaire devra être ajouté explicitement à la
  projection et couvert par un test.

## Gate

La décision est valide si :

1. modifier uniquement la provenance, les compteurs, le temps, la requête ou le
   digest complet ne change pas `selected_product_digest` ;
2. modifier un placement ou un contrat aval change ce digest ;
3. le runner distingue la stabilité produit de la stabilité de trace ;
4. le holdout reste fermé.
