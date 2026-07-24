# ADR-0082 — HiGHS 1.15.1 comme lane produit hors ligne

## Statut

Accepté.

> **Portée requalifiée — 2026-07-24.** ADR-0083 conserve cette décision pour une lane de sol rectangulaire, mais interdit de la lire comme un choix de solveur global. Cette lane est expérimentale ; P64-L08B mesure son impact avant toute nouvelle promotion.

## Date

2026-07-23

## Carte liée

- `P64-L07E — intégration mesurée du gagnant principal`

## Contexte

P64-L07A à L07D ont audité dix candidats puis comparé quatre moteurs externes
réels dans quatre familles. HiGHS est le meilleur candidat compatible avec le
produit après les gates de licence et de redistribution. Il a été scellé seul
avant l'ouverture unique du holdout.

Le holdout L07 est désormais consommé. Il a confirmé cinq solutions certifiées
sur sept cas représentables, mais il ne pouvait pas établir un gain produit :
ces cas imposaient une interdiction de rotation absente du schéma BGIG V1.
L07E a donc exécuté une gate distincte sur cinq régressions produit réellement
représentables, sans rouvrir ni régler le holdout.

Sur ces cinq cas communs, HiGHS et BGIG conservent le même nombre de solutions
certifiées. HiGHS gagne les deux comparaisons de qualité possibles, n'en perd
aucune et réduit la fragmentation résiduelle de 5 à 0. Les temps observés sont
1,308987 s contre 4,077502 s au total. Ces temps sont une observation de gate,
pas une promesse de performance.

## Options examinées

### Option A — ne pas intégrer le gagnant

- Avantage : aucune dépendance native supplémentaire.
- Inconvénient : abandonne deux gains de qualité produits sans régression
  observée.
- Risque : conserver une limite connue alors que la gate demandée passe.

### Option B — embarquer le wheel Python `highspy`

- Avantage : API structurée et proche de l'adapter de tournoi.
- Inconvénient : couple le paquet à l'ABI Python embarquée et à NumPy.
- Risque : compatibilité plus fragile avec le Python propre à Fusion.
- Coût : wheel et dépendances Python à maintenir et recertifier.

### Option C — embarquer le binaire CLI officiel Windows

- Avantage : pas d'import natif dans Python, aucun installateur BGIG, pas de
  dépendance à l'ABI de Fusion et isolement par processus.
- Inconvénient : ajoute 10,783 Mio au paquet source de l'add-in.
- Risque : processus natif à borner et protocole fichier à valider strictement.
- Coût : un exécutable, une DLL, leurs licences et un adapter Python pur.

## Décision

L'option C est retenue pour Windows x86_64.

BGIG embarque le paquet officiel `highs-1.15.1-x86_64-windows-mit.zip` publié
par le projet HiGHS :

- archive officielle : 5 517 021 octets ;
- SHA-256 archive :
  `26302d9024f307e09128a45a58898917287351dcf754c55aebc07742237f78bf` ;
- `highs.exe` : 906 752 octets, SHA-256
  `4ff24abf4cfdd5f4e87e73edf6886d1b9333c13c388b328466ca15a502b4c46d` ;
- `highs.dll` : 10 392 576 octets, SHA-256
  `722dfd5eb66e1de2fe306d8e6e9c68085ca1b454c04e1860dd22f636557e6de5` ;
- paquet redistribué complet : 11 307 594 octets, soit 10,784 Mio.

La licence principale est MIT. Le paquet inclut le texte HiGHS, les avis tiers
et les textes de licence utilisés par le CLI : CLI11, pdqsort et zstr. Les
empreintes et tailles sont verrouillées dans `ARTIFACT.json`.

L'inventaire PE du CLI et de sa DLL établit une dépendance au runtime déjà
présent de Windows : Universal CRT, `MSVCP140.dll`, `VCRUNTIME140.dll` et
`VCRUNTIME140_1.dll`. Le poste de validation expose ces trois DLL Microsoft
en version `14.44.35211.0`. BGIG ne les redistribue pas et ne lance aucun
installateur. Leur absence fait échouer le chargement natif puis active le
repli interne ; « sans installation globale » signifie donc qu'aucune
installation n'est effectuée par BGIG, pas que le binaire est autonome du
runtime Windows.

## Contrat runtime

1. La palette Fusion configure uniquement le chemin local du binaire fourni par
   l'add-in. Le cœur ne charge ni DLL ni module Python candidat.
2. Sur un système non Windows, la lane reste non configurée et le portefeuille
   interne continue seul.
3. Un seul processus HiGHS est autorisé par calcul minimal : dans Deep, il est
   appelé dans le préfixe Normal et jamais dans l'extension.
4. Le processus reçoit un modèle LP local, un seed fixe, un thread et une
   limite mémoire de 1 024 Mio.
