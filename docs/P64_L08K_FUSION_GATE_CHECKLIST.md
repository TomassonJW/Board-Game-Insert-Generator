# P64-L08K — gate Fusion du solveur SCIP produit

## Statut avant retour humain

Gate préparée, mais non validée. `fusion-validated=false` et
`print-validated=false`.

Cette gate sépare volontairement deux questions :

1. SCIP 10.0.2 est-il réellement chargé et utilisé par BGIG dans Fusion ?
2. apporte-t-il un résultat utile sur le vrai cas limite de Thomas ?

Le petit contrôle automatisé à trois niveaux prouve l'empilement en Z et la
recertification BGIG. Il ne suffit pas à revendiquer la valeur sur les cas
limites. Le cas public 18 conteneurs / 20 éléments reste honnêtement
`bounded_unknown` en Normal et en Approfondi.

## Préparation faite par Codex

Codex doit, avant de demander une action humaine :

- intégrer et pousser le commit L08K dans `main` ;
- installer l'add-in `0.1.61` depuis ce commit ;
- vérifier l'archive SCIP, le runtime extrait, les avis et les marqueurs ;
- préserver l'ancien état local de la palette ;
- installer le projet `p64-l08k-real-18x20.bgig.json` ;
- sélectionner `Auto intelligent` et `Approfondi` ;
- écrire le marqueur exact du commit installé.

Thomas ne lance aucun script.

## Parcours humain — contrôle public

1. Dans Fusion, recharge l'add-in BGIG `0.1.61`, puis ouvre la palette.
2. Vérifie que le projet `p64-l08k-real-18x20` est chargé et que l'effort est
   `Approfondi`.
3. Clique une seule fois sur `Calculer l'agencement`, puis attends au maximum
   35 secondes. Ne relance pas pendant le calcul.
4. Ouvre le détail technique et relève :
   - le statut final ;
   - `external_scip_real_3d` ou, en cas de fallback, sa raison exacte ;
   - une invocation externe ;
   - zéro lane interne après SCIP ;
   - `solution_found` avec certificat BGIG, ou
     `no_solution_within_budget / bounded_unknown` sans prétendre impossible.

Le résultat automatisé attendu aujourd'hui sur ce cas public est
`bounded_unknown`. Une solution certifiée serait une amélioration réelle et doit
être signalée, mais elle n'est pas présumée.

## Parcours humain — gate réelle obligatoire

Charge ensuite ton vrai projet limite contenant beaucoup de conteneurs et
d'éléments, garde `Auto intelligent + Approfondi`, puis lance exactement un
calcul.

Si BGIG trouve une solution :

- vérifie que la source sélectionnée est SCIP ;
- vérifie que le certificat global est vert ;
- vérifie visuellement l'empilement en Z et l'absence de collision ;
- matérialise seulement après le certificat ;
- observe que la scène correspond bien au plan calculé.

Si BGIG ne trouve pas de solution :

- relève `bounded_unknown`, `unsupported`, `invalid_runtime` ou la raison exacte ;
- ne l'interprète pas comme une preuve d'impossibilité ;
- indique le temps observé et si Fusion est resté réactif ;
- ne relance pas sans nouvelle mission, afin de ne pas doubler le budget.

## Retour attendu

Retour minimal :

```text
P64-L08K Fusion 0.1.61 - commit <sha>
Cas public 18x20 : <statut> - <temps observé>
Mon vrai cas limite : <statut> - <temps observé>
Source SCIP visible : oui/non
Certificat BGIG : oui/non/non applicable
Empilement 3D cohérent : oui/non/non applicable
Fusion réactif pendant le calcul : oui/non
```

Une capture du détail technique est utile en cas de KO. Aucun bundle personnel
n'est ajouté au dépôt sans autorisation distincte.

Cette gate ne vaut jamais validation d'impression.