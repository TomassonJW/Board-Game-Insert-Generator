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
| P64-F01B | automatisé — terminé | incumbent, réservations, fermeture, réparation locale et certificat final |
| P64-F02B admissible | automatisé — terminé | volume ajouté égal, ratio d’expansion égal et fallback certifié |
| P64-L09V | préparation automatisée — observation humaine suivante | add-in 0.1.63, trois projets publics et checklist combinée |

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

Preuves acquises :

- [x] le placement minimal certifié devient l’incumbent initial ;
- [x] les réservations plateaux/livrets entrent avant toute expansion ; les
  futures enveloppes mécaniques restent explicitement à zéro ;
- [x] seules les faces Auto/Target admissibles reçoivent du volume ;
- [x] les cavités et leurs origines dans le repère minimal certifié restent
  fixes ;
- [x] chaque proposition repasse collisions, jeux, support matériel, boîte et
  réservations ;
- [x] une réparation locale est tentée après stagnation directe et avant tout
  nouveau placement global ;
- [x] itérations, candidats, réparations et temps partagent un budget unique ;
- [x] l’épuisement rend no_solution_within_budget, avec plan partiel non publié
  et non matérialisable ;
- [x] un projet avec réservation ne publie pas son incumbent minimal comme
  artefact sélectionnable ou witness ;
- [x] seule la CAD IR du finalized_plan globalement certifié est admise ;
- [x] tests ciblés : fermeture 3/3, staged 14/14, palette 29/29, DOM 39/39 ;
- [x] suite complète : 851/851 en 233,473 s, 1 test natif ignoré sous Python
  3.10 ;
- [x] preuve : P64_F01B_COUPLED_FINALIZATION_EVIDENCE.md.

## P64-F02B — partie admissible

Preuves acquises :

- [x] objectif « volume ajouté égal » ;
- [x] objectif « ratio d'expansion égal » ;
- [x] déterminisme à entrée et budget identiques ;
- [x] aucune contrainte dure affaiblie par un objectif secondaire ;
- [x] l'incumbent certifié est conservé si l'objectif n'améliore rien ;
- [x] l'harmonisation modulaire reste différée tant que P45/P46 ne fournit pas
  les contrats de faces nécessaires ;
- [x] tests ciblés : fermeture 5/5, staged 14/14, palette 29/29 ;
- [x] suite complète : 853/853 en 224,573 s, 1 test natif ignoré sous Python
  3.10 ;
- [x] preuve : P64_F02B_BALANCED_PROPORTIONAL_EVIDENCE.md.

## P64-L09V — actions restantes dans Fusion

Préparation automatisée :

- [x] add-in 0.1.63 versionné ;
- [x] trois projets publics et résumé à digest générés ;
- [x] préflight anti-chute, pontage, réservation et finalisation ;
- [x] préparateur local avec sauvegarde de l'état précédent ;
- [x] réglage Auto intelligent + Approfondi ;
- [x] vérification des marqueurs installés et du runtime SCIP ;
- [x] suite complète : 855/855 en 225 s, 1 test natif ignoré sous Python
  3.10 ;
- [x] preuve : P64_L09V_FUSION_GATE_PREPARATION.md.

Thomas, il te restera uniquement ceci après confirmation de l'installation :

1. recharge l'add-in BGIG 0.1.63 et ouvre la palette ;
2. ouvre le projet `01 anti-fall negative`, lance un seul calcul et vérifie
   qu'aucun petit conteneur n'est certifié au-dessus d'une ouverture qui peut
   l'avaler ;
3. ouvre `02 stable bridge`, lance un seul calcul et vérifie qu'un pontage
   matériel stable reste accepté ;
4. ouvre `03 tray finalization`, lance un seul calcul puis la finalisation ;
   vérifie que SCIP traite la réservation, que l'encastrement augmente Z sans
   réduire ni percer les cavités, puis matérialise uniquement le plan final ;
5. confirme que le volume utile est fermé proprement selon le plan final, que
   `has_lid` seul ne crée ni surface pleine ni nouvelle pose, et que
   `print-validated=false` reste affiché ;
6. donne pour chaque cas le statut, le moteur, le temps observé et tout
   diagnostic visible.

Observations à cocher après ton retour :

- [ ] anti-chute confirmée ;
- [ ] pontage stable confirmé ;
- [ ] réservation plateau réellement traitée par SCIP ;
- [ ] compensation Z sans atteinte aux cavités ;
- [ ] volume utile fermé par un finalized_plan certifié ;
- [ ] aucune scène issue d'un plan partiel ou non certifié ;
- [ ] aucune sémantique implicite de couvercle ;
- [ ] temps, statut, moteur et diagnostic consignés ;
- [ ] `print-validated=false` confirmé.

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
