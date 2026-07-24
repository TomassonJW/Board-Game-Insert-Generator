# P64-L08H — preuve de remédiation du paquet SCIP

Date : 2026-07-24
Statut : `negative-package-redistribution-incomplete`, `abi-pass`, `offline-probe-pass`, `no-product-integration`, `no-fusion-gate`.

## Verdict

Le wheel officiel PySCIPOpt 6.2.1 pour CPython 3.14 corrige réellement le
blocage ABI de L08G. Il charge localement NumPy 2.5.1 et SCIP 10.0.2 dans un
Python 3.14 isolé, puis résout un contrôle exact à l'optimal sans installation
globale ni accès réseau.

La gate produit reste néanmoins fermée. Le wheel PySCIPOpt contient l'avis MIT
de l'interface, mais pas les avis et termes applicables à toutes les
bibliothèques natives qu'il redistribue. Les obligations MUMPS/METIS et la
chaîne d'autorité des runtimes Intel et Microsoft ne sont pas entièrement
établies par les artefacts officiels. Aucun runtime n'est donc intégré dans
BGIG et aucune gate Fusion n'est préparée.

## Choix du paquet

Le candidat retenu pour l'audit est le couple de wheels PyPI officiel :

- `pyscipopt-6.2.1-cp314-cp314-win_amd64.whl` ;
- `numpy-2.5.1-cp314-cp314-win_amd64.whl`.

