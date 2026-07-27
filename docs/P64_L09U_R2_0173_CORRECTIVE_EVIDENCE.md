# P64-L09U-R2 — preuve corrective 0.1.73

## Portée

R2 corrige uniquement :

- l'identité du plan final ;
- la fidélité de l'aperçu composite ;
- les cellules et jeux de fermeture ;
- l'insertion tardive d'un support de pile ;
- l'exécution Fusion des booléens rectangulaires.

Les jobs annulables, les miniatures de variantes et la nouvelle épaisseur de
séparateur restent hors portée.

## Résultat fonctionnel

- La finalisation utilise un seul candidat : le minimum exact sélectionné.
- Les poses et dimensions des cavités gelées restent identiques entre minimum,
  final, CAD IR et plan Fusion.
- L'aperçu projette chaque prisme composite réel.
- Une annexe retire toutes les cellules entièrement couvertes.
- Les jeux externes XY/Z et leurs jonctions restent vides et certifiés.
- `CasLimite01+` sans plateau finalise avec un résiduel imprimable nul.
- `CasLimite01++` calcule puis finalise grâce à l'insertion tardive d'un support
  large sous la pile.
- La matérialisation rectangulaire construit un BRep transitoire complet par
  module, puis le persiste une seule fois.
- Le compte de features Combine paramétriques rectangulaires est zéro.
- Le rollback de scène après erreur reste actif.

## Replays exacts en lecture seule

Le préparateur sec exécute six variantes locales et rapporte :

```text
P64_L09T_LOCAL_REPLAY status=passed cases=6 read_only=true
```

Les projets personnels restent hors dépôt et inchangés.

SHA-256 avant et après :

- `CasLimite01+` :
  `998ce73153cf5657f2653222e6cc57f6598b5ddefd0b11b2f57b0db8ff831090` ;
- `CasLimite01++` :
  `7ccac58e6304ae38bfbee38b9aee9f78fa05919e1ce72bed2efacdbaa95181bb` ;
- `CasLimite02+` :
  `53c1f607b033378b3a6228a49b9815fa1e663ccc9effa31021cbe55981175fe2`.

## Preflight

```text
P64_L09UW_PREFLIGHT_OK
version=0.1.73
digest=e8392bc12c69074e654d1d9cecf99656df5fe9ac187eb17d1b981a713584b6fd
join_batches=1/41
cut_batches=1/17
```

Le ratio de lots décrit toujours le regroupement logique du CAD IR. L'adaptateur
Fusion exécute désormais ces opérations dans le corps transitoire du module et
ne crée aucune feature Combine rectangulaire.

## Vérifications passées

- tests de fermeture composite, dont jeux Z et jonctions XY/Z ;
- tests du solveur de piles et support tardif ;
- tests d'aperçu composite et cavités gelées ;
- tests de matérialisation Fusion avec mocks de booléens transitoires ;
- matrice release publique historique ;
- préparateur 0.1.73 complet en mode sec ;
- six replays personnels exacts en lecture seule.

- matrice ciblée du préparateur : `109/109` ;
- suite globale autorisée : `886/886` en `363.209 s` ;
- modules exécutés : `113` ;
- modules benchmark/holdout/corpus/tournoi exclus : `12` ;
- test ignoré : `1`, intégration SCIP native indisponible sous Python 3.10.

## Installation et préparation de la gate

- package installé : `0.1.73` ;
- commit du paquet : `b5fb15b` ;
- manifeste, marqueur de commit et quatre marqueurs du chemin booléen
  transitoire : vérifiés ;
- réglages installés : aucun projet courant persistant ;
- fixture, résumé de preflight et résumé des replays : préparés dans le dossier
  personnel de projets ;
- SHA-256 des trois projets personnels : inchangés après installation.

## Limites et statut

- Aucun benchmark, holdout ou corpus solveur n'est ouvert.
- Aucune valeur physique n'est ajoutée ou changée.
- Les tests hors Fusion ne prouvent ni la réactivité réelle ni la géométrie
  visible de l'API Fusion.
- `fusion-validated=false`.
- `print-validated=false`.
- Gate : `ready-human-gate`, `prepared-not-human-observed`.
