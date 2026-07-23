# P64-L07D — preuve du tournoi externe

Date : 2026-07-23

Statut : `done`, `automated-validated`, `holdout-consumed`.

`fusion-validated: false`. `print-validated: false`.

## Résultat en une phrase

Quatre vrais moteurs externes de quatre familles ont été comparés. HiGHS est le
meilleur candidat encore intégrable dans le produit, mais le tournoi ne démontre
pas encore un gain produit face à BGIG : tous les cas communs de sélection
interdisent la rotation par une propriété que le schéma produit ne sait pas
exprimer.

## Concurrents réels

| Moteur | Famille | Gate produit | Discovery | Tuning retenu |
| --- | --- | --- | ---: | ---: |
| OR-Tools CP-SAT 9.15.6755 | contraintes / SAT hybride | candidat | 3/8 | 2/7 |
| HiGHS 1.15.1 | programmation linéaire entière | candidat | 8/8 | 5/7 |
| SCIP 10.0.2 / PySCIPOpt 6.2.1 | CIP / MIP | benchmark-only | 8/8 | 6/7 |
| LAFF 4.2.1 | heuristique spécialisée | benchmark-only | 7/8 | 7/7 |

BGIG et l'oracle interne ne sont pas comptés dans ces quatre concurrents.
`bounded_unknown` reste un non-succès honnête. Une sortie positive compte
uniquement après un nouveau certificat BGIG.

SCIP reste exclu de l'intégration tant que l'inventaire des licences des
binaires natifs embarqués n'est pas complet. LAFF reste exclu tant que la
redistribution EPL/EDL d'Eclipse Collections et le paquet Java complet ne sont
pas tranchés. Ces exclusions existaient avant le classement.

## Corpus réellement utilisé

- trois petits contrôles exacts par moteur, soit 12 résultats attendus sur 12 ;
- huit régressions historiques, dont cinq représentables par le modèle sol ;
- 64 cas `discovery`, dont huit représentables sans perte de contrainte ;
- 64 cas `tuning`, dont sept représentables sans perte de contrainte ;
- deux essais de tuning annoncés avant mesure, graines `640707` et `640708` ;
- 64 cas de holdout ouverts une seule fois après le scellement, dont sept
  représentables.

Les autres cas ne sont pas transformés en problèmes plus simples : ils restent
`unsupported` ou `invalid_input`. Le tournoi ne revendique donc pas une
couverture de 64/64.

## Deux sources publiques

Les artefacts officiels ont été revérifiés par taille et SHA-256 :

- OR-Library THPACK9 : 47 instances analysées, contrôles 1 à 4 liés à une
  réduction exacte de décision à nombre de conteneurs fixé ;
- Q4RealBPP V1 : quatre entrées mono-bin `1`, `3`, `5` et `7` vérifiées dans
  l'archive officielle.

Ces huit cas sont des contrôles de méthode. Ils ne classent pas le produit,
car leurs objectifs et contraintes n'incluent ni support BGIG, ni ordre de
retrait, ni réservations, ni variantes locales P45. Aucun score produit n'est
inventé à partir de cette projection.

## Ressources ouvertes

Enveloppe par exécution : 3 s, 1 thread, 1 024 Mio, un seul processus lourd à
la fois. Les temps ci-dessous sont les sommes mesurées sur la portée
représentable.

| Moteur | Discovery | Tuning retenu | Pic mémoire observé | Paquet verrouillé |
| --- | ---: | ---: | ---: | ---: |
| OR-Tools | 18,843 s | 15,754 s | 104 173 568 octets | 49 821 428 octets |
| HiGHS | 17,475 s | 15,043 s | 82 485 248 octets | 15 612 832 octets |
| SCIP | 17,026 s | 14,492 s | 149 889 024 octets | 61 194 406 octets |
| LAFF | 1,960 s | 1,787 s | 99 815 424 octets | 204 015 872 octets |

LAFF est le plus rapide et résout 7/7 au tuning, mais ne passe pas sa gate de
redistribution. SCIP obtient 6/7, mais reste lui aussi benchmark-only. Parmi les
candidats produit, HiGHS domine OR-Tools.

## Sélection scellée avant holdout

Le commit `acdee83570f7fe89305d76811d33b1b06653dec6` contient la
sélection avant toute lecture du sidecar :

- candidat principal : `highs` ;
- réglage retenu : graine `640708` ;
- limite holdout : 3 s, 1 thread, 1 024 Mio, graine `640709` ;
- complément : aucun ;
- routeur : HiGHS seul, au plus une invocation par cas ;
- digest de sélection :
  `b2f7fa79d96a6facbfc814bb408076a245d7964bfc4d723c3f1b4ad0fbcb634e` ;
- digest du code scellé :
  `57abfc4ce47c6cc99df6c52c3cf987535f113dfdb26769327ad64d8372622cb7`.

OR-Tools ne gagne aucune famille du tuning face à HiGHS. Un portefeuille ne
bat donc pas le meilleur moteur seul sous une seule invocation par cas.

## Holdout unique

Résultat sur les sept cas représentables :

- cinq solutions certifiées ;
- deux `bounded_unknown` après la limite de 3 s ;
- zéro sortie invalide ;
- zéro rejet du certificat ;
- zéro erreur candidat.

Sur les 64 entrées complètes :

- 55 `unsupported` ;
- 2 `invalid_input` déjà déterminés par le corpus ;
- 5 `solution_found` certifiés ;
- 2 `bounded_unknown`.

Digest de campagne :
`bcc4e85a3175943fbf1ee85692ef91c861cc22856be22f89b3d8b3049f1e369d`.

## Comparaison avec BGIG

Les huit cas discovery, sept cas tuning et sept cas holdout dans la portée sol
portent tous `rotation_policy_target=forbidden_by_benchmark`. Le schéma projet
V1 ne sait pas désactiver la rotation. L'adapter BGIG refuse donc ces cas au
lieu d'ignorer silencieusement la contrainte.

Conséquence : `product_gain_demonstrated=false`. Les succès HiGHS prouvent sa
capacité sur le modèle scellé, pas encore une amélioration du produit courant.
L07E doit comparer HiGHS et BGIG sur des entrées produit représentables, puis
refuser l'intégration si aucun gain réel, répété et rentable n'apparaît.

## Reprise du post-traitement

Après les 64 entrées, le rapporteur initial a rencontré un `TypeError` en
additionnant le temps `null` normal des lignes `unsupported`. Aucun résultat
du holdout n'a été consulté avant la correction de reprise.

La reprise :

- n'a changé ni candidat, ni routeur, ni réglage ;
- n'a exécuté aucun tuning après ouverture ;
- a réutilisé les sept checkpoints externes et les sept checkpoints BGIG ;
- n'a relancé aucun moteur ;
- a seulement reconstruit l'agrégat à partir des rapports scellés.

Le reçu
`tests/fixtures/p64_l07d_holdout_recovery_receipt.v1.json` porte le digest
`117e9c011678859ea3d1f41b2c04bc214a541743ed7e0c65fa4647eeafe7b220`.

## Soak

Aucun soak n'est lancé. Les deux non-résolutions HiGHS sont des limites de
temps déjà observées au tuning, pas une instabilité de résultat. Un soak
n'aurait pas le droit de modifier le réglage après holdout.

## Preuves versionnées

- `tests/fixtures/p64_l07d_external_tournament_config.v1.json` ;
- `tests/fixtures/p64_l07d_external_tournament_selection.v1.json` ;
- `tests/fixtures/p64_l07d_external_tournament_evidence.v1.json` ;
- `tests/fixtures/p64_l07d_holdout_recovery_receipt.v1.json`.

## Validation

- tests externes ciblés : 40/40 en 33,088 s ;
- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- suite complète : 756/756 en 230,824 s ;
- compilation Python ciblée et `git diff --check` : OK.

## Décision L07D

Le vrai benchmark externe est exécuté avec quatre concurrents. HiGHS est le
gagnant intégrable du laboratoire et passe en L07E. Il n'est pas encore adopté
par le produit. L07E conserve le droit et l'obligation de conclure
`benchmark-winner-not-integrated` si les gates produit, packaging, fallback ou
gain réel échouent.
