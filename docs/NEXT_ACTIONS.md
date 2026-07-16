# Next Actions

Dernière mise à jour : 2026-07-16

## Version active

V0.1 reste mvp-accepted par P66 (package 0.1.20), fusion-validated: true et print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir de capacité géométrique ou physique.

## Dernier état réel

P44-M007 est implemented et automated-validated dans le package Fusion 0.1.37 :

- validation dérivée après 350 ms sans nouvelle édition ;
- proposition complète après 1 500 ms de stabilité ;
- réponses obsolètes ignorées par révision source et par dernière identité de requête ;
- `Recalculer maintenant` conservé comme fallback manuel ;
- statut compact et projections de l’Aperçu affichés avant les alertes et détails ;
- `Matérialiser dans Fusion` reste l’unique action de matérialisation et ne part jamais automatiquement ;
- `Hauteur de conception` reste dérivée, non éditable et visiblement grisée ;
- aucun schéma, bridge, solveur, budget, valeur physique, tolérance, géométrie ou comportement de scène n’est modifié.

P44-M009H05 reste fusion-validated dans Fusion 360 (package 0.1.36, preuve `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0`). P44-M007 n’est pas encore fusion-validated et aucune propriété physique ni impression réelle n’est validée.

## Prochaine action recommandée

### P44-M007V - Gate Fusion du calcul adaptatif et de l’Aperçu

Statut : human-fusion-check-required après installation du package 0.1.37.

Thomas vérifie dans Fusion uniquement :

1. plusieurs éditions rapides ne volent ni focus ni scroll ;
2. seul le calcul correspondant aux dernières valeurs devient visible ;
3. l’Aperçu automatique arrive après environ 1,5 seconde de stabilité ;
4. statut et projections précèdent alertes et détails ;
5. `Recalculer maintenant` fonctionne comme fallback sans créer de scène ;
6. `Hauteur de conception` est grisée et impossible à éditer ;
7. aucune scène BGIG ne change avant un clic explicite sur `Matérialiser dans Fusion`.

Preuve attendue :

```text
P44-M007 Fusion OK 0.1.37 - commit <sha>
```

Cette gate qualifie le comportement UI observé, pas les valeurs physiques, la géométrie imprimée ou l’impression.

Ne pas ouvrir P45/P46, P47-P50, P67, P68 ou P69 avant ce retour. P44-V reste la gate globale de fondation UX et print-validated: false reste obligatoire.

## Séquence verrouillée

P44-M005, P44-M006 et P44-M009H05 sont fusion-validated pour leurs parcours UX. P44-M007 est implemented et automated-validated ; P44-M007V est la seule action suivante autorisée. P45/P46 ne commencent pas avant P44-V ; P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des faits réels sans modifier les valeurs par défaut.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte. Une gate Fusion ne devient jamais une validation d’impression.