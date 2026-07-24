# P64-L08F — tournoi réel 3D, sélection scellée et récupération du verdict

Date : 2026-07-24

Statut : `done`, `automated-validated`, `benchmark-winner-scip`,
`portfolio-rejected`, `product-integration-blocked`, `holdout-consumed`.

## Verdict

SCIP est le meilleur moteur externe retenu par P64-L08F. Sur le holdout de
40 cas limites, il établit 18 vérités contre 0 pour le comportement réel de la
baseline BGIG dans le même protocole, sans perte fonctionnelle.

Le portefeuille SCIP + OR-Tools + LAFF est rejeté : il gagne 5 vérités face à
SCIP seul, mais en perd 3 et ne gagne pas en qualité globale. La règle
préenregistrée impose alors de conserver le meilleur moteur seul.

Le résultat benchmark est positif, mais le résultat produit reste négatif :
SCIP est encore `benchmark-only` tant que les avis et dépendances natives du
paquet Windows ne sont pas finalisés. La décision est donc
`negative_no_product_integrable_winner`. Aucun moteur n'est branché dans BGIG et
aucune gate Fusion n'est ouverte.

## Défaut détecté et récupération

La première postproduction du holdout était invalide. Le worker de baseline
lisait la borne formelle attachée aux 10 cas impossibles et la transformait
directement en `infeasible_proven`, au lieu d'exécuter le solveur BGIG. Cette
baseline n'était donc pas comparable aux moteurs externes.

Le défaut a été corrigé avant commit :

- les entrées worker ne transportent plus `expected` ni
  `formal_negative_bound` ;
- le worker BGIG ne contient plus le raccourci par borne de corpus ;
- les 10 lignes contaminées deviennent honnêtement `bounded_unknown` ;
- le verdict applique la règle écrite avant le holdout : un portefeuille qui ne
  bat pas le moteur principal sans recul est rejeté ;
- le code futur interdit aussi d'autoriser un portefeuille perdant.

La récupération n'a rouvert aucun secret et n'a rappelé aucun worker. Les 80
résultats externes sont inchangés, la sélection, les routes, les graines et les
caps sont inchangés, et aucun tuning postérieur n'a eu lieu. Une garde statique
vérifie que les quatre workers externes exécutés ne lisaient pas ces métadonnées
de corpus. Le premier digest public
`508c9b1e8834051c22b9c168055d87abb8319785be7d0346cf7159b687db89bb`
est conservé dans le reçu comme preuve invalidée, jamais comme verdict.

## Protocole réellement exécuté

Quatre moteurs externes distincts ont été comparés hors ligne avec une entrée
X/Y/Z, les mêmes limites de ressources et la même recertification BGIG :

- OR-Tools CP-SAT, formulation par contraintes entières et SAT ;
- SCIP, formulation CIP/MIP ;
- PackingSolver `box`, recherche arborescente 3D spécialisée ;
- LAFF, heuristique 3D par niveaux.

La campagne ouverte a exécuté, dans l'ordre :

1. 24 petits contrôles exacts ;
2. 120 lignes de discovery, soit 30 cas par moteur ;
3. 80 lignes de tuning, soit 10 cas XL avec deux graines par moteur ;
4. la baseline BGIG sur les mêmes splits ;
5. une sélection scellée avec code, artefacts, caps, graines et digests ;
6. une seule ouverture du holdout privé de 40 cas ;
7. 120 lignes de holdout : portefeuille, SCIP seul, puis BGIG actuel.

Le holdout a été ouvert exactement une fois. Chaque cas du portefeuille appelle
un seul moteur ; un seul processus lourd a tourné à la fois, avec 1 thread,
1 024 Mio et au plus 30 secondes par cas. Aucun service, compte, secret, trafic
réseau ou installation globale n'a été utilisé.

## Résultats ouverts

| Étape | Moteur | Cas | Représentables | Vérités | Solutions certifiées | Échec worker |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Discovery | OR-Tools | 30 | 30 | 16 | 7 | 0 |
| Discovery | SCIP | 30 | 30 | 19 | 13 | 0 |
| Discovery | PackingSolver | 30 | 3 | 2 | 2 | 0 |
| Discovery | LAFF | 30 | 3 | 2 | 2 | 0 |
| Tuning XL, deux graines | OR-Tools | 20 | 20 | 0 | 0 | 0 |
| Tuning XL, deux graines | SCIP | 20 | 20 | 0 | 0 | 0 |
| Tuning XL, deux graines | PackingSolver | 20 | 2 | 2 | 2 | 0 |
| Tuning XL, deux graines | LAFF | 20 | 2 | 2 | 2 | 0 |

OR-Tools et SCIP couvrent toutes les sémantiques, mais ne trouvent aucune
solution XL dans les deux budgets de 30 secondes. PackingSolver et LAFF ne
représentent fidèlement que la famille `many-containers` ; leurs autres cas
restent `unsupported`, jamais simplifiés. LAFF gagne cette famille ouverte et
résout son cas XL.

La sélection scellée choisit SCIP comme moteur principal, OR-Tools et LAFF comme
compléments. Les routes sont déterminées avant le holdout : OR-Tools pour
`access`, `fragmentation`, `layers`, `mixed-extreme`, `support` et `variants` ;
SCIP pour `many-assets`, `real-anonymized` et `reservations` ; LAFF pour
`many-containers`.

## Résultats du holdout

| Système | Cas | Vérités | Solutions certifiées | Temps total |
| --- | ---: | ---: | ---: | ---: |
| Portefeuille scellé | 40 | 20 | 12 | 654,304 s |
| SCIP seul, retenu | 40 | 18 | 12 | 771,490 s |
| BGIG actuel corrigé | 40 | 0 | 0 | 4,748 s |

Comparaisons contractuelles :

- portefeuille contre SCIP : 5 gains, 3 pertes, un gain de qualité et une perte
de qualité ; `portfolio_beats_primary=false` ;
- SCIP contre BGIG : 18 gains, 0 perte ; `no_functional_loss=true` et
  `benchmark_winner_demonstrated=true` ;
- les 40 lignes BGIG corrigées sont `bounded_unknown` : le solveur interne n'a
  certifié aucun cas positif et ne possède pas de preuve formelle pour les cas
  négatifs ;
- aucun worker externe n'a échoué.

Le succès SCIP porte principalement sur les paliers small et large. Les cas XL
généraux restent souvent `bounded_unknown` au plafond de 30 secondes. Le
benchmark ne permet donc aucune promesse de « remplissage ultime » sur tous les
XL ; il désigne seulement le meilleur moteur réellement mesuré sous ces caps.

## Digests et invariants

- sélection scellée :
  `e061f9af67e9ce80974a8ea2c5fe705ba59a637dbba319464a412651b6fa7140` ;
- reçu d'ouverture unique :
  `e5a52f3ec34167e631cdf2109f5681cfb1b6ee9f2f1820334c011e481ba53444` ;
- campagne brute :
  `1b9e2c722e43632fa44c56046cbba6098d406577694bfd846c09730c895c448c` ;
- preuve récupérée :
  `0dbf1b45ae9135c1316051ab7e0946dfbfeafac5c785ad96ccd5d7a620acd46d` ;
- reçu de récupération :
  `0fc672b479074f446d333bf3a8ac4bd16f8e3caeadb8f70dec4fcd9a939e5001` ;
- ouverture privée : 1 ; réouverture privée : 0 ;
- réexécution worker externe : 0 ; réexécution baseline : 0 ;
- tuning après ouverture : 0 ; sélection ou route modifiée : false.

La preuve publique compacte ne contient ni recette, ni nonce, ni placement, ni
témoin privé du holdout.

## Artefacts

- `src/board_game_insert_generator/real_3d_solver_tournament.py` : problèmes
  négatifs concrets, métriques, sélection, fallback et comparaisons ;
- `scripts/solver/run_real_3d_solver_tournament.py` : campagne ouverte,
  checkpoints, reprise sans double exécution et ouverture unique ;
- `scripts/solver/recover_real_3d_solver_tournament.py` : récupération bornée,
  sans worker ni secret ;
- `scripts/solver/external_workers/bgig_real_3d_worker.py` : baseline interne
  isolée, non comptée comme concurrent externe ;
- `tests/fixtures/p64_l08f_real_3d_tournament_config.v1.json` : caps et graines ;
- `tests/fixtures/p64_l08f_real_3d_selection.v1.json` : sélection scellée ;
- `tests/fixtures/p64_l08f_holdout_opening_receipt.v1.json` : ouverture unique ;
- `tests/fixtures/p64_l08f_holdout_recovery_receipt.v1.json` : invalidation et
  récupération sans réexécution ;
- `tests/fixtures/p64_l08f_real_3d_tournament_evidence.v1.json` : preuve
  récupérée, sans secret de holdout ;
- `tests/test_real_3d_solver_tournament.py` : contrats, digests et verdict.

## Validations

- compilation Python des modules, workers, runners et tests L08F : OK ;
- `ruff format` et `ruff check` : OK ;
- tests ciblés `test_real_3d_solver_*.py` : 24/24 en 2,141 s ;
- garde documentaire : 1/1 ; alignement Fusion-only : 6/6 ;
- suite complète en cinq partitions disjointes : 793/793 en 284,127 s
  cumulées, cinq codes de sortie 0 ;
- `git diff --check` : OK.
## Limites et décision L08G

Le benchmark désigne SCIP, mais la preuve scellée ne l'autorise pas encore au
produit. P64-L08G doit donc soit satisfaire explicitement la gate de
redistribution Windows sans modifier le moteur, les caps ni les résultats, soit
clore sans intégration. Aucun autre candidat ne peut être substitué après
lecture du holdout.

Aucun budget, certificat, schéma, tolérance, géométrie, propriété P45/P64, CAD,
scène ou valeur physique n'est modifié par L08F. Tant qu'aucun package produit
conforme n'est intégré et testé, aucune installation Fusion ne doit être
préparée. `fusion-validated=false` et `print-validated=false` restent inchangés.
