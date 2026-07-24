# P64-L08I — preuve d'audit du runtime SCIP minimal

Date : 2026-07-24
Statut : `prebuild-audit-pass`, `build-only-authorized`, `no-product-integration`, `no-fusion-gate`.

## Verdict

Le runtime SCIP minimal peut être construit sans modifier le gagnant ni le
modèle 3D. Le worker scellé est un MIP entier et linéaire : 18 sites de création
de variables, tous en `B` ou `I`, aucun produit entre deux expressions de
décision et aucune primitive Ipopt/MUMPS/METIS.

La cible conserve SCIP 10.0.2, SoPlex 8.0.2, PySCIPOpt 6.2.1, les plugins MIP
internes, la symétrie `snauty` et LTO. Elle retire la chaîne NLP inutilisée :
Ipopt, MUMPS/METIS, MKL et runtimes Intel. Aucun benchmark, tuning ou holdout
n'a été lancé pendant cette mission.

L08I autorise uniquement P64-L08J, le build et la gate d'équivalence publique.
Aucun fichier produit, runtime BGIG ou add-in Fusion n'est encore modifié.

## Modèle 3D réellement protégé

Le contrôle statique porte sur
`scripts/solver/external_workers/scip_real_3d_worker.py`, SHA-256
`2a1870dc65955e59d15720d4133e55a45da1205b7a72b1f9457632b193d13363`.

Il confirme la présence des familles sémantiques obligatoires :

- séparation orthogonale sur X, Y et Z ;
- placement multi-niveaux et hauteur réelle ;
- nombre et surface d'appuis ;
- volumes réservés ;
- régions disjointes ;
- ordre de retrait ;
- sélection des variantes et orientations locales.

Il ne s'agit donc pas d'un retour à un rangement au sol ni d'un cas 11 × 34.

## Sources verrouillées avant build

| Composant | Version | Commit | Taille | SHA-256 |
|---|---|---|---:|---|
| SCIP | 10.0.2 | `b8eaf989f9168f966a471b2039ffb75d925d5202` | 13 725 644 | `7225e8d493707ebb1b5c5d5696cf384a1cd6aeaf8820253ae260a5fdcc763308` |
| SoPlex | 8.0.2 | `cfadddc47e142fb21e040ff9dc564cbe2e8e3801` | 1 466 934 | `f1a45c6338ad1cfb6c2950e91e4f854ed199c2e4039830b26dbe65d0dd67cd34` |
| PySCIPOpt | 6.2.1 | `6ff33812155e6592e0a681b6a1967322428ac2db` | 959 233 | `0d53902150724665c2f2a22adb89fd1b3717c16b365819dfbdf137f65ab76588` |

