# P64-L09R-V 0.1.65 — KO humain et causes du nouveau programme

## 1. Statut

- Date : 2026-07-25.
- Gate : `human-KO`, `suspended`, non acceptée.
- Package observé : 0.1.65.
- Effet : P64-L09R-V ne doit pas être reprise avec cette architecture.
- Impression : `print-validated=false`.

Cette preuve consigne les faits observés et lus dans les journaux locaux. Aucun
snapshot, projet personnel ou witness local n'est versionné.

## 2. Cas plateau observé

Le projet contient 18 conteneurs, 20 contenus et un plateau de 1 mm. La boîte
offre 59,6 mm de hauteur utile.

Sans plateau, le witness certifié culmine à 52,8 mm et conserve
778 926,416 mm³ de volume résiduel.

Avec plateau, le calcul 0.1.65 trouve une solution, mais :

- `container-018` est placé à Z = 21,2 mm ;
- son enveloppe XY reste 23,2 × 23,2 mm ;
- sa hauteur minimale de 31,6 mm devient 38,4 mm ;
- son sommet atteint artificiellement 59,6 mm ;
- une encoche de 21,4 × 23,2 × 1 mm est créée ;
- la couverture de plateau rapportée n'est que 0,0075, soit 0,75 % ;
- le diagnostic `TOP_INSET_LOW_SUPPORT_COVERAGE` est présent ;
- le résiduel tombe à 775 266,384 mm³.

La différence de résiduel est exactement :

```text
778 926,416 - 775 266,384
= 3 660,032 mm³
= 23,2 × 23,2 × 6,8
```

Le calcul minimal a donc attribué au hasard de la règle de support un volume qui
devait rester résiduel jusqu'à la finition.

## 3. Cause technique du plateau

Dans `scip_product_solver.py`,
`_invoke_worker_with_top_inset_compensation` :

1. retire les `top_inset_zones` ;
2. résout le plan minimal ;
3. appelle `_apply_required_top_inset_z_compensation` ;
4. choisit un conteneur recouvrant partiellement le plateau ;
5. remplace sa hauteur par celle nécessaire pour atteindre `design_top_z`.

Dans le worker SCIP, `_add_top_inset_constraints` impose également au moins un
support par zone et exige qu'il atteigne le sommet de conception.

Les deux chemins implémentent donc une obligation de support qui n'appartient
pas au besoin produit confirmé par Thomas.

## 4. Finition observée

Trois tentatives récentes de finition ont duré environ 9,0 s, 9,0 s et 16,0 s.
Elles conservent le même plan minimal :

- digest du plan : `1cdc48741fb7c6875ee6c5abe634365872a415617cda91d6d86380668f40e751` ;
- digest de l'artefact :
  `9bf13e9fb752cd8bfa6426a445f02303cb2d4aea1415c7846a9efec83f4220d9`.

Chaque tentative se termine par :

- `no_solution_within_budget` ;
- stop reason `printable_residual_remains` ;
- aucun `finalized_plan` publié ;
- 775 266,384 mm³ encore résiduels.

Le plan minimal est bien conservé, ce qui confirme l'acquis non destructif de
P64-L09R-C.

## 5. Cause technique de la finition

`coupled_finalization.py` exige d'abord que
`close_free_3d_residual(..., closure_only)` ne laisse aucun espace. Si cette
baseline gloutonne échoue, la fonction lève immédiatement
`CoupledFinalizationError`.

Les objectifs équilibré et proportionnel ne sont donc évalués qu'après une
fermeture déjà complète. Ils ne peuvent pas aider à la construire.

La croissance locale par faces n'est pas une méthode globale de partition :
elle peut fragmenter les espaces et rester bloquée malgré un volume total
suffisant.

## 6. Résultat UI trompeur

Le bridge garde le plan minimal et ne renvoie aucune partition finale. Malgré
cela :

- `_operation_stop_reason("finalize_project", ...)` renvoie toujours
  `finalized_plan_ready` dès que la réponse bridge vaut `ready` ;
- le chemin générique de la palette affiche `Projet accepté`.

La couche transport est donc confondue avec le succès métier.

## 7. Référence historique utile

Le `partition_solver.py` du commit `bd0e09b` :

- construisait plusieurs découpages en lignes ;
- distribuait le surplus X entre les conteneurs extensibles ;
- distribuait le surplus Y entre les lignes extensibles ;
- portait chaque corps à la hauteur de rangement ;
- validait une partition complète avant publication.

Ce principe explique son comportement propre de bout en bout. Il n'est toutefois
pas réutilisable tel quel : il suppose une partition 2D par lignes et une
hauteur commune, donc ne couvre pas les plans 3D complexes actuels.

## 8. Conclusion

La bonne trajectoire n'est ni un retour au vieux solveur, ni un nouveau choix de
conteneur porteur. Elle est hybride :

1. SCIP conserve le solve minimal complexe ;
2. les plateaux deviennent des réservations sans croissance de support ;
3. un finaliseur global cherche une couverture complète et équilibrée ;
4. des annexes XY soudées et certifiées sont permises seulement en repli ;
5. la matérialisation suit exactement le certificat final ;
6. l'interface dit la vérité à chaque étape.

ADR-0089 et le Goal P64-L09S portent cette correction.
