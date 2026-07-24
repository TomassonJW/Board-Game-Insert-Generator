# P64-L09 — validation unifiée

Date de mise à jour : 2026-07-24
Périmètre : P64-L09B, P64-L09C, P64-F01B, partie admissible de P64-F02B,
préparation P64-L09V.

Ce fichier est la liste canonique des preuves à exécuter pendant le Goal. Il
sépare les preuves automatisées déjà acquises des observations qui resteront à
faire dans Fusion.

## État synthétique

| Lot | État | Preuve principale |
| --- | --- | --- |
| P64-L09B | automatisé — terminé | support réel, chute, pontage, stabilité, parité des voies |
| P64-L09C | automatisé — terminé | réservations supérieures fidèles dans SCIP et preuve native CPython 3.14 |
| P64-F01B | à exécuter | fermeture couplée bornée et réparation locale |
| P64-F02B admissible | à exécuter | volume ajouté égal et ratio d'expansion égal |
| P64-L09V | bloqué par l'implémentation | gate Fusion combinée |

## P64-L09B — support matériel

Preuves acquises :

- [x] un solide expose une face pleine ;
- [x] un conteneur ouvert expose ses rebords, pas son enveloppe XY pleine ;
- [x] une empreinte qui tient dans l'ouverture est rejetée avec
  `falls_through_opening` ;
- [x] un pontage dont les appuis encadrent le centre est accepté ;
- [x] un appui suffisant en aire mais unilatéral est rejeté avec
  `unstable_support_polygon` ;
- [x] une aire matérielle inférieure à 25 % est rejetée ;
- [x] `has_lid` sans certificat ne ferme rien ;
- [x] le validateur commun recalcule la preuve avant publication ;
- [x] greedy, beam, fermeture continue, SCIP et stage-stack utilisent la même
  autorité ;
- [x] les anciens plans non conformes deviennent
  `no_solution_within_budget`, jamais des impossibilités prouvées ;
- [x] suite complète : 843/843.

## P64-L09C — réservations supérieures SCIP

Preuves acquises :

- [x] `_prepare_product_problem` accepte les `top_inset_zones` représentables ;
- [x] chaque zone conserve exactement son origine XY, sa taille XY, son plan
  d’appui et sa profondeur ;
- [x] le modèle SCIP interdit tout corps incompatible dans le prisme réservé ;
- [x] une cavité compatible peut recevoir la compensation Z sans réduction de
  son volume ;
- [x] retrait, prise, paroi et fond restent certifiés par le validateur final ;
- [x] un cas avec plateau atteint réellement la lane SCIP sous CPython 3.14 ;
- [x] un cas non représentable reste fail-closed avec un statut borné honnête ;
- [x] aucune approximation silencieuse ni fallback présenté comme preuve SCIP ;
- [x] worker natif : 1/1, `solution_found`, une invocation ;
- [x] tests ciblés : SCIP 16 cas sous Python 3.10 avec le cas natif ignoré,
  encastrements 8/8, placement minimal 14/14 ;
- [x] suite complète : 847/847 en 242,868 s, un test natif ignoré sous
  Python 3.10 puis exécuté séparément 1/1 sous CPython 3.14.

## P64-F01B — fermeture couplée bornée

À prouver :

- [ ] le placement minimal SCIP devient l'incumbent initial ;
- [ ] réservations et futures enveloppes mécaniques sont introduites avant la
  fermeture ;
- [ ] seules les faces admissibles reçoivent du volume ;
- [ ] les cavités et leurs origines certifiées restent fixes ;
- [ ] toute expansion est revalidée contre collisions, jeux, support matériel
  et réservations ;
- [ ] une réparation locale est tentée avant tout nouveau placement global ;
- [ ] itérations, candidats et temps sont bornés par un budget unique ;
- [ ] l'épuisement rend `no_solution_within_budget`, jamais un plan partiel
  matérialisable ;
- [ ] seul le plan final globalement certifié peut produire la CAD IR.

## P64-F02B — partie admissible

À prouver séparément :

- [ ] objectif « volume ajouté égal » ;
- [ ] objectif « ratio d'expansion égal » ;
- [ ] déterminisme à entrée et budget identiques ;
- [ ] aucune contrainte dure affaiblie par un objectif secondaire ;
- [ ] l'incumbent certifié est conservé si l'objectif n'améliore rien ;
- [ ] l'harmonisation modulaire reste différée tant que P45/P46 ne fournit pas
  les contrats de faces nécessaires.

## P64-L09V — observations Fusion à remettre à Thomas

Cette section ne sera marquée prête qu'après L09C et F01B automatisées.

Observations prévues :

- [ ] le petit conteneur ne peut plus être empilé au-dessus d'une ouverture
  dans laquelle il tombe ;
- [ ] un pontage réellement stable reste accepté ;
- [ ] le projet avec plateau atteint le solveur et ne produit plus le refus
  `top_inset_reservations_not_supported` ;
- [ ] l'encastrement du plateau augmente Z sans réduire ni percer les cavités ;
- [ ] le plan final remplit le volume utile selon l'objectif choisi ;
- [ ] aucune scène n'est créée depuis un plan partiel ou non certifié ;
- [ ] `has_lid` seul n'autorise ni support plein ni nouvelle pose ;
- [ ] temps observé, statut, moteur et diagnostic sont consignés ;
- [ ] `print-validated=false` reste affiché.

## Commandes canoniques

Les commandes longues sont exécutées avec le wrapper Windows gardé du projet.

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
git diff --check
git diff --cached --check
```

Chaque lot doit aussi exécuter ses tests ciblés, enregistrer leur nombre et
mettre à jour cette fiche avant son commit.
