# Journal — P64-L08F tournoi réel 3D

Date : 2026-07-24

## Mission

Exécuter discovery, tuning, sélection scellée et holdout unique sur les cas
limites 3D BGIG, sans intégrer de moteur pendant L08F.

## Exécution

- quatre moteurs externes et quatre familles réellement appelés hors ligne ;
- 24 contrôles exacts, 120 lignes discovery, 80 lignes tuning ;
- SCIP sélectionné principal, OR-Tools et LAFF comme compléments ;
- code, artefacts, caps, graines et routes scellés avant le holdout ;
- ouverture publique reçue une fois pour 40 cas privés ;
- 120 lignes de holdout checkpointées sans double exécution ;
- aucun échec de worker, aucun tuning après ouverture, aucun trafic réseau.

## Incident de validité et récupération

La postproduction initiale crédite la baseline BGIG de 10 impossibilités en
lisant directement une borne de corpus. Ce n'est pas un solve réel. Le verdict
initial et son digest `508c9b1e...` sont invalidés avant commit.

La récupération réapplique les règles du programme sans rouvrir le holdout et
sans rappeler un worker : 10 lignes baseline deviennent `bounded_unknown`, les
80 résultats externes restent identiques, sélection, routes, caps et graines ne
changent pas. Les futures entrées worker ne transportent plus la vérité ni la
borne du corpus.

## Décision

Le portefeuille gagne 5 vérités et en perd 3 face à SCIP : il est rejeté. SCIP
seul gagne 18 vérités et n'en perd aucune face au comportement BGIG corrigé.
SCIP est donc le gagnant benchmark.

La gate produit reste fermée : les avis et dépendances natives Windows de
SCIP/PySCIPOpt doivent encore être entièrement versionnés. Aucun moteur n'entre
dans Auto, Normal ou Approfondi pendant L08F. Aucune gate Fusion n'est ouverte.

## Validation

- tests L08 ciblés : 24/24 ;
- suite complète : 793/793 en cinq partitions bornées ;
- style, compilation, garde documentaire, alignement Fusion-only et
  `git diff --check` : OK.
## Preuve

- `docs/P64_L08F_REAL_3D_TOURNAMENT_EVIDENCE.md` ;
- preuve récupérée :
  `0dbf1b45ae9135c1316051ab7e0946dfbfeafac5c785ad96ccd5d7a620acd46d` ;
- reçu de récupération :
  `0fc672b479074f446d333bf3a8ac4bd16f8e3caeadb8f70dec4fcd9a939e5001` ;
- campagne brute :
  `1b9e2c722e43632fa44c56046cbba6098d406577694bfd846c09730c895c448c`.
