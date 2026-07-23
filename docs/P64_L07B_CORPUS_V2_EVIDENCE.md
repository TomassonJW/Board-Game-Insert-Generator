# P64-L07B — preuve du corpus externe et BGIG V2

Date : 2026-07-23

Statut : `done`, `implemented-core`, `automated-validated`.

`fusion-validated: false`. `print-validated: false`.

## 1. Résultat

P64-L07B livre un manifest neuf
`bgig.solver_benchmark_manifest.v2` pour la campagne externe :

- huit régressions L05D1/L06 sont conservées sans modifier leurs digests ;
- 192 nouveaux cas BGIG T0/T1 sont répartis en 64 `discovery`, 64 `tuning` et
  64 `holdout` ; seules les 128 recettes ouvertes sont dans le manifest, les 64
  recettes du holdout restent dans un sidecar local ignoré par Git ;
- OR-Library THPACK9 et Q4RealBPP v1 apportent huit contrôles publics ouverts ;
- quatre petits contrôles BGIG possèdent une vérité positive ou négative
  vérifiée sans lancer de solveur candidat ;
- le nouveau holdout est indépendant de L06 et scellé par deux digests ; ni
  ses graines, ni ses recettes, ni ses réponses ne sont reconstructibles depuis
  le dépôt avant une sélection préalable complète ;
- aucun moteur externe, solveur BGIG, finaliseur, CAD ou adaptateur Fusion n'a
  été exécuté sur le holdout.

Digest du manifest V2 :
`828c4df787b07b35040a6026db0cfd43efa20c5b9c01f42eefd63a3607a48c9c`.

Engagement des 64 recettes du nouveau holdout :
`706f0452410fb877d77a87f1df08a6f558167f5a5a98f30f421ccb37d1e0296a`.

Digest du sidecar scellé :
`4ec4eb2cc8cea01c71cd3073857d0c152b4f8a3e4c3d6b5fac25edc49b400bcc`.

## 2. Sources publiques verrouillées

