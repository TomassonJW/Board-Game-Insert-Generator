# P64-L04 — Réutilisation incrémentale d’un agencement minimal

Statut : contrat accepté ; P64-L04A, L04B et L04C automated-validated ; L04V ready-human-gate.

ADR :
[ADR-0075](DECISIONS/ADR-0075-pre-final-local-layout-reuse.md).

## 1. Résultat produit attendu

Lorsqu’un élément est ajouté ou modifié dans un conteneur déjà présent dans un
`minimal_layout` courant, BGIG tente d’abord de mettre à jour uniquement ce
conteneur. Si une disposition locale certifiée tient dans l’enveloppe exacte
déjà placée, le plan monde est recertifié sans lancer la recherche globale.

En cas d’échec, l’édition source est conservée, l’ancien aperçu reste visible
comme obsolète et l’interface demande explicitement `Calculer l’agencement
minimal`. Aucun voisin n’est déplacé automatiquement.

## 2. Distinction avec la capacité post-finalisation

P64-L04 travaille sur les cavités et variantes minimales avant finalisation. Il
ne crée pas de `CapacityOpportunityMap`, ne convertit pas de surplus solide et
n’ouvre ni P64-C01 ni P64-C02. Ces lots restent destinés aux plans finalisés et
à leurs zones de capacité explicites.

## 3. Entrées

- projet source précédent et courant normalisés ;
- `minimal_layout` courant et certifié ;
- frontières locales L01/L02 courantes ;
- placement local et monde de chaque corps ;
- boîte, réservations, jeux globaux et réglages solveur ;
- budget local versionné et observable.

## 4. Statuts publics dérivés

- `not_attempted` : aucune édition locale admissible ou aucun plan courant ;
- `placement_reused` : nouveau plan certifié, placements monde identiques ;
- `global_solve_required` : tentative refusée ou non certifiée ;
- `stale_or_cancelled` : dépendance modifiée pendant la tentative.

Un succès expose au minimum :

```text
placement_reused: true
global_solver_invocation_count: 0
local_recertification_attempt_count: 1
world_placements_changed: false
changed_container_group_ids[]
producer_id + producer_version
budget + counters + stop_reason
source_plan_digest + result_plan_digest
```

## 5. Producteur local à enveloppe fixe

Le producteur `incremental_fixed_envelope_v1` :

1. conserve les origines des cavités toujours présentes lorsque leur géométrie
   courante reste admissible ;
2. place les nouvelles cavités rectangulaires dans les positions de contact
   libres de l’enveloppe existante ;
3. ne change ni pose, dimension résolue, jeu, paroi, fond ou quantité ;
4. ne permute pas Z avec X/Y et ne tourne pas individuellement une cavité ;
5. s’arrête sous des caps déterministes ;
6. repasse par le certificat local commun.

Si cette conservation stricte échoue, l’orchestrateur peut sélectionner une
variante déjà certifiée de la frontière locale ayant exactement la même
enveloppe. Ce fallback peut réorganiser les cavités du seul conteneur ; il ne
déplace jamais son corps monde.

## 6. Conditions du certificat global réutilisé

Le `plan_digest` source doit d’abord être recalculé et égal au digest enregistré.
Le nouveau plan doit ensuite conserver bit-à-bit, pour chaque corps :

- identifiant, rôle et nombre de corps ;
- origine monde ;
- dimensions monde et locales ;
- rotation autour de Z ;
- absence de corps automatique.

Le validateur commun rejoue ensuite boîte, jeux, collisions, appuis,
réservations, retrait, conservation et certificat de sélection des variantes.
La recherche de placement n’est jamais appelée par ce chemin.

## 7. Invalidation

La tentative est refusée avant géométrie si changent :

- boîte ou hauteur utile ;
- réservations supérieures ;
- méthode, effort ou classement ;
- ensemble des conteneurs ou compléments ;
- dimensions ou placement d’un complément ;
- provenance, digest source ou certificat requis absent ou invalide.

