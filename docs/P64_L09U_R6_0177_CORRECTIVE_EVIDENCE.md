# P64-L09U-R6 — preuve corrective 0.1.77

Date : 2026-07-28.

Statut : `automated-validated`, `installed-local`, `ready-human-gate`.

`fusion-validated=false`, `print-validated=false`.

## Point de départ humain

0.1.76 est `human-KO`, `do-not-run`.

Deux défauts distincts ont été observés dans `CasLimite02+` :

1. une micro-partie de cavité sous plateau perdait exactement les `6 mm` du
   plateau et du livret ;
2. deux éléments plats de tailles XY différentes ne produisaient pas leurs
   deux encastrements locaux exacts.

Les faits complets sont consignés dans
`docs/P64_L09U_R5_V_0176_HUMAN_KO_EVIDENCE.md`.

## Première divergence

Le replay instrumenté sépare le plan minimal, les régions locales, les
intervalles Z, les cavités gelées, les accès, la fermeture, l'aperçu, la CAD IR
et le plan Fusion.

La première divergence apparaît dans la finalisation composite :

- les régions minimales distinguent déjà correctement `4 mm`, `2 mm` et leur
  cumul local `6 mm` ;
- la garde de fermeture appliquait encore ce cumul sur toute l'empreinte de
  l'élément inférieur ;
- la cavité micro-chevauchée était testée par un point central, donc son petit
  chevauchement réel n'était pas reconnu ;
- le plan de matérialisation choisissait ensuite une seule réservation
  responsable par cellule.

La CAD IR et le plan Fusion reproduisaient donc un contrat amont déjà faux.

## Contrat retenu

ADR-0102 impose une partition XY atomique et des intervalles Z locaux :

- seuls les éléments réellement présents dans une cellule cumulent leur
  épaisseur ;
- deux empreintes disjointes repartent indépendamment du sommet ;
- chaque intervalle d'élément plat survit jusqu'au plan Fusion ;
- tout chevauchement rectangulaire réel supérieur à l'epsilon compte, même
  lorsqu'il est plus petit qu'une paroi ;
- aucune valeur physique, aucun jeu et aucune tolérance ne changent.

## Correctifs

- La garde Z conservative est remplacée par l'union exacte des régions locales.
- La fermeture reconnaît deux corridors techniques légitimes :
  la croix des jeux XY et la mosaïque d'un jeu Z entre plusieurs propriétaires.
- Un résiduel partiellement consommé est découpé avant attribution, au lieu
  d'être accepté en bloc ou rejeté sans preuve.
- Une cavité est rattachée par intersection de rectangles, jamais par son seul
  centre.
- Toutes les réservations actives d'une cellule deviennent des coupes
  distinctes avec identité et intervalle Z.
- Le plan Fusion conserve `flat_item_id`, `local_interval_bottom_z_mm` et
  `local_interval_top_z_mm`.
- L'identité du finaliseur passe à
  `bgig.bounded_coupled_finalization.v12`.

## Régressions

Les tests couvrent notamment :

- micro-chevauchement plus petit qu'une paroi ;
- cavité calibrée de `10 mm` sous un cumul local de `6 mm` ;
- empreintes imbriquées et partiellement recouvrantes ;
- empreintes disjointes ou côte à côte ;
- croix de jeux XY et mosaïque de jeu Z ;
- conservation de deux intervalles jusqu'au plan Fusion ;
- variantes `60×80`, `60×82` et `60×85`.

Résultats :

- régressions finalisation/fermeture : `30/30` ;
- matrice finalisation, CAD IR et Fusion : `104/104` ;
- gates version/correctif/release : `21/21` ;
- préparateur sec : `136/136` ;
- suite globale autorisée : `909/909` en `415.612 s`, un test SCIP ignoré ;
- exactement douze modules benchmark/holdout/corpus/tournoi exclus ;
- aucun benchmark, holdout, corpus ou tournoi exécuté.

Une invocation isolée très large de `test_fusion_skeleton.py` a atteint son
timeout gardé de `180 s`. La suite globale autorisée, qui contient ce module,
s'est ensuite terminée intégralement en succès.

## Replays personnels en lecture seule

Source :
`C:\Users\janko\Documents\BGIG\projects\CasLimite02+.bgig.json`.

SHA-256 avant et après tous les replays :

```text
5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC
```

Les copies `60×82` et `60×85` ont été créées uniquement sous `.codex-work`,
contrôlées avant/après, puis supprimées.

Les trois variantes calculent, finalisent et produisent un plan Fusion :

| Livret | Calcul | Finalisation | Résultat |
|---|---:|---:|---|
| `60×80×2` | `9498.717 ms` | `1269.156 ms` | CAD IR et plan Fusion prêts |
| `60×82×2` | `9644.994 ms` | `1216.922 ms` | CAD IR et plan Fusion prêts |
| `60×85×2` | `11694.621 ms` | `2676.007 ms` | CAD IR et plan Fusion prêts |

Dans `c4`, la cavité micro-chevauchée conserve ses `10,4 mm` de coupe réelle.
Les zones communes transportent séparément une coupe plateau de `4 mm` et une
coupe livret de `2 mm`.

## Preflight

Version : `0.1.77`.

Digest :

```text
de55e8e85652ecb6d01e44b7494b7adc7f92ee2472c8e3c6874836f93823f6b6
```

Le préparateur à blanc passe, sans écrire dans AppData ni dans les projets
personnels.

## Installation

Le commit `e81737d` est intégré dans `origin/main`. Son package 0.1.77 est
installé et vérifié localement :

- manifeste : `0.1.77` ;
- marqueur installé : `e81737d` ;
- runtime embarqué, réglages et marqueurs CAD : conformes ;
- fixture publique et reçus : installés ;
- projet personnel `CasLimite02+` : SHA-256 inchangé après installation.

## Limite restante

La géométrie réelle dans Fusion n'a pas encore été observée. La nouvelle gate
humaine reste obligatoire avant toute promotion de statut.