Ce choix conserve la même interface PySCIPOpt et le même SCIP 10.0.2 que le
worker scellé de L08F. Il évite d'introduire un nouveau protocole CLI non
benchmarké. Les artefacts sont publics, directement téléchargeables et
possèdent des empreintes officielles sur [PyPI PySCIPOpt](https://pypi.org/project/PySCIPOpt/6.2.1/)
et [PyPI NumPy](https://pypi.org/project/numpy/2.5.1/).

L'exécutable SCIP autonome n'est pas téléchargé ni retenu : son parcours
officiel demande des champs d'identité, ajoute la suite complète et ses
prérequis, et imposerait un nouvel adaptateur à recertifier. Le
[site officiel SCIP](https://scipopt.org/) confirme la disponibilité de SCIP
10.0.2 et des paquets Windows, sans fournir une équivalence avec le worker
PySCIPOpt du tournoi.

## Artefacts verrouillés

| Artefact | Taille | SHA-256 |
|---|---:|---|
| PySCIPOpt 6.2.1 `cp314` | 49 375 214 octets | `6aed03b621decb09b38f399773bf8cf2c707e965990b778a24d28c8cc90a0756` |
| NumPy 2.5.1 `cp314` | 12 562 177 octets | `24d0eb82c0541d3415a33425db64ae439dffccd7b4dbcb30e7c35120205c506a` |
| Python 3.14.0 embarqué, banc d'essai uniquement | 11 994 671 octets | `8d4d3590c10449d78aa4375f534e6d5f3027d67fdc362dd1a882279db6f90fdf` |
| `scipoptsuite-deploy` v0.12.0 Windows | 67 130 466 octets | `a6461de7d8e20b3115e7bfe6439597acaeb803c259e22b22b74404ac4a6b4cad` |
| Ipopt 3.14.19 Windows | 42 026 331 octets | `bd7818a19c2a627f1dcd538358833fbcb17c35080e19b4228be3f66cadf8c8fd` |

Le paquet produit étudié mesure 61 937 391 octets compressés et 186 127 316
octets décompressés. Les 30 binaires `.pyd` et `.dll` des deux wheels sont
inventoriés individuellement avec leur taille et leur SHA-256 dans
`tests/fixtures/p64_l08h_scip_package_remediation.v1.json`.

Le Python embarqué n'est pas un composant produit : il sert uniquement à
reproduire l'ABI `cp314`. Son empreinte est vérifiée contre la preuve Sigstore
de la [publication Python 3.14.0](https://www.python.org/downloads/release/python-3140/).

## Preuve d'exécution locale hors ligne

Le probe est lancé avec :

- Python 3.14.0, option isolée `-I` ;
- chemin ajouté explicitement vers les wheels décompressés dans `.codex-work` ;
- `PIP_NO_INDEX=1` ;
- proxys HTTP et HTTPS dirigés vers `127.0.0.1:9` ;
- aucune installation globale ;
- aucun corpus et aucun holdout lu.

Résultat :

| Contrôle | Valeur |
|---|---|
| Python | `3.14.0`, `cpython-314`, mode isolé |
| NumPy | `2.5.1` |
| PySCIPOpt | `6.2.1` |
| SCIP | `10.0.2` |
| Problème | variable binaire, maximiser `x` |
| Statut | `optimal` |
| Solution | `x = 1.0` |

La gate ABI et la gate d'exécution locale passent donc toutes les deux.

## Chaîne native vérifiée

La configuration officielle
[PySCIPOpt v6.2.1](https://github.com/scipopt/PySCIPOpt/tree/v6.2.1)
télécharge `scipoptsuite-deploy` v0.12.0 pour fabriquer les wheels Windows.
Cette publication verrouille :

- SCIP 10.0.2 ;
- SoPlex 8.0.2 ;
- Ipopt 3.14.19 ;
- GCG 4.0.2.

Le paquet Ipopt 3.14.19 indique lui-même MUMPS 5.8.0, METIS 5.2.1, Intel MKL
2024.1 et les compilateurs Intel 2021.8.0. Les DLL réellement présentes dans
le wheel sont liées à cette chaîne et verrouillées par empreinte.

## Audit des licences et avis

| Composant | Version verrouillée | Licence identifiée | Avis dans le candidat | Autorité de redistribution |
|---|---|---|---:|---:|
| PySCIPOpt | 6.2.1 | MIT | oui | établie |
| SCIP | 10.0.2 | Apache-2.0 | non | obligations identifiées, avis absent |
| Ipopt | 3.14.19 | EPL-2.0 | non | obligations identifiées, avis absent |
| MUMPS / METIS | 5.8.0 / 5.2.1 | CeCILL-C avec exceptions / Apache-2.0 | non | incomplète |
| runtimes Intel | MKL 2024.1 et chaîne 2021.8.0 | termes Intel applicables | non | incomplète |
| runtime Microsoft | `msvcp140` 14.40.33810.0 | termes Visual Studio | non | incomplète |
| NumPy et bibliothèques liées | 2.5.1 | avis BSD et tiers inclus | oui | établie |

Les sources officielles confirment la licence
[Apache-2.0 de SCIP](https://github.com/scipopt/scip), la
[CeCILL-C de MUMPS et ses exceptions](https://mumps-solver.org/index.php?page=dwnld),
et la redistribution conditionnelle du
[runtime Visual C++](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).
La publication du wheel ne suffit pas à démontrer que BGIG peut redistribuer
ces DLL sans compléter les avis et sans établir les droits Intel/Microsoft.

## Décision fail-closed

- `technical_abi_gate_passed=true` ;
- `isolated_offline_execution_passed=true` ;
- `all_native_versions_bound=true` ;
- `all_notices_present=false` ;
- `all_redistribution_terms_bound=false` ;
- `product_integration_authorized=false` ;
- `fusion_gate_prepared=false` ;
- `fusion_gate_installed=false`.

Raisons bloquantes :

1. `third_party_notices_incomplete` ;
2. `redistribution_authority_incomplete`.

## Frontières respectées

- holdout L08F non lu et non rejoué ;
- zéro tuning et zéro changement du gagnant ;
- aucun budget, certificat, schéma, tolérance ou modèle modifié ;
- aucun runtime produit ou add-in Fusion modifié ;
- `fusion-validated=false` et `print-validated=false` inchangés.

## Suite recommandée

P64-L08I doit ouvrir une ADR et auditer une fabrication minimale de SCIP 10.0.2
pour `cp314`, sans Ipopt, MUMPS/METIS ni runtimes Intel puisqu'ils ne servent
pas au modèle discret BGIG retenu. Cette mission doit verrouiller la toolchain,
les licences et les avis avant build, puis exécuter les régressions publiques
sans toucher au holdout. L'intégration produit et la gate Fusion resteront une
mission séparée après réussite.

## Validations

- probe Python 3.14 isolé : `optimal`, SCIP 10.0.2, `x=1.0` ;
- preuve L08H : 5/5 tests ;
- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- `ruff format --check` et `ruff check` : OK ;
- `py_compile` : OK ;
- suite complète : 802/802 en 287,464 s sous garde Windows ;
- `git diff --check` : OK.

Digest canonique de la preuve :
`d2de2bea96200c614270ae60e5fdbe2736a398701eb424ec57c61706ba8c9440`.