Les archives proviennent des tags officiels
[SCIP](https://github.com/scipopt/scip/releases/tag/v10.0.2),
[SoPlex](https://github.com/scipopt/soplex/tree/v8.0.2) et
[PySCIPOpt](https://github.com/scipopt/PySCIPOpt/tree/v6.2.1).

## Outils Python de build verrouillés

| Entrée | Version | Taille | SHA-256 | Produit |
|---|---:|---:|---|---:|
| Python NuGet x64 | 3.14.0 | 14 839 285 | `620fb3527428fb354f093b0b8b634dfb8e3023115df68608fba7e91db69b4f4d` | non |
| Cython `cp314` | 3.2.8 | 2 807 626 | `89b0fdc2ca0b502afedc4dd4ddbc4f9cb5a135245afacf9483e556e8ad3ada3b` | non |
| setuptools | 83.0.0 | 1 008 090 | `29b23c360f22f414dc7336bb39178cc7bcbf6021ed2733cde173f09dba19abb3` | non |
| wheel | 0.47.0 | 32 218 | `212281cab4dff978f6cedd499cd893e1f620791ca6ff7107cf270781e587eced` | non |
| NumPy `cp314` | 2.5.1 | 12 562 177 | `24d0eb82c0541d3415a33425db64ae439dffccd7b4dbcb30e7c35120205c506a` | oui |

Le [paquet NuGet Python](https://docs.python.org/3/using/windows.html#the-nuget-org-packages)
est prévu par Python pour les builds isolés et contient les en-têtes et
bibliothèques de développement sans installation système.

## Toolchain Windows verrouillée

| Élément | Version | Empreinte ou référence |
|---|---|---|
| Visual Studio 2022 Community | 17.14.2 | installation locale complète |
| MSVC x64 | 19.44.35207.1 | `6aa39ae173cb8563d796359930b332a08b2fdc1745b70e5a4caa48a9779fdd07` |
| Windows SDK | 10.0.26100.0 | sélection explicite au build |
| CMake | 4.0.2 | `c5cecf8e663f105217ff5805bb1d748f7de2fe3767312974b677b3c818883d2c` |
| Ninja, disponible mais non requis | 1.11.1 | `9ee2fc6bc8c0acd1de6e6dcadf009c0598e6336646b87cfb5ed2918604b81597` |

Le build sera limité à deux processus lourds et restera sous `.codex-work`.

## Configuration native décidée

### SoPlex

`Release`, `BOOST=OFF`, `GMP=OFF`, `MPFR=OFF`, `PAPILO=OFF`, `QUADMATH=OFF`,
`ZLIB=OFF`.

### SCIP

`Release`, `SHARED=ON`, `LPS=spx`, `LPSEXACT=none`, `SYM=snauty`, `LTO=ON`,
`IPOPT=OFF`, `PAPILO=OFF`, `GMP=OFF`, `MPFR=OFF`, `EXACTSOLVE=OFF`,
`EXPRINT=none`, `TPI=none`, `ZIMPL=OFF`, `AMPL=OFF`, `READLINE=OFF`,
`ZLIB=OFF`, `LAPACK=OFF`, `WORHP=OFF`, `CONOPT=OFF`.

[SCIP 10.0.2 documente officiellement](https://www.scipopt.org/doc/html/md_INSTALL.php)
que SoPlex est la cible LP, qu'Ipopt est optionnel et que le profil MIP désactive
Ipopt. [PySCIPOpt documente](https://pyscipopt.readthedocs.io/en/stable/build.html)
la compatibilité 6.2 / SCIP 10.0.2 et la compilation contre un `SCIPOPTDIR` local.

## Licences et redistribution

Les avis obligatoires avant tout paquet produit sont verrouillés :

- PySCIPOpt MIT ;
- SCIP, tclique et nauty Apache-2.0 ;
- dejavu MIT ;
- SoPlex Apache-2.0 et fmt MIT ;
- licence et avis tiers NumPy ;
- termes de redistribution Microsoft Visual C++.

Le build emploiera `/MD`. La liste exacte des DLL Microsoft sera dérivée du
binaire construit ; seules celles issues du dossier officiel
`VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT` seront admises.
La [documentation Microsoft](https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp?view=msvc-170)
prévoit le déploiement local et le lie aux fichiers redistribuables fournis avec
Visual Studio. Tout binaire natif non résolu ou issu d'une autre source ferme la
gate.

Familles explicitement interdites dans la sortie : `ipopt*`, `coinmumps*`,
`libifcoremd*`, `libiomp5md*`, `libmmd*` et `svml_dispmd*`.

## Frontières et décision

- `minimal_build_authorized=true` ;
- `product_integration_authorized=false` ;
- `holdout_read=false` ;
- `benchmark_replayed=false` ;
- `post_holdout_tuning_count=0` ;
- `fusion_gate_prepared=false` ;
- `fusion_gate_installed=false` ;
- `fusion-validated=false` ;
- `print-validated=false`.

La prochaine mission est P64-L08J : build reproductible, inventaire réel des DLL,
probe hors ligne et équivalence sur contrôles publics et régressions ouvertes.

Digest canonique de la preuve :
`51b89df9666bbb8b0272bf5e4c582dc2737e7733472e581bec685ae4102d38e5`.
## Validations de mission

- preuve L08I : 6/6 ;
- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- `ruff format --check` et `ruff check` : OK ;
- `py_compile` : OK ;
- suite complète : 808/808 en 289,784 s sous garde Windows ;
- `git diff --check` : OK.
