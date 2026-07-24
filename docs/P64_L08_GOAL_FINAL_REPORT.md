# P64-L08 — rapport final du Goal benchmark 3D réel

Date : 2026-07-24

> Mise à jour post-rapport : la conclusion produit négative de L08G est
> supersédée par les missions autorisées L08H à L08J. L'ABI `cp314` est réparée
> et un runtime SCIP minimal redistribuable passe la gate de build et
> d'équivalence publique. L'intégration produit reste à réaliser dans L08K ; ce
> document conserve la preuve historique du tournoi A à G et ne décrit plus
> l'état courant à lui seul.

Statut : `done`, `automated-validated`, `benchmark-winner-scip`,
`negative-no-product-integrable-winner`, `holdout-consumed`, `no-fusion-gate`.

`fusion-validated: false`

`print-validated: false`

## 1. Réponse courte

Le vrai benchmark 3D demandé est terminé. Il ne se limite ni au cas 11 × 34,
ni à un remplissage de sol, ni à des cas faciles : quatre moteurs externes de
quatre familles ont été exécutés sur les dix familles de cas limites BGIG,
avec empilement, multi-appui, réservations haut/bas, fragmentation, accès,
variantes et fortes cardinalités.

SCIP 10.0.2 est le meilleur moteur externe mesuré. Sur le holdout neuf de
40 cas, il gagne 18 vérités et n'en perd aucune face au vrai comportement BGIG
corrigé. Le portefeuille SCIP + OR-Tools + LAFF est rejeté parce qu'il perd
3 vérités face à SCIP seul.

Le benchmark est donc positif, mais l'intégration produit est négative : le
runtime PySCIPOpt acquis n'est pas compatible avec le Python de Fusion et ses
avis/dépendances natives ne sont pas entièrement redistribuables sur preuve.
Conformément à la gate préenregistrée, aucun moteur n'est intégré par hypothèse
et aucune fausse gate Fusion n'est ouverte.

## 2. Missions exécutées

| Mission | Résultat | Commit intégré |
| --- | --- | --- |
| L08A | correction de portée et gate de solvage 3D réel | `83987f8b8827c30f285f551f20e996ab84de2ccd` |
| L08B | diagnostic de lenteur et quarantaine de la lane HiGHS 2D | `decc03ac22aadacde690fed15c006b32372fd18c` |
| L08C | audit officiel des moteurs réellement 3D | `0516aaf1f39724a464bc54f85c42806553e0967f` |
| L08D | corpus adversarial, témoins et holdout neuf | `170b10fafcf50a650b31a8edd6da1f439d268ba9` |
| L08E | quatre adaptateurs 3D fidèles et contrôles exacts | `96018fd2dd12d1854bafd5ffcdf999c38a81dcd1` |
| L08F | tournoi, sélection scellée et holdout unique | `63f198dea91a7cb82f05d6b08e51c6b454a139fb` |
| L08G | gate produit SCIP fail-closed | commit contenant ce rapport |

Chaque mission A à F a été intégrée et poussée dans `main` avant la suivante.
Le SHA L08G distant est vérifié pendant la clôture Git de ce rapport.

## 3. Concurrence réellement exécutée

| Moteur | Famille | Fidélité 3D exécutée |
| --- | --- | --- |
| PackingSolver `box` | packing 3D natif spécialisé | X/Y/Z et rotations ; refus explicite des règles non traduites |
| LAFF 4.2.1 | construction 3D par niveaux | empilement natif sur les familles fidèles ; refus explicites ailleurs |
| OR-Tools CP-SAT 9.15.6755 | contraintes CP/SAT | formulation complète des règles BGIG mesurées |
| SCIP 10.0.2 / PySCIPOpt 6.2.1 | CIP/MIP | formulation complète indépendante, gagnante |

BGIG et les oracles internes sont restés des références. Ils ne comptent pas
dans ces quatre concurrents externes.

Campagne :

- 24 petits contrôles exacts ;
- 120 lignes discovery ;
- 80 lignes tuning ;
- 40 cas privés ouverts exactement une fois après sélection scellée ;
- aucune sortie positive acceptée sans recertification BGIG fraîche ;
- aucun service, compte, secret, réseau, télémétrie ou installation globale à
  l'exécution du tournoi.