5. La sous-limite murale ajoutée est de 0,75 s en Rapide et de 3 s en Normal ou
   Approfondi. Elle ne modifie aucun cap historique des lanes internes.
6. Les variables de placement sont entières au millième de millimètre. La lane
   accepte au plus 64 participants, un seul niveau, les rectangles orthogonaux
   et les rotations Z de 0 ou 90 degrés.
7. Toute réservation haute ou dimension non représentable répond
   `unsupported`.
8. Un statut d'infaisabilité du modèle de sol reste `bounded_unknown` pour le
   produit : ce modèle partiel ne prouve jamais l'impossibilité BGIG générale.
9. Une sortie positive devient seulement une proposition. Elle repasse par le
   certificat BGIG commun avant de rejoindre le classement existant.
10. Le portefeuille interne continue dans tous les cas. Il gagne normalement
    si sa proposition certifiée est meilleure.
11. La gate d'installation démarre le vrai CLI et vérifie ainsi le runtime
    Windows transitif sans installer ni réparer ce runtime.

## Isolement et échec fermé

Le lancement utilise un chemin absolu, `shell=False`, aucune entrée standard et
aucune fenêtre. Les variables de proxy sont retirées du processus et aucune
adresse réseau n'est fournie. Le modèle, les options et la solution vivent dans
un répertoire temporaire local supprimé après le run.

Les empreintes de l'exécutable et de la DLL sont contrôlées avant chaque appel.
Fichier absent, empreinte différente, erreur d'entrée-sortie, code de sortie
non nul, timeout, dépassement mémoire, solution illisible ou certificat refusé
laissent le portefeuille BGIG poursuivre. Aucun de ces cas ne devient une preuve
d'impossibilité.

Comme le statut peut dépendre d'une limite murale, un résultat ayant réellement
appelé HiGHS déclare honnêtement `deterministic: false`. Les mesures volatiles
restent hors du payload certifiable.

## Compatibilité vérifiée

Le CLI officiel a été comparé à l'adapter `highspy` scellé :

- trois petits contrôles exacts équivalents ;
- huit régressions avec le même statut ;
- aucune différence sur les axes de qualité lorsqu'une solution existe ;
- digest de la sonde :
  `3ea1e213bf26cdc667e7f23abdc6ca0b8d730956af857005f24e177c858bed63`.

Le paquet Fusion passe à `0.1.60`. L'installateur recopie le binaire, la DLL,
le manifest d'artefact, les avis et le module Python pur puis refuse un runtime
incomplet.

## Mise à jour et retrait

Il n'existe aucune mise à jour automatique. Une nouvelle version exige :

1. un nouvel audit officiel de la release et des licences ;
2. de nouvelles empreintes ;
3. la sonde CLI équivalente ;
4. les tests produit et packaging ;
5. une nouvelle décision documentée.

Le retrait consiste à désactiver la configuration dans la palette, supprimer le
répertoire `vendor/highs`, le module `highs_product_solver.py` et les marqueurs
de packaging. Les lanes internes et leur ordre restent alors identiques à
l'état antérieur.

## Conséquences

### Positives

- deux gains de qualité produits mesurés sans perte certifiée ;
- fonctionnement local, hors ligne et sans compte ;
- aucun installateur global déclenché par BGIG et aucune dépendance à l'ABI
  Python de Fusion ;
- repli BGIG conservé et certifié ;
- mise à jour et retrait bornés.

### Négatives

- le paquet Fusion augmente de 10,784 Mio ;
- la lane externe est limitée aux rectangles sur un seul niveau ;
- les temps deviennent non déterministes dès que le processus est invoqué ;
- le binaire produit intégré est Windows x86_64 seulement ;
- la lane externe suppose Universal CRT et le runtime Visual C++ 14 déjà
  présents ; leur absence conserve seulement le solveur interne.

### Risques résiduels

- aucune observation réelle dans Fusion 360 n'est encore enregistrée ;
- aucune impression n'est validée ;
- les formes T2 à T4, réservations hautes, empilements et poses arbitraires
  restent hors portée ;
- le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.

## Alternatives refusées

- adopter HiGHS sans gate produit : le holdout seul n'était pas comparable ;
- adopter OR-Tools en complément : aucune famille distincte gagnée ;
- adopter SCIP ou LAFF : gates produit de redistribution non satisfaites ;
- appeler un service distant : contraire au produit local et au runbook ;
- croire une preuve d'infaisabilité du modèle de sol : portée incomplète.

## Suivi

- conserver `fusion-validated: false` jusqu'à une observation dédiée P64-L07V ;
- conserver `print-validated: false` ;
- ne jamais rouvrir le holdout L07 ;
- comparer toute future version sous une nouvelle preuve indépendante.