| Source | Droit vérifié | Artefact | Empreinte SHA-256 | Usage |
| --- | --- | ---: | --- | --- |
| [OR-Library THPACK9](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/thpackinfo.html) | [MIT pour le contenu OR-Library](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/legal.html) | 3 818 octets | `a4f5e3a748709217cdc749f7d27940f15b9f2a31b3e840e725642237036f82cc` | quatre contrôles publics |
| [Q4RealBPP v1](https://data.mendeley.com/datasets/y258s6d939/1) | GPLv3 indiqué par la version publiée | 12 201 414 octets | `dd3825b8abac54e04e748777d654065e176bb6ddf5e479cbeb638630fdb22fb4` | cas dimensionnels 1, 3, 5 et 7 |

L'archive Q4RealBPP a été téléchargée deux fois depuis l'endpoint public de la
version 1 ; les deux octets-à-octets donnent la même empreinte. Les quatre
fichiers sélectionnés possèdent aussi une taille et une empreinte propres dans
le manifest.

Les données Q4RealBPP ne sont pas recopiées dans le dépôt. Le téléchargeur
`scripts/solver/fetch_public_solver_benchmark.py` écrit uniquement vers le cache
choisi par l'appelant, refuse d'écraser un fichier, borne la lecture à 64 Mio et
valide l'archive avant renommage atomique.

## 3. Correspondance des objectifs

THPACK9 demande de charger tout le lot dans le nombre minimal de conteneurs
identiques. La projection utilisée fixe un nombre de conteneurs et pose la
question de faisabilité correspondante. C'est une réduction exacte de
l'objectif, sans retirer les objets, les dimensions, les permissions
d'orientation ni la non-intersection.

Les cas Q4RealBPP 1, 3, 5 et 7 fixent un seul conteneur et n'ajoutent que les
dimensions. Leur question devient directement : « tous les objets peuvent-ils
tenir dans cette boîte ? ».

Ces deux sources ne décrivent toutefois pas les règles BGIG d'appui complet, de
retrait, de réservation ni les variantes locales P45. Les huit cas publics sont
donc marqués `public_method_control_only`,
`product_ranking_eligible: false` et `holdout_eligible: false`. Une solution
publique ne peut jamais devenir une réussite produit sans passer par une entrée
BGIG complète et sa recertification.

## 4. Corpus BGIG V2

Le générateur L06 validé est réutilisé avec :

- le préfixe distinct `l07-v2-` ;
- les bases de graines ouvertes `640710000` et `640720000` pour discovery
  et tuning ;
- des graines et un nonce aléatoires conservés uniquement dans le sidecar local
  du holdout, sans affichage dans les sorties de commande ;
- aucune réutilisation d'identifiant, de graine, de digest projet ou de digest
  de projet précédent entre `discovery`, `tuning` et `holdout`.

Chaque split couvre :

- cinq familles : nombreux conteneurs/un contenu, peu de conteneurs/nombreux
  contenus, nombreux/nombreux, cas mixtes denses et paire incrémentale/froide ;
- 2, 4, 8, 12, 18, 30 et 50 groupes ;
- 1, 2, 4, 8, 16 et 32 contenus par conteneur ;
- un à trois niveaux ;
- réservations absentes ou contraignantes ;
- rotation permise ou interdite par le benchmark ;
- exécution froide et incrémentale ;
- témoins faisables construits et preuves négatives strictes de volume ou de
  hauteur.

Le générateur historique reste bit-à-bit compatible avec la fixture L06. Une
nouvelle entrée publique permet seulement de fournir des graines et identifiants
de campagne distincts.

## 5. Petits contrôles exacts

`discovery` et `tuning` possèdent chacun :

- un petit cas faisable avec placement construit vérifié ;
- un petit cas impossible avec borne stricte vérifiée ;
- au plus quatre groupes ;
- aucun témoin transmis au moteur testé.

Ces quatre contrôles sont destinés à la première gate L07C. Ils ne remplacent
pas les régressions ni les cas complexes.

## 6. Holdout neuf

Le holdout L06 est enregistré comme
`consumed_open_regression_archive_only`. Son engagement et ses réponses ne
participent pas à la sélection L07.

Le nouveau holdout V2 :

- possède 64 nouveaux cas et des graines propres ;
- conserve ses recettes dans
  `.codex-work/p64-l07/sealed_holdout.v2.json`, checkpoint local ignoré par Git
  qui ne doit pas être lu avant la sélection L07D ;
- ne publie dans le manifest que le nombre de cas, l'engagement des recettes et
  le digest du sidecar ;
- n'accepte aucun cas public dont la réponse est déjà consultable ;
- refuse toute matérialisation sans le sidecar exact et un fichier de sélection
  V2 lié au digest du corpus ouvert ;
- exige un candidat principal, zéro à deux compléments, un routeur, les digests
  du code, du corpus ouvert et des réglages, ainsi que l'enveloppe totale ;
- interdit tout réglage après ouverture ;
- impose une nouvelle version de manifest pour une itération ultérieure.

Construire et vérifier les témoins lors de la génération n'est pas un run
solveur. Le compteur de lancement du holdout reste exactement zéro à la clôture
de L07B.

## 7. Fichiers livrés

- `src/board_game_insert_generator/external_solver_benchmark_corpus.py` ;
- `src/board_game_insert_generator/solver_benchmark_corpus.py` ;
- `scripts/solver/build_external_solver_benchmark_manifest.py` ;
- `scripts/solver/create_external_solver_holdout.py` ;
- `scripts/solver/fetch_public_solver_benchmark.py` ;
- `tests/fixtures/p64_l07b_solver_benchmark.v2.json` ;
- `tests/test_external_solver_benchmark_corpus.py` ;
- ce document et le journal de mission.

## 8. Vérifications

Résultats acquis avant clôture Git :

- compilation Python des quatre modules/scripts modifiés : `OK` ;
- reconstruction du manifest V2 : `OK`, 192 cas BGIG, deux sources ;
- vérification locale de THPACK9 par le téléchargeur : `OK` ;
- vérification locale de Q4RealBPP, archive et quatre membres : `OK` ;
- tests ciblés L07B après fermeture réelle du holdout : `12/12`, `OK`,
  26,780 s ;
- holdout implicitement inaccessible puis ouvert avec une sélection synthétique
  valide dans les tests : `OK` ;
- reconstruction fixture depuis un chemin temporaire Windows : `OK`.

Vérifications de clôture :

- compatibilité du corpus L06 : `9/9`, `OK`, 15,840 s ;
- garde documentaire : `2/2`, `OK` ;
- alignement produit Fusion-only : `6/6`, `OK` ;
- suite complète : `733/733`, `OK`, 225,722 s ;
- `git diff --check` : `OK`.

Le premier appel de compatibilité, lancé sans `PYTHONPATH`, a échoué avant
d'exécuter un test. Le même contrôle a été relancé une seule fois avec le chemin
`src` canonique et a produit le résultat `9/9` ci-dessus.

La relecture pré-commit a ensuite détecté que la première fixture refusait
l'accès par l'API mais publiait encore les recettes déterministes du holdout.
Cette fixture n'a pas été intégrée. Elle a été remplacée par le reçu public et
le sidecar privé décrits ci-dessus, sans consulter aucun cas ni réponse.

## 9. Limites et frontières

- Aucun moteur externe n'est encore installé, adapté, exécuté ou classé.
- Les cas publics sont des contrôles de méthode, pas une preuve de qualité
  produit.
- Le corpus reste exclusivement T0/T1 ; aucune forme T2 à T4 n'est introduite.
- Le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.
- Aucun budget, deadline, certificat, schéma projet, tolérance, géométrie,
  finalisation, CAD, scène, manifest Fusion ou valeur physique ne change.
- Le résultat ne vaut ni observation Fusion ni validation d'impression.

## 10. Suite

P64-L07C peut acquérir les artefacts candidats dans des environnements isolés,
verrouiller leurs SHA-256, adapter au moins trois moteurs réellement distincts
et recertifier toutes leurs sorties avec BGIG. Les petits contrôles et les
régressions passent avant toute campagne ouverte ; le holdout reste fermé.
