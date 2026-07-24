# P64-L08J — Preuve de build du runtime SCIP minimal

## Verdict

P64-L08J est `done`, `implemented-build` et `automated-validated`.
Le runtime minimal SCIP 10.0.2 pour Python 3.14 est construit hors ligne depuis les
entrées verrouillées par L08I, puis qualifié deux fois depuis deux racines de build
propres. Il conserve le vrai modèle MIP 3D du tournoi et autorise la mission
séparée P64-L08K d’intégration produit et de régressions complètes.

Aucun runtime produit ni paquet Fusion n’est modifié dans cette mission. Le
holdout L08F n’a été ni lu ni rejoué. `fusion-validated=false` et
`print-validated=false` restent inchangés.

Décision : `minimal_scip_runtime_build_and_public_equivalence_pass`.

## Candidat construit

- SCIP 10.0.2, SoPlex 8.0.2 et PySCIPOpt 6.2.1 `cp314` ;
- NumPy 2.5.1 `cp314` ;
- Visual Studio 17 2022 x64, toolset v143 14.44, SDK 10.0.26100.0 ;
- bibliothèques dynamiques `/MD`, LTO actif, SoPlex obligatoire ;
- symétrie `snauty` et plugins MIP internes conservés ;
- Ipopt, MUMPS, METIS, runtimes Intel, PaPILO/TBB, GCG, ZIMPL, GMP et
  solve rationnel exact absents.

Le script `scripts/solver/build_minimal_scip_runtime.ps1` reconstruit toute la
chaîne sous une nouvelle racine `.codex-work`, avec un seul processus lourd,
sans installation globale et sans accès réseau.

## Inventaire natif et redistribution

| Contrôle | Résultat |
| --- | ---: |
| Fichiers du runtime qualifié | 1 016 |
| Taille du runtime qualifié | 56 491 565 octets |
| Taille du candidat PyPI refusé en L08H | 186 127 316 octets |
| Réduction non compressée | 69,65 % |
| Binaires inventoriés | 26 |
| DLL | 6 |
| PYD | 20 |
| Dépendances non résolues | 0 |
| Binaires interdits | 0 |
| Fichiers Microsoft vérifiés contre `VC/Redist` | 4 |
| Fichiers d’avis | 26 |

Les avis PySCIPOpt, SCIP, `nauty`, `dejavu`, `tclique`, SoPlex, `fmt`,
`zstr`, NumPy et Microsoft sont présents. Chaque DLL/PYD, dépendance, taille et
SHA-256 figure dans les reçus JSON versionnés.

## Contrôles publics 3D

Le probe isolé confirme Python `cp314`, NumPy 2.5.1, PySCIPOpt 6.2.1, SCIP
10.0.2 et un optimum exact de 7. Les six contrôles publics conservent le même
statut, le même objectif et le même niveau de preuve que le runtime du tournoi.

| Famille | Verdict candidat | Objectif |
| --- | --- | ---: |
| empilement faisable | solution | 440 |
| empilement impossible | preuve impossible | — |
| appuis multiples | solution | 1 088 |
| réservation 3D | solution | 1 196 |
| fragmentation | solution | 1 968 |
| variante et rotation | solution | 314 |

Temps total de référence : 12,5138 ms. Temps du candidat qualifié : 16,8199 ms.
Seuil de régression matérielle préenregistré : 32,5138 ms. Verdict : aucune
régression matérielle.

La régression publique à 18 conteneurs et 20 contenus reste honnêtement
`unsupported` à la couche de représentation `incomplete_real_3d_problem` ;
aucun worker SCIP n’est lancé pour inventer une réponse.

## Reconstruction indépendante

Une seconde construction complète depuis une racine vide a fini avec succès en
505 secondes puis a repassé la même qualification : 1 016 fichiers, 26 binaires,
zéro dépendance manquante ou interdite, même probe exact, six contrôles 3D sans
perte et aucune régression matérielle.

Le wheel et `libscip.dll` ne sont pas identiques bit à bit entre les deux builds
à cause des métadonnées ZIP et de la sortie du compilateur MSVC. Cette variation
est explicitement conservée dans le second reçu ; elle ne change ni les entrées,
ni les options CMake, ni les dépendances, ni le comportement qualifié. Le paquet
produit devra donc versionner un build qualifié précis plutôt que promettre un
hash binaire indépendant de la racine de compilation.

## Preuves versionnées

- `tests/fixtures/p64_l08j_minimal_scip_runtime_build.v1.json` ;
- `tests/fixtures/p64_l08j_minimal_scip_runtime_rebuild.v1.json` ;
- `tests/test_minimal_scip_runtime_build_evidence.py` ;
- `scripts/solver/build_minimal_scip_runtime.ps1` ;
- `scripts/solver/qualify_minimal_scip_runtime.py`.

Empreinte du premier reçu :
`6fc5a141a809cf2db18f54c162e7f26dc1baf7947bf53ca50ffe6ecd36c94823`.

Empreinte du reçu de reconstruction :
`d96974446f50f3143bbbc54da1e156f95c9b8b77e5d7f35f09f73d19858139ba`.

## Frontières et suite

- aucun tuning, aucun replay du holdout, aucun changement de budget ou de modèle ;
- aucune revendication nouvelle sur le cas dense 11 × 34 ;
- aucune modification de certificat, schéma, tolérance, géométrie, finalisation,
  CAD, scène ou valeur physique ;
- aucune validation Fusion ou impression déduite de ce build.

P64-L08K peut maintenant intégrer un build qualifié précis dans le paquet local
Fusion, brancher SCIP derrière le contrat BGIG existant, exécuter les
régressions complètes et préparer une gate humaine seulement si tout reste vert.
