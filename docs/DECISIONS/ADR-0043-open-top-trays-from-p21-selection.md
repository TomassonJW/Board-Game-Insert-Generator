# ADR-0043 - Bacs ouverts depuis une selection P21

## Statut

Accepte par validation humaine explicite P31 le 2026-07-11.

## Date

2026-07-11

## Contexte

P28 expose les envelopes P21 brutes dans Fusion. Le produit exige maintenant
des bacs fonctionnels sans que Fusion recalcule le plan. Les contrats existants
portent deja les cavites rectangulaires, les murs/fonds par defaut et une coupe
Fusion top-open, mais la selection locale ne les emploie pas encore.

## Options

1. Un bac ouvert par module P21, avec une cavite `free` unique.
2. Des compartiments asset-specific des le premier pas.
3. Une geometrie decidee dans Fusion.

## Decision

Retenir l option 1 : conserver l enveloppe P21, creer une cavite ouverte en
haut a partir des epaisseurs existantes de paroi et de fond, refuser les
enveloppes incapables de garder une cavite positive et conserver les assets
comme tracabilite non normative.

## Consequences

- Le premier resultat P31 est un vrai receptacle simple, pas un bloc plein.
- Le plan P21, les tolerances et le schema de draft restent inchanges.
- La CAD IR et Fusion gardent leurs primitives existantes.
- Les compartiments, encoches, formes et mecanismes restent des lots ulterieurs.
- Une observation Fusion puis une impression reelle restent obligatoires avant
  toute promesse de fabrication.

## Alternatives refusees

- Compartiments immediats : demande une nouvelle strategie de packing local.
- Recalcul Fusion : cree une seconde source de verite.
- Maintien des blocs P28 : incompatible avec le resultat produit vise.

## Suivi

Le rapport `docs/P31_FUNCTIONAL_TRAY_GATE.md` porte les invariants, preuves et
validation attendus. P31 est approuve ; l implementation doit preparer le smoke Fusion sans declarer de validation physique.
