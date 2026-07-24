# P64-L08G — gate produit SCIP Windows/Fusion

Date : 2026-07-24

Statut : `done`, `automated-validated`, `benchmark-winner-scip`,
`negative-no-product-integrable-winner`, `no-fusion-gate`.

`fusion-validated: false`

`print-validated: false`

## Verdict

SCIP 10.0.2 reste le gagnant réel du benchmark P64-L08F : cette décision n'est
ni annulée ni modifiée. En revanche, le runtime Windows acquis pour le tournoi
ne peut pas être intégré honnêtement dans BGIG.

La gate produit échoue sur quatre motifs indépendants :

1. PySCIPOpt est un wheel `cp310`, alors que Fusion 2704.1.36 embarque
   `python314.dll` ; le module natif ne peut pas être chargé par l'add-in ;
2. les versions exactes d'Ipopt, MUMPS et de plusieurs runtimes Intel ne sont
   pas liées par les métadonnées du wheel ;
3. le wheel PySCIPOpt ne contient que sa licence MIT, sans les avis SCIP,
   Ipopt, MUMPS, Intel ou Microsoft nécessaires aux DLL qu'il redistribue ;
4. l'autorité de redistribution de ces binaires précis n'est donc pas établie
   sans hypothèse.

Décision : `negative_no_product_integrable_winner`. Aucun moteur externe 3D
n'est ajouté au produit, aucune gate Fusion n'est préparée ou installée, et les
lanes BGIG actuelles restent inchangées.

## Paquets audités

| Paquet | Taille wheel | Taille décompressée | ABI | SHA-256 |
| --- | ---: | ---: | --- | --- |
| PySCIPOpt 6.2.1 | 48 289 786 octets | 144 503 392 octets | `cp310-win_amd64` | `d83d1cc9cc6d9a840cee71f4b19174cf01a54f004148a29725e2464e17011f59` |
| NumPy 2.2.6 | 12 904 620 octets | 43 344 960 octets | `cp310-win_amd64` | `f0fd6321b839904e15c46e0d257fdd101dd7f530fe03fd6359c1ea63738703f3` |

Total : 61 194 406 octets compressés, 187 848 352 octets décompressés dans les
wheels. Dix DLL sont inventoriées et verrouillées individuellement dans
`tests/fixtures/p64_l08g_scip_product_gate.v1.json`.

L'installation Fusion observée est la version 2704.1.36. Son exécutable et son
`python314.dll` sont verrouillés dans la preuve ; l'ABI produit observée est
`cp314`, différente du `cp310` acquis pour le benchmark.

## Audit des dépendances et avis

| Composant | Fichiers observés | Source/licence officielle | État du paquet acquis |
| --- | --- | --- | --- |
| PySCIPOpt 6.2.1 | wheel et extension Python | [MIT, dépôt officiel](https://github.com/scipopt/PySCIPOpt) | complet pour l'interface seule |
| SCIP 10.0.2 | `libscip-*.dll` | [Apache-2.0, dépôt officiel](https://github.com/scipopt/scip) | avis absent du wheel |
| Ipopt | `ipopt-3-*.dll` | [EPL-2.0, documentation officielle](https://coin-or.github.io/Ipopt/LICENSE.html) | version exacte et avis absents |
| MUMPS | `coinmumps-3-*.dll` | [CeCILL-C et exceptions, site officiel](https://mumps-solver.org/index.php?page=dwnld) | version exacte et avis absents |
| runtimes Intel | quatre DLL Fortran/OpenMP/math | [règles de redistribution Intel](https://www.intel.com/content/www/us/en/docs/dpcpp-cpp-compiler/developer-guide-reference/2023-0/redistribute-libraries-when-deploying-apps.html) | versions/termes exacts non liés, avis absents |
| Visual C++ Runtime | deux copies de `msvcp140-*.dll` | [conditions Microsoft](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files?view=msvc-170) | avis et autorité de cette copie non établis |
| NumPy/OpenBLAS/LAPACK/GCC runtime | `libscipy_openblas*.dll` | avis embarqués par NumPy | complet dans `LICENSE.txt` |

L'audit ne dit pas que ces composants sont interdits en soi. Il dit que leur
redistribution exacte par BGIG n'est pas prouvée par le paquet acquis. Le
contrat L08G impose alors de refuser, pas de compléter les trous par intuition.

## Intégrité du benchmark

- sélection SCIP inchangée ;
- digest de sélection :
  `e061f9af67e9ce80974a8ea2c5fe705ba59a637dbba319464a412651b6fa7140` ;
- digest de preuve L08F récupérée :
  `0dbf1b45ae9135c1316051ab7e0946dfbfeafac5c785ad96ccd5d7a620acd46d` ;
- holdout rouvert : non ;
- worker privé rappelé : 0 ;
- tuning après holdout : 0 ;
- OR-Tools, LAFF et PackingSolver substitués après lecture privée : non.

La preuve L08G a pour digest :
`a8ddb80e48ba83f9e3869f0bd3fffc7447be997b2c5932daf781775a7cbcc09a`.

## Changements produit

Aucun. En particulier :

- aucun moteur, wheel ou DLL n'entre dans `fusion_addin/` ;
- aucun cap, budget, certificat, schéma, tolérance ou seed ne change ;
- aucune propriété P45/P64, géométrie, finalisation, CAD, scène ou valeur
  physique ne change ;
- aucune installation globale, aucun service, compte, secret, réseau ou
  télémétrie n'est ajouté.

## Preuves automatisées

- `scripts/solver/audit_scip_product_gate.py` : audit ZIP hors ligne, empreintes,
  avis, ABI et décision fail-closed ;
- `tests/fixtures/p64_l08g_scip_product_gate.v1.json` : preuve versionnée ;
- `tests/test_scip_product_gate_evidence.py` : quatre contrôles de la preuve,
  de la décision et de l'absence de réouverture.

## Suite possible sans falsifier le verdict

Une future mission séparée peut remédier au paquet sans refaire le benchmark :

1. acquérir le wheel officiel PySCIPOpt 6.2.1 `cp314` et son NumPy correspondant,
   ou choisir un exécutable SCIP autonome ;
2. lier chaque DLL à sa version, sa source et ses droits de redistribution ;
3. constituer un paquet complet de licences, avis et obligations de source ;
4. tester l'import ou le processus dans un environnement Fusion isolé ;
5. seulement alors créer l'ADR d'intégration, rejouer les régressions ouvertes
   et préparer une gate Fusion humaine.

Cette remédiation ne pourra ni rouvrir le holdout L08F, ni retuner le moteur, ni
changer le vainqueur après lecture du privé.
