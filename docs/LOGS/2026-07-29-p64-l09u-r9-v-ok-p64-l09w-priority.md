# 2026-07-29 — R9-V positive et priorité P64-L09W

Thomas valide la candidate Fusion 0.1.80 avec le verdict
`P64-L09U-R9-V Fusion OK 0.1.80`.

R9 est donc clos en `human-positive`, `fusion-validated=true` et
`print-validated=false`. Aucun temps humain séparé n’a été fourni ; les mesures
automatisées restent les seules valeurs chiffrées versionnées.

Thomas signale ensuite une limite plus générale : des projets réalisables mais
différents des deux cas R9 peuvent rester sans solution après une modification
de paramètres. Il demande une large passe de tests et d’optimisation couvrant
des cardinalités, dimensions, densités, conteneurs et éléments plats très
variés.

Décision de pilotage : P64-L09W devient prioritaire avant P64-L10 et la roadmap
d’origine. Le programme réutilise les corpus et runners L05D à L08, crée un
nouveau domaine mesurable et un holdout neuf, puis n’optimise que les causes
démontrées. Une cible de `95 %` ou `99 %` ne pourra être revendiquée que sur un
domaine et des limites préenregistrés.

Handoff :
`docs/P64_L09W_GENERAL_SOLVER_ROBUSTNESS_HANDOFF.md`.
