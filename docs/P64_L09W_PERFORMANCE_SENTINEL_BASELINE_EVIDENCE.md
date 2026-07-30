# P64-L09W — Baseline et seuils du panel sentinelle

Date : 2026-07-30.

Statut : `baseline-complete`, `thresholds-frozen`, `holdout-sealed`.

## Verdict

Le panel permanent est opérationnel :

- 16/16 sentinelles complètes ;
- 5 répétitions par cas, soit 80 calculs ;
- 8 cas `common` et 8 cas `stress` ;
- zéro échec fonctionnel ;
- une seule identité produit sélectionnée par solution certifiée ;
- 10 résultats prêts hors Fusion dans l'état courant ;
- aucun accès au holdout.

Rapport local autoritaire :

- digest :
  `99d0360e196e0939bdeadf11723a5a49d293e757a7a7dd51421c3fed3512d75b` ;
- checkpoint :
  `bf3b0bf4f3c1364b44f89b2f34e2671e6d2efc386d4258ec28a326539eb9eba9`.

Le rapport reste dans `.codex-work` car il contient les 80 mesures brutes. Les
identités, échantillons et seuils nécessaires aux futures comparaisons sont
gelés dans la fixture versionnée.

## Corrections révélées par la baseline

La campagne a volontairement arrêté sur chaque incohérence avant de continuer.
Elle a révélé trois erreurs de classification :

1. le runner C faisait une copie superficielle du plan avant la finalisation du
   premier replay ; une copie profonde isole désormais le plan minimal ;
2. `global_certificate.candidate_digest` engage la trace complète du candidat,
   pas uniquement le produit retenu ; l'identité produit v2 conserve les checks
   du certificat mais exclut ce digest parasite ;
3. deux voies différentes peuvent certifier exactement le même produit ; la
   stabilité de route est maintenant publiée séparément de la stabilité
   fonctionnelle.

Un contrôle `bounded_unknown` ne doit pas posséder de placement. La gate exige
donc exactement une identité et un placement pour une solution certifiée, mais
au plus une identité pour un résultat borné.

Le cas lourd `p64-l09w-tuning-277-a66af911e7` a été refusé comme sentinelle :
ses deux replays C étaient certifiés vers 50–53 s, mais cinq replays courants
étaient tous bornés vers 21 s. Il a été remplacé avant gel par
`p64-l09w-tuning-300-cf933fb090`, issu de l'échantillon causal stratifié et
reproductible sur cinq répétitions.

Les 15 résultats v5 encore compatibles ont été réutilisés par un checkpoint
semé, avec engagement du digest source. Seule la nouvelle sentinelle a été
recalculée. Aucun résultat en échec ou interrompu n'a été importé.

## Variance mesurée

Temps total de calcul des 16 cas, par répétition alignée :

- minimum : `180 382,987 ms` ;
- médiane : `181 092,463 ms` ;
- maximum : `183 510,662 ms` ;
- MAD : `480,174 ms`.

Par strate :

- `common` : médiane `49 006,695 ms`, MAD `121,409 ms` ;
- `stress` : médiane `132 085,768 ms`, MAD `271,483 ms`.

Deux cas ont produit plusieurs digests de trace, mais une seule identité produit
et un seul placement. Cette variation reste une donnée d'exécution.

## Méthode de seuil

Aucune marge fixe `±5 %` n'est utilisée.

Pour chaque cas :

1. calcul de la médiane et de la MAD sur cinq répétitions ;
2. conversion de la MAD en sigma robuste par `1,4826` ;
3. borne unilatérale normale à 99 % ;
4. correction de Bonferroni sur 16 cas ;
5. marge retenue égale au maximum entre la borne statistique et le plus grand
   écart supérieur réellement observé.

La même méthode est appliquée au total du panel et aux deux strates, avec leurs
niveaux de multiplicité.

Bornes agrégées gelées :

- total : `183 510,662 ms`, soit `+1,335 %` sur la médiane mesurée ;
- `common` : `49 470,347 ms`, soit `+0,946 %` ;
- `stress` : `134 426,784 ms`, soit `+1,772 %`.

Les ratios individuels varient honnêtement de `+0,34 %` à `+33,09 %`. Le plus
grand ratio appartient au cas de 8 ms, où quelques millisecondes représentent
une forte proportion mais un faible coût absolu.

## Règles futures

Un candidat sentinelle passe uniquement si :

- toutes les gates fonctionnelles passent ;
- la médiane de chacun des 16 cas reste sous sa borne corrigée ;
- les médianes totales `overall`, `common` et `stress` restent sous leurs
  bornes.

Le panel 48 n'est exécuté qu'après ce passage. Il reste une confirmation
fonctionnelle et représentative ; il ne produit aucun taux global. Les 400 cas
ouverts restent réservés à un changement global ou au candidat gelé avant E.

## Preuves versionnées

- plan :
  `tests/fixtures/p64_l09w_performance_panels.v1.json` ;
- seuils :
  `tests/fixtures/p64_l09w_performance_thresholds.v1.json` ;
- digest du plan :
  `d427e148a194d6dec66bf354e287604e6f5446eb50c7e083682419187a36e528` ;
- digest des seuils :
  `beac00108140b72a625c7f756b9c27d70e50701ac9c34860743ab703254a4b72`.

Évaluation du rapport autoritaire contre les seuils gelés :
`passed`, zéro échec.

## Vérifications de clôture

- tests ciblés panels, runner, identité, seuils et D : `34/34`, OK ;
- tests documentaires : `11/11`, OK ;
- suite complète canonique avec `PYTHONPATH=src;.` :
  `1093/1093`, `1` skip prévu, OK en `622,557 s` ;
- compilation Python des scripts et modules concernés : OK ;
- régénération bit à bit du plan et des seuils : OK ;
- `git diff --check` : OK ;
- holdout : zéro lecture, ouverture ou invocation.
