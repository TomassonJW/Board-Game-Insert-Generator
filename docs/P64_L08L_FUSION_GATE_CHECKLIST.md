# P64-L08L — Gate Fusion de la correction SCIP 3D

## Préparation automatique requise

Avant toute action de Thomas, Codex doit :

1. intégrer et pousser le commit P64-L08L dans `main` ;
2. vérifier le SHA distant ;
3. exécuter `scripts/fusion/prepare_p64_l08l_solver_correction_gate.ps1` depuis ce commit ;
4. vérifier l’add-in 0.1.62, l’artefact SCIP, le runtime extrait et le marqueur de commit ;
5. préserver l’état documentaire local existant ;
6. installer le projet public `p64-l08l-public-28x30.bgig.json` et sélectionner `Auto intelligent + Approfondi`.

## Actions humaines restantes

1. Dans Fusion, recharge l’add-in BGIG 0.1.62 puis ouvre la palette.
2. Vérifie que le projet public 28x30 est affiché avec `Auto intelligent + Approfondi`.
3. Clique une seule fois sur `Calculer l’agencement minimal` et attends au plus 130 secondes.
4. Ouvre `Diagnostic du calcul`, puis relève :
   - le résultat ;
   - l’état `SCIP 3D externe` ;
   - le moteur ;
   - `Recertifié BGIG` ;
   - le nombre d’appels SCIP ;
   - le nombre de voies internes.
5. Charge ensuite ton vrai projet limite 28x30 et répète une seule fois le même calcul.
6. Ne matérialise que si BGIG affiche une solution certifiée.

## Critères d’acceptation

La gate est positive seulement si les deux calculs :

- terminent sans blocage durable de Fusion ;
- affichent `solution_found` ;
- affichent SCIP 3D externe avec moteur `hybrid_anchor_and_fill` ou un plan SCIP direct ;
- affichent `Recertifié BGIG : Oui` ;
- n’utilisent qu’un appel SCIP et aucune voie interne après succès ;
- produisent un agencement 3D cohérent visuellement.

Un arrêt au plafond, un certificat refusé, une interface figée ou un résultat incohérent est un KO documenté, jamais une impossibilité géométrique implicite.

## Retour attendu

```text
P64-L08L Fusion 0.1.62 - commit <sha>
Cas public 28x30 : <statut> - <temps> - <moteur> - recertifié <oui/non>
Projet réel 28x30 : <statut> - <temps> - <moteur> - recertifié <oui/non>
Fusion réactive : <oui/non>
Agencement 3D cohérent : <oui/non + remarque>
```

Cette gate ne valide pas l’impression. `print-validated=false`.