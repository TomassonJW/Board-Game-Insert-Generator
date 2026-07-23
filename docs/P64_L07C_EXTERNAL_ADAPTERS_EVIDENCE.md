# P64-L07C — preuve des adapters externes

## 1. Résultat

La gate locale réelle passe : `12/12`.

| Candidat | Faisable simple | Rotation requise | Impossible |
|---|---|---|---|
| OR-Tools CP-SAT 9.15.6755 | certifié | certifié | `infeasible_proven` |
| HiGHS 1.15.1 | certifié | certifié | `infeasible_proven` |
| SCIP 10.0.2 / PySCIPOpt 6.2.1 | certifié | certifié | `infeasible_proven` |
| LAFF 4.2.1 | certifié | certifié | `bounded_unknown` |

Les huit sorties positives portent toutes un nouveau certificat
`bgig.minimal_layout_certificate.v1`. Aucun rejet de certificat, aucune erreur
worker et aucune réutilisation de checkpoint n'apparaissent dans ce premier
passage.

## 2. Exécution

Enveloppe identique par cas :

- 10 secondes murales totales ;
- 1 thread demandé ;
- 1 024 Mio maximum ;
- graine 640707 ;
- un seul processus lourd à la fois.

Commande reproductible :

```powershell
$env:PYTHONPATH = "src"
python scripts/solver/run_external_solver_adapter_controls.py `
  --artifact-lock tests/fixtures/p64_l07c_external_solver_artifacts.v1.json `
  --artifact-root .codex-work/p64-l07/artifacts `
  --environment-root .codex-work/p64-l07/envs `
  --java-home .codex-work/p64-l07/envs/laff-jdk/jdk-17.0.19+10 `
  --scratch-root .codex-work/p64-l07/control-campaign `
  --output .codex-work/p64-l07/l07c-controls-run.json `
  --wall-seconds 10
```

La commande a été lancée par le wrapper Windows gardé, avec heartbeat et timeout
métier de 600 secondes. Résultat : `completed`, code 0, environ 4 secondes.

## 3. Artefacts vérifiés

| Candidat | Taille du bundle verrouillé | Gate produit |
|---|---:|---|
| OR-Tools | 49 821 428 octets | candidat |
| HiGHS | 15 612 832 octets | candidat |
| SCIP/PySCIPOpt | 61 194 406 octets | benchmark seulement |
| LAFF + JDK portable | 204 015 872 octets | benchmark seulement |

Ces tailles mesurent les téléchargements verrouillés, pas encore un package
produit optimisé.

Temps observés sur ces très petits contrôles, seulement indicatifs :

| Candidat | Temps total min–max | Pic mémoire maximal observé |
|---|---:|---:|
| OR-Tools | 0,324–0,413 s | 74 219 520 octets |
| HiGHS | 0,121–0,136 s | 31 739 904 octets |
| SCIP/PySCIPOpt | 0,122–0,135 s | 40 448 000 octets |
| LAFF | 0,229–0,250 s | 90 107 904 octets |

Ces valeurs ne classent pas les moteurs. L07D seul possède un corpus et une
enveloppe suffisants pour décider.

## 4. Digests

- verrou d'artefacts :
  `58736ecde2a6bfbc4d57c3e5bc4e947c9875fe9f7a3c654cb87594e91c552bc6` ;
- contrôles :
  `501f17b099ee7031f9f0f363b720a94601b8a353a45f1213063514b892c4712a` ;
- campagne complète locale :
  `83c40101b29e26dd88a8bfba0e2d55cd9c8c34fbcc90e36f490a9585b692d6d2` ;
- preuve compacte versionnée :
  `926afb91e3bf4e18a1d70af01e32f2cfd0d0bdf4c92d7a0b77120de201848dbb`.

## 5. Vérifications automatisées

- validation fail-closed du verrou et de ses digests ;
- vérification locale taille + SHA-256 avant worker ;
- trois contrôles BGIG déterministes ;
- worker factice pour le certificat et la reprise de checkpoint ;
- séparation exacte / heuristique des statuts négatifs ;
- validation canonique de la preuve réelle.

Résultats :

- tests ciblés de tous les modules `external_solver*` : 28/28 en 28,057 s ;
- tests propres aux adapters et preuves L07C : 11/11 ;
- suite complète : 744/744 en 223,411 s ;
- wrapper Windows : `completed`, code 0, 224 s.

Un premier lancement de suite complète a été interrompu par la fenêtre terminal
de 30 secondes ; l'absence de processus restant a été vérifiée avant l'unique
relance gardée ci-dessus.

## 6. Limites et suite

Le modèle L07C couvre un seul niveau rectangulaire. Les cas avec plusieurs
niveaux ou réservations sont refusés, pas simplifiés. Le prochain lot L07D doit
donc mesurer d'abord la couverture représentable, puis seulement la qualité et
les temps.

Le holdout L07 n'a été ni lu ni matérialisé. `fusion-validated: false` et
`print-validated: false`.
