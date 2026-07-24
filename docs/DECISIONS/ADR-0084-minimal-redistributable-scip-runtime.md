# ADR-0084 — Runtime SCIP MIP minimal et redistribuable

## Statut

Acceptée le 2026-07-24 dans le Goal autonome P64-L08 post-benchmark autorisé par Thomas.

## Contexte

P64-L08F a établi SCIP 10.0.2 via PySCIPOpt 6.2.1 comme meilleur moteur 3D
mesuré. P64-L08H a ensuite confirmé que le wheel officiel `cp314` fonctionne
techniquement dans Python 3.14, mais ce wheel embarque aussi Ipopt, MUMPS/METIS
et plusieurs runtimes Intel sans tous les avis nécessaires au paquet BGIG.

Le worker scellé `scip_real_3d_worker.py` ne construit pourtant que des variables
binaires ou entières et des expressions linéaires. Il couvre les placements XYZ,
les collisions sur trois axes, les étages, appuis, réservations, régions,
variantes et précédences de retrait. Il n'appelle aucune primitive non linéaire.

La documentation SCIP 10.0.2 distingue explicitement le solveur LP SoPlex des
solveurs NLP tels qu'Ipopt, fournit un profil MIP avec Ipopt désactivé et permet
de désactiver chaque dépendance. La documentation PySCIPOpt confirme que la
branche 6.2 est compatible avec SCIP 10.0.2 et qu'une compilation contre un SCIP
local passe par `SCIPOPTDIR`.

## Décision

BGIG fabriquera un candidat Windows x64 reproductible composé de :

- SCIP 10.0.2, tag et commit officiels verrouillés ;
- SoPlex 8.0.2 comme solveur des relaxations linéaires ;
- PySCIPOpt 6.2.1 recompilé pour CPython `cp314` ;
- NumPy 2.5.1 `cp314` ;
- les plugins MIP internes de SCIP, la symétrie `snauty` et l'optimisation LTO.

La cible exclut explicitement Ipopt, MUMPS, METIS, MKL, les runtimes Intel
Fortran/OpenMP, GCG, ZIMPL, GMP et le mode de résolution rationnelle exacte.
PaPILO est également désactivé dans ce premier candidat parce que sa chaîne
Windows ajoute Boost et TBB ; les présolveurs MIP internes de SCIP restent
présents. Cette exclusion ne devient une décision produit que si la mission de
build suivante prouve l'équivalence et l'absence de régression pertinente sur
les cas publics ouverts. Sinon le candidat est refusé, sans utiliser le holdout.

Le build utilise Visual Studio 2022 x64, MSVC 19.44.35207.1, Windows SDK
10.0.26100.0 et CMake 4.0.2. Tout est extrait ou construit sous `.codex-work` :
aucune installation globale, aucun service, compte, secret ou accès réseau au
runtime produit.

Les bibliothèques C/C++ utilisent `/MD` afin de rester cohérentes avec une
extension CPython. Les DLL réellement requises seront déterminées après build
avec l'outil de dépendances Windows. Seules les DLL prises dans le répertoire
`VC/Redist` de Visual Studio pourront être vendues localement ; toute autre
provenance ferme la gate. Ce choix suit la documentation Microsoft, qui autorise
le déploiement local des fichiers redistribuables et déconseille le CRT statique
dans une DLL sans analyse complète de ses effets.

## Gate de build suivante

P64-L08J doit échouer immédiatement si l'une des conditions suivantes n'est pas
prouvée :

1. versions, tailles et SHA-256 des entrées conformes à la preuve L08I ;
2. configuration effective conforme aux options CMake verrouillées ;
3. aucun binaire Ipopt, MUMPS/METIS ou Intel dans la sortie ;
4. dépendances natives toutes résolues et issues des sources autorisées ;
5. avis PySCIPOpt, SCIP, SoPlex et sources embarquées présents ;
6. import PySCIPOpt `cp314`, SCIP 10.0.2 et contrôle exact local réussis hors ligne ;
7. contrôles publics 3D et régressions ouvertes équivalents au runtime du tournoi ;
8. aucune lecture, relance ou adaptation fondée sur le holdout L08F.

Même en cas de réussite, L08J n'autorise pas à elle seule l'intégration produit :
une mission atomique séparée devra encore intégrer le runtime et mesurer les
régressions BGIG complètes.

## Alternatives refusées

- **Redistribuer le wheel PyPI actuel** : techniquement fonctionnel, mais ses
  avis tiers et son autorité de redistribution restent incomplets.
- **Conserver Ipopt et compléter seulement les fichiers de licence** : BGIG ne
  formule aucun NLP ; cette voie garde inutilement MUMPS et les runtimes Intel.
- **Supprimer SoPlex** : un MIP SCIP sérieux a besoin d'un solveur LP pour ses
  relaxations ; le profil retenu doit rester `LPS=spx`.
- **Lier tout le CRT statiquement** : cela éloigne l'extension de la chaîne
  CPython et Microsoft déconseille ce choix pour les DLL sans maîtrise complète
  des états CRT.
- **Rejouer le holdout pour qualifier le paquet** : le holdout est consommé et
  ne peut plus guider un choix ou un réglage.

## Conséquences

- Le gagnant, le modèle, les budgets et les paramètres du tournoi ne changent pas.
- L08I autorise seulement un build contrôlé ; aucun runtime produit ni add-in
  Fusion n'est modifié.
- La taille finale, la liste exacte des DLL et la performance publique restent
  à mesurer dans L08J.
- `fusion-validated=false` et `print-validated=false` restent inchangés.

## Sources officielles

- [SCIP 10.0.2 et sa licence Apache-2.0](https://github.com/scipopt/scip/releases/tag/v10.0.2)
- [Options de compilation SCIP](https://www.scipopt.org/doc/html/md_INSTALL.php)
- [SoPlex 8.0.2](https://github.com/scipopt/soplex/tree/v8.0.2)
- [PySCIPOpt 6.2.1](https://github.com/scipopt/PySCIPOpt/tree/v6.2.1)
- [Compilation PySCIPOpt contre un SCIP local](https://pyscipopt.readthedocs.io/en/stable/build.html)
- [Paquet Python 3.14.0 pour les builds locaux](https://www.nuget.org/packages/python/3.14.0)
- [Déploiement du runtime Microsoft C++](https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp?view=msvc-170)
