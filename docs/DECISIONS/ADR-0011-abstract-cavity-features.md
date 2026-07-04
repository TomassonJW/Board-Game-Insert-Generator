# ADR-0011 - Features ergonomiques abstraites de cavites

## Statut

Accepte

## Date

2026-07-04

## Carte liee

- `P5-M004 - Decrire les encoches de doigts et fonds arrondis comme features abstraites`

## Contexte

La vague P5 a deja introduit les cavites rectangulaires simples dans le coeur
Python pur, les rapports et la CAD IR. La gate humaine P5-M004 autorise seulement
les aides ergonomiques de cavites en abstrait : encoches de doigts, encoches
laterales ou centrales, demi-lunes, fonds arrondis et aides de prise en main.

Le risque principal est de confondre une intention ergonomique avec une operation
Fusion executable. Une encoche ou un fond arrondi implique a terme des coupes,
booleans, fillets ou geometries courbes, qui restent soumis a une gate humaine
separee.

## Options

### Option A - Generer directement les features dans Fusion

- Principe : mapper immediatement les encoches et rayons vers des cuts/fillets Fusion.
- Avantages : retour visuel rapide.
- Inconvenients : sort du perimetre autorise et melange moteur/adaptateur.
- Risques : geometrie fragile, booleans non testes, confusion avec validation CAD.
- Cout de maintenance : eleve des maintenant.
- Compatibilite MVP : faible pour cette gate.
- Facilite de test : faible hors Fusion.

### Option B - Documenter sans modele code

- Principe : decrire les futures features sans les charger depuis la configuration.
- Avantages : tres simple et sans risque CAD.
- Inconvenients : pas de flux testable configuration -> rapport -> CAD IR.
- Risques : futur adaptateur contraint d'inventer un contrat.
- Cout de maintenance : bas mais repousse la complexite.
- Compatibilite MVP : partielle.
- Facilite de test : limitee a la relecture.

### Option C - Modeliser des features abstraites liees aux cavites

- Principe : ajouter un contrat `Feature` explicite, local a une cavite, valide et
  serialise dans les rapports et la CAD IR.
- Avantages : garde le moteur source de verite et prepare Fusion sans l'executer.
- Inconvenients : ajoute un contrat de donnees a maintenir.
- Risques : certains placements resteront approximatifs tant qu'ils ne sont pas
  testes dans Fusion et par impression.
- Cout de maintenance : modere et localise.
- Compatibilite MVP : bonne.
- Facilite de test : bonne hors Fusion.

## Decision

Retenir l'option C.

Une feature ergonomique P5-M004 est une intention abstraite associee a une cavite.
Elle porte :

- un identifiant ;
- un kind parmi `finger_notch`, `side_notch`, `center_notch`,
  `half_moon_notch`, `rounded_floor` et `grip_aid` ;
- un placement humain ;
- une position locale dans la cavite ;
- une taille optionnelle ;
- un rayon optionnel ;
- un commentaire ;
- `status: abstract_only` ;
- `fusion_generation: not_implemented`.

Les features sont validees contre la cavite locale. Les encoches et aides de
prise en main requierent `size_mm`. Les demi-lunes et fonds arrondis requierent
`radius_mm`. La CAD IR les transporte dans `body.cavities[].features` et par
operations abstraites `describe_cavity_feature`.

Cette decision n'autorise pas de coupe Fusion, boolean, fillet, conge, extrusion
cut, geometrie courbe reelle ou export imprimable.

## Consequences

### Positives

- Le flux configuration -> validation -> rapports -> CAD IR devient testable.
- Fusion pourra mapper plus tard un contrat deja explicite.
- Les rapports distinguent clairement intention abstraite et generation CAD.

### Negatives

- Les placements restent des conventions abstraites tant qu'aucun adaptateur ne
  les materialise.
- Le contrat CAD IR V0 transporte maintenant plus de metadata non executees.

### Risques

- Une future mission Fusion pourrait executer trop tot ces operations. Mitigation :
  `fusion_generation: not_implemented`, documentation et gate obligatoire avant
  toute operation soustractive ou courbe reelle.

## Alternatives refusees

- Generation Fusion immediate : refusee par le perimetre P5-M004 et par la gate
  obligatoire suivante.
- Documentation seule : refusee car la mission demande un flux testable et
  exportable dans la CAD IR.

## Suivi

- `tests/test_model_contract.py` couvre les kinds autorises et les refus de
  features incoherentes.
- `tests/test_config_loader.py`, `tests/test_report.py` et `tests/test_cad_ir.py`
  couvrent chargement, rapports et CAD IR.
- Toute generation reelle de cavites, encoches, fonds arrondis, fillets, booleans
  ou geometrie courbe Fusion doit declencher une nouvelle gate humaine.
