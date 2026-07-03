# ADR-0006 - Explicit print profiles

## Statut

Accepte.

## Date

2026-07-03

## Carte liee

- `P3-M003 - Ajouter des profils d'impression`

## Contexte

Apres `P3-M002`, les offsets appliques par face sont explicites, mais les
valeurs de tolerance restent soit les valeurs V0 par defaut, soit des overrides
champ par champ dans `tolerances`.

La Phase 3 prevoit des profils d'impression afin de proposer des points de
depart lisibles pour PLA, PETG, impression rapide ou detail fin. Ces profils ne
doivent pas cacher les valeurs finales et ne doivent pas etre presentes comme
valides physiquement.

## Options

### Option A - Garder uniquement des overrides manuels

- Principe : ne pas ajouter de profil, laisser l'utilisateur renseigner chaque
  champ `tolerances`.
- Avantages : aucun risque de confusion sur des presets.
- Inconvenients : configuration verbeuse et peu guidante.
- Risques : duplication d'exemples divergents.
- Cout de maintenance : faible.
- Compatibilite MVP : correcte mais peu ergonomique.
- Facilite de test : forte.

### Option B - Ajouter des profils explicites et surchargeables

- Principe : ajouter un champ racine `print_profile`, resoudre un preset en
  `ToleranceProfile`, puis appliquer les overrides explicites de `tolerances`.
- Avantages : valeurs finales visibles, comportement local et testable,
  ergonomie meilleure sans service externe.
- Inconvenients : les presets peuvent etre mal interpretes comme calibres.
- Risques : confusion avec une validation physique.
- Cout de maintenance : raisonnable.
- Compatibilite MVP : forte.
- Facilite de test : forte.

### Option C - Ajouter des profils dynamiques externes

- Principe : charger des profils depuis fichiers externes ou service.
- Avantages : extensibilite future.
- Inconvenients : surface de validation plus large.
- Risques : dependance ou format premature.
- Cout de maintenance : eleve maintenant.
- Compatibilite MVP : faible.
- Facilite de test : moyenne.

## Decision

Retenir l'option B.

Le JSON V0 accepte un champ racine optionnel `print_profile`. Les profils
implementes sont :

- `default` ;
- `pla_standard` ;
- `petg_standard` ;
- `fast_draft` ;
- `fine_detail`.

Le loader resout d'abord le profil en `ToleranceProfile`, puis applique les
valeurs explicites de `tolerances` comme overrides champ par champ.

Cette decision n'autorise pas :

- la modification des valeurs du profil `default` sans gate humaine ;
- la validation physique des presets ;
- l'ajout de profils externes ;
- l'integration Fusion 360 ou STL/3MF.

## Consequences

### Positives

- Les rapports montrent le profil et les valeurs finales.
- Un utilisateur peut partir d'un preset puis surcharger un champ precise.
- Les valeurs restent dans le coeur Python pur et dans le JSON local.

### Negatives

- Les presets opt-in restent des hypotheses tant qu'ils ne sont pas calibres par
  impression reelle.
- Le loader doit maintenir une liste stricte de profils reconnus.

### Risques

- Un preset pourrait etre confondu avec une recommandation universelle. Les docs
  et rapports indiquent explicitement que les profils sont experimentaux et non
  valides physiquement.

## Alternatives refusees

- Overrides seuls : refuse pour ergonomie insuffisante apres `P3-M002`.
- Profils externes : refuse car premature et hors besoin V0.

## Suivi

- Tests loader pour profil inconnu, resolution et overrides.
- Tests rapports pour exposition du profil.
- `P3-M004` doit documenter un protocole de calibration physique.