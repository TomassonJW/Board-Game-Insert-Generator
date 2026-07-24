# P64-L07 — rapport final du Goal externe

Date : 2026-07-23

Statut historique : `done`, `automated-validated`, `partial-floor-benchmark`,
`highs-specialized-lane`.

> **Correction de portée — 2026-07-24.** ADR-0083 et le programme P64-L08 remplacent la conclusion `external-benchmark-complete` pour le solvage global BGIG. Les preuves ci-dessous restent valides pour le sous-problème rectangulaire à un niveau, mais ne classent plus un moteur 3D ni la performance des cas limites.

`fusion-validated: false`

`print-validated: false`

## 1. Réponse courte

Le benchmark externe de lane de sol est terminé. Il est insuffisant pour la gate réelle de solvage 3D ; voir `docs/P64_L07_SCOPE_CORRECTION.md` et `docs/P64_L08_REAL_3D_SOLVER_BENCHMARK_PROGRAM.md`.

- dix candidats crédibles ont été audités ;
- quatre moteurs externes réels de quatre familles ont été exécutés ;
- le corpus BGIG V2 utilise deux sources publiques et un nouveau holdout ;
- la sélection a été scellée avant une ouverture unique du holdout ;
- HiGHS 1.15.1 gagne la gate produit et est intégré seul ;
- chaque sortie positive reste certifiée par BGIG ;
- le produit reste local et hors ligne ; BGIG ne lance aucune installation
  globale et échoue fermé si le runtime Windows requis manque.

P64-L06 reste une expérience interne valide mais ne compte pas comme ce
benchmark externe.

## 2. Missions exécutées

| Mission | Résultat |
| --- | --- |
| L07A | 10 candidats audités, 5 shortlists dans 5 familles |
| L07B | corpus V2, 2 sources publiques, holdout neuf scellé |
| L07C | 4 moteurs et 4 familles réellement adaptés |
| L07D | tournoi progressif, sélection scellée, holdout ouvert une fois |
| L07E | gate produit, ADR, paquet hors ligne, fallback et intégration HiGHS |

Commits déjà intégrés avant L07E :

- L07A : `3395e19f91d89659cffbe6f9f988d976664779ad` ;
- L07B : `b121a3dc445042b2213f4674120476bbc426fb86` ;
- L07C : `d4474c302e9f63972855a50d962c6f05516def65` ;
- L07D : `a5a7dfeeeecbda0d10149f7e7d79fb337da1ea3f`.

Le SHA L07E est le commit qui contient ce rapport ; sa vérification distante est
consignée dans le compte rendu de clôture.

## 3. Audit des candidats

| Candidat | Famille | Décision finale |
| --- | --- | --- |
| PackingSolver | placement spécialisé | audité, non adapté au tournoi final |
| LAFF 4.2.1 | niveaux / énumération | benchmark-only |
| OR-Tools CP-SAT 9.15 | contraintes | candidat produit non retenu |
| SCIP 10.0.2 | CIP/MIP | benchmark-only |
| HiGHS 1.15.1 | MIP | gagnant intégré |
| Choco 6.0.1 | domaines finis | benchmark-only, non exécuté |
| Chuffed | clauses paresseuses | benchmark-only, non exécuté |
| CBC 2.10.13 | branch-and-cut | gate copyleft, non exécuté |
| Timefold 2.3.0 | métaheuristiques | rejeté |
| py3dbp 1.1.2 | heuristique simple | rejeté |

Les filtres de licence, redistribution, plateforme et maintenance ont précédé
les acquisitions coûteuses.

## 4. Corpus et vérité

Le manifest V2 conserve huit régressions BGIG et ajoute :

- 192 cas BGIG T0/T1 ;
- huit contrôles publics issus de THPACK9 et Q4RealBPP ;
- un nouveau holdout indépendant de 64 cas ;
- des témoins locaux et globaux pour les cas faisables ;
- des bornes exactes de volume ou de hauteur pour les cas impossibles.

Les contrôles publics servent à vérifier les méthodes. Ils ne sont pas utilisés
pour classer le produit lorsqu'un objectif ne correspond pas exactement à
BGIG.

Le holdout L06 est resté interdit. Le holdout L07 a été ouvert une seule fois
après scellement du candidat, des réglages, du code et du corpus. Il est
désormais consommé et ne doit jamais être rouvert pour régler HiGHS.

## 5. Concurrence réellement exécutée

| Moteur | Famille | Contrôles réels | Gate produit |
| --- | --- | ---: | --- |
| OR-Tools CP-SAT | contraintes | 12/12 | admissible, non retenu |
| HiGHS | MIP | 12/12 | admissible, retenu |
| SCIP | CIP/MIP général | 12/12 | benchmark-only |
| LAFF | niveaux / packing | 12/12 | benchmark-only |

BGIG et le petit oracle interne sont restés des références. Ils ne comptent pas
dans ces quatre concurrents.

Toutes les solutions positives ont été reconstruites puis recertifiées par
`bgig.minimal_layout_certificate.v1`.

## 6. Tournoi ouvert et sélection

Résultats de la portée sans perte :

| Moteur | Discovery | Tuning |
| --- | ---: | ---: |
| SCIP | 8/8 | 6/7 |
| HiGHS | 8/8 | 5/7 |
| LAFF | 7/8 | 7/7 |
| OR-Tools | 3/8 | 2/7 |

SCIP et LAFF sont exclus du produit par leurs gates de redistribution. HiGHS
est donc le meilleur candidat produit. OR-Tools ne gagne aucune famille
distincte et aucun portefeuille ne bat HiGHS seul sous une enveloppe totale
comparable.

La sélection scellée retient HiGHS seul.

## 7. Holdout

Sur les 64 cas neufs :

- 7 sont fidèlement représentables par la route scellée ;
- 5 donnent une solution certifiée ;
- 2 restent `bounded_unknown` ;
- 0 sortie invalide ;
- 0 erreur candidat ;
- 0 réglage après ouverture ;
- 0 double exécution pendant la reprise.

Ce résultat confirme le candidat mais ne prouve pas seul un gain produit :
l'interdiction de rotation de ces cas n'existe pas dans le schéma BGIG V1.

## 8. Gate produit

Une gate séparée utilise cinq régressions communes réellement représentables :

- égalité sur la vérité et le nombre de solutions certifiées ;
- 2 gains de qualité HiGHS ;
- 0 perte ;
- fragmentation résiduelle 0 contre 5 sur les deux solutions communes ;
- 1,308987 s contre 4,077502 s observés au total.

Décision : `product_gain_demonstrated=true`.

## 9. Intégration retenue

HiGHS 1.15.1 est embarqué comme CLI officiel Windows x86_64 MIT :

- archive verrouillée par SHA-256 ;
- exécutable et DLL verrouillés par SHA-256 ;
- licences et avis redistribués ;
- 11 307 594 octets dans le paquet versionné ;
- add-in Fusion 0.1.60 ;
- aucun compte, service, secret, réseau ou installateur global déclenché par
  BGIG ; Universal CRT et Visual C++ Runtime 14 doivent déjà être présents.

La lane HiGHS :

- propose seulement un placement de sol rectangulaire ;
- est appelée au plus une fois ;
- possède ses propres caps additionnels ;
- ne modifie aucun cap historique des lanes BGIG ;
- repasse par le certificat commun ;
- laisse ensuite toutes les lanes internes concourir ;
- échoue fermé vers BGIG.

ADR : `docs/DECISIONS/ADR-0082-highs-offline-product-lane.md`.

## 10. Validation et limites

La validation finale comprend :

- vrai binaire, licences et empreintes : OK ;
- imports PE inventoriés et runtime Windows local 14.44.35211.0 : OK ;
- équivalence CLI avec l'adapter scellé : 3 contrôles et 8 régressions,
  aucune différence ;
- gate du runtime final : 5 cas, 2 gains, 0 perte, 0 changement de statut ;
- tests de la lane, du fallback et des preuves : 9/9 ;
- packaging Fusion staging 0.1.60 : OK ;
- Ruff et compilation Python ciblés : OK ;
- garde documentaire : 2/2 ; alignement Fusion-only : 6/6 ;
- suite complète : 765/765 en 228,071 s ;
- diff-check et vérification Git distante : clôture Git de L07E.

Limites maintenues :

- T0/T1 seulement ;
- aucune forme T2 à T4 ;
- aucune auto-modification ;
- aucun changement de certificat, tolérance, propriété P45/P64, finalisation,
  CAD, scène ou valeur physique ;
- aucune nouvelle revendication dense 11 × 34 ;
- aucune validation Fusion ou impression.

## 11. Conclusion

Le benchmark est honnêtement complet : il dépasse le minimum de trois vrais
concurrents externes et aboutit à une intégration mesurée. Un seul moteur est
retenu parce qu'aucun complément ne démontre de gain distinct.

La prochaine étape est une observation humaine P64-L07V dans Fusion 360 sur le
package 0.1.60. Elle ne conditionne pas la clôture automatisée du Goal et ne
vaut jamais validation d'impression.