## 4. Verdict benchmark

La sélection scellée retenait SCIP principal avec OR-Tools et LAFF comme
compléments conditionnels. Le holdout donne :

- portefeuille contre SCIP : +5 vérités, −3 vérités, une victoire et une perte
  de qualité ; portefeuille rejeté ;
- SCIP contre BGIG corrigé : +18 vérités, −0 vérité ;
- `benchmark_winner_demonstrated=true` ;
- `portfolio_beats_primary=false` ;
- moteur retenu : SCIP seul.

Une erreur de post-traitement a été détectée avant publication : la baseline
BGIG lisait une borne négative du corpus au lieu de résoudre dix cas. La
récupération a supprimé ces fausses preuves à partir des sorties existantes,
sans rappeler aucun worker, rouvrir le privé, modifier la sélection ou retuner.

Digest final L08F :
`0dbf1b45ae9135c1316051ab7e0946dfbfeafac5c785ad96ccd5d7a620acd46d`.

## 5. Gate produit L08G

Deux wheels déjà acquis sont audités :

- PySCIPOpt 6.2.1 : 48 289 786 octets ;
- NumPy 2.2.6 : 12 904 620 octets ;
- total décompressé dans les wheels : 187 848 352 octets ;
- dix DLL verrouillées individuellement par SHA-256.

Quatre blocages imposent le refus :

1. wheel PySCIPOpt `cp310` contre Python Fusion `cp314` dans Fusion 2704.1.36 ;
2. versions exactes incomplètes pour plusieurs composants natifs ;
3. avis SCIP, Ipopt, MUMPS, Intel et Microsoft absents ou incomplets ;
4. autorité de redistribution de ces binaires précis non entièrement établie.

Décision : `product_integration_authorized=false` et
`negative_no_product_integrable_winner`.

Ce refus ne retire rien au classement algorithmique de SCIP. Il interdit
seulement de transformer un résultat de benchmark en dépendance produit non
maîtrisée.

Digest L08G :
`a8ddb80e48ba83f9e3869f0bd3fffc7447be997b2c5932daf781775a7cbcc09a`.

## 6. Produit et gate humaine

Aucun runtime SCIP, wheel ou DLL n'est ajouté à l'add-in. Aucune lane, cap,
deadline, graine, tolérance, certificat, schéma, propriété P45/P64,
finalisation, géométrie, CAD, scène ou valeur physique ne change.

Il n'existe donc aucune solution post-benchmark intégrée à montrer honnêtement
dans Fusion à ce stade. L08G ne prépare et n'installe aucune gate humaine.
`fusion-validated=false` et `print-validated=false` restent exacts.

## 7. Validation finale

- audit SCIP hors ligne et génération de preuve : OK ;
- tests ciblés L08G : 4/4 ;
- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- Ruff format/check ciblé : OK ;
- compilation Python ciblée : OK ;
- suite complète : 797/797 en 270,144 s sous garde Windows, code 0 ;
- holdout rouvert : non ; worker privé rappelé : 0 ; tuning post-holdout : 0 ;
- diff-check, staged diff-check et SHA distant : vérifiés pendant la clôture Git.

## 8. Limites maintenues

- T0/T1 seulement ; aucune forme T2 à T4 ;
- aucune auto-modification ;
- aucune nouvelle revendication de résolution dense 11 × 34 ;
- le holdout L08F est consommé et interdit à tout nouveau réglage ;
- une solution benchmark n'est pas une validation Fusion ou d'impression.

## 9. Prochaine étape recommandée

P64-L08H peut remédier uniquement au paquet, sans refaire le tournoi : auditer
un wheel PySCIPOpt 6.2.1 `cp314` ou un exécutable SCIP 10.0.2 autonome,
verrouiller toutes ses obligations, puis prouver une exécution hors ligne dans
un environnement compatible Fusion. Si cette gate passe, une mission séparée
devra créer l'ADR, intégrer SCIP, rejouer les régressions ouvertes et seulement
alors installer une gate Fusion humaine.

Aucun autre moteur ne peut remplacer SCIP après lecture du holdout, et aucune
future remédiation ne peut utiliser ce holdout pour régler le moteur.
