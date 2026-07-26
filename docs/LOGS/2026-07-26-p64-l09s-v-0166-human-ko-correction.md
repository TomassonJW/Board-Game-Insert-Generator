# 2026-07-26 - correction du KO humain P64-L09S-V 0.1.66

## Declencheur

Thomas a rejete la finalisation `0.1.66` sur des cas complexes et signale un possible rabotage des volumes minimaux.

## Diagnostic confirme

- le mode approfondi transmettait son budget, mais le moteur quittait prematurement ;
- une variante reduisait le minimum `76 x 76 x 31.8 mm` a `53.6 x 76 x 31.8 mm` ;
- les certifications ne protegeaient pas le minimum source ;
- la fermeture continue moderne ne couvrait pas ce repli.

## Correctif 0.1.67

- minimum canonique source impose par axe dans les variantes et l'adaptateur global ;
- voie dense au sol par etageres guillotine certifiees, sans remplacer SCIP ;
- fermeture continue prioritairement verticale, bornee aux plans reserves ;
- ordre de repli : fermeture globale, croissance verticale, annexes XY bornees ;
- publication interdite sans plan recertifie et residuel nul.

## Preuve locale

Le rejeu exact du projet prive recent obtient :

- calcul : `solution_found` en environ `0.176 s` ;
- violations de minima : `0` ;
- finalisation : `solution_found` en environ `0.091 s` ;
- materialisable : `true` ;
- residuel imprimable : `0.0 mm3` ;
- source finale : `c_global_rectangular_partition`.

La suite automatisee autorisee passe `833/833`, avec `68` tests benchmark/holdout/corpus exclus et `1` test SCIP natif ignore sous Python 3.10. `fusion-validated=false`, `print-validated=false`.

<!-- P64-L09S-0167-PREPARED -->
## Preparation Fusion 0.1.67 confirmee

- statut : `prepared-not-human-observed` ;
- commit installe : `832c9d5` ;
- preflight : `85c578d051b83fcd71b6b3c6eeaed7601748b1b95e5e942377faf9f52ef3e528` ;
- package/manifeste/reglages/marqueur : verifies ;
- cas humain obligatoire : projet recent a 28 conteneurs, avec controle du minimum `76 x 76 x 31.8 mm` ;
- `fusion-validated=false` et `print-validated=false` jusqu'au verdict humain.