Une réussite crée un nouvel artefact global courant. Un plan finalisé devient
obsolète. La CAD IR et la scène deviennent désynchronisées jusqu’à une action
explicite de matérialisation ou mise à jour.

## 8. UX P64-L04A

Après succès :

```text
Élément intégré localement
Placement global conservé
```

Après échec :

```text
Recalcul global requis
Le plan courant ne peut pas être conservé après cette modification.
Lance le calcul de l’agencement minimal.
```

Le détail replié expose conteneurs touchés, producteur, compteurs, motif
d’arrêt et digests. Aucune zone libre n’est présentée comme garantie avant
certification.

## 9. Fixtures obligatoires P64-L04A

1. ajout dans une poche rectangulaire interne, cavités existantes inchangées ;
2. succès avec enveloppe locale et placement monde bit-à-bit identiques ;
3. nouvel asset trop grand : plan stale et solve global non lancé ;
4. modification de boîte ou réservation : tentative non applicable ;
5. nouvel autre conteneur : solve global requis ;
6. certificat local altéré : échec fail-closed ;
7. certificat global ou `plan_digest` source altéré : ancien plan stale ;
8. nouvelle révision et nouveaux digests après succès ;
9. plan finalisé et scène rendus obsolètes sans mutation Fusion ;
10. édition locale via palette : réponse courante sans appel solveur ;
11. fallback de réagencement local à enveloppe identique ;
12. déterminisme et caps ;
13. projet dense inchangé et aucune nouvelle revendication ;
14. `unknown` non promu ;
15. aucune importation `adsk` dans le cœur.

## 10. Découpage

### P64-L04A — Réutilisation locale à enveloppe fixe

- cœur pur, producteur rectangulaire et recertification globale sans recherche ;
- lifecycle staged, bridge et retour UX compact ;
- tests purs, bridge et DOM ;
- aucune nouvelle option de schéma ou forme P45.

### P64-L04B — Approfondi anytime et borné

Statut : `implemented-core`, `automated-validated`.

- Normal devient l’incumbent conservé ;
- Approfondi ajoute trois lanes sans pouvoir perdre une solution déjà obtenue ;
- deadline commune de 30 000 ms, arrêt coopératif et meilleur résultat conservé ;
- caps par lane historiques inchangés ;
- annulation stale distinguée d’une expiration ;
- détail normatif : `docs/P64_L04B_DEEP_ANYTIME_CONTRACT.md` ;
- preuve : `docs/P64_L04B_DEEP_ANYTIME_EVIDENCE.md`.

### P64-L04C — Attente et progression UX

- activité immédiate pour analyse, calcul, finalisation et matérialisation ;
- identité exacte, lifecycle, étape courante, temps écoulé et raison d'arrêt ;
- aucun faux pourcentage ni ETA ;
- aucun bouton Annuler sans sémantique coopérative sûre ;
- stale_or_cancelled reste une invalidation de validité, jamais une annulation
  utilisateur générique ;
- blocage du même type d'opération dans la palette et le bridge, sans verrou
  arbitraire entre types différents ;
- état dérivé non persisté, sans déclenchement de solve, finalisation, CAD ou scène ;
- détails repliés, focus, autosave et actions existantes préservés ;
- preuve : docs/P64_L04C_OPERATION_ACTIVITY_EVIDENCE.md.

### P64-L04V — Gate Fusion

- insertion locale réellement observée ;
- aucun solve global ni déplacement de voisins ;
- fallback explicite lorsque l’ajout ne tient pas ;
- scène ancienne désynchronisée puis mise à jour sans doublon ;
- retour d’attente observé après L04C.

## 11. Hors scope P64-L04A

- solveur Approfondi et budgets historiques ;
- animation, progression ou annulation des opérations longues ;
- finalisation, cales, réserves utiles et cartes de capacité ;
- nouveau conteneur autonome ou déplacement de voisin ;
- formes non rectangulaires et nouvelles intentions P45 ;
- valeurs physiques, tolérances, defaults ou migration de schéma ;
- scène automatique ;
- affirmation d’optimalité, de Fusion-validation ou d’impression.
