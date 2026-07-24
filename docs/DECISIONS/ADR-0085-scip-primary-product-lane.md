# ADR-0085 — SCIP comme moteur produit 3D prioritaire et recertifié

## Statut

Acceptée le 2026-07-24 dans P64-L08K, après les gates L08I et L08J et sous le
GO autonome explicite de Thomas pour aller jusqu'au test humain Fusion.

## Contexte

P64-L08F a retenu SCIP 10.0.2 avec 18 gains et aucune perte face au comportement
BGIG corrigé sur le vrai benchmark 3D. Le portefeuille externe a été rejeté car
il perdait trois vérités face à SCIP seul. L08J a ensuite produit un runtime
minimal `cp314`, redistribuable et équivalent sur les contrôles publics.

Le produit doit maintenant utiliser ce gagnant sans réintroduire le faux solveur
2D HiGHS, sans modifier les règles BGIG et sans transformer un résultat natif en
autorité. Fusion embarque CPython `cp314`, mais aucun exécutable Python produit
séparé n'a été audité pour cette mission.

## Décision

SCIP devient la première lane du calcul global explicite lorsque le runtime est
configuré et que la traduction produit est fidèle. Un plan SCIP certifié arrête
la recherche : le portefeuille interne n'est pas exécuté en parallèle, puisque
le tournoi a refusé ce portefeuille face à SCIP seul.

Le runtime qualifié est versionné sous forme d'une archive déterministe dans le
paquet Fusion 0.1.61. L'installateur vérifie son SHA-256, l'extrait localement et contrôle le
nombre et la taille totale des fichiers. L'adaptateur vérifie ensuite l'arbre complet
et son digest avant tout chargement natif. PySCIPOpt est
chargé dans le CPython `cp314` de Fusion, sans service, compte, secret,
télémétrie, réseau ou installation globale. Un conflit avec un NumPy déjà chargé
depuis une autre origine ferme la lane et conserve le fallback interne.

Le modèle exécuté est l'exact worker SCIP scellé du tournoi. Les deux fichiers du
worker sont copiés et verrouillés par empreinte. Le produit adapte seulement ses
entrées :

- échelle entière de 1 000 unités par millimètre ;
- refus si une dimension n'est pas représentable exactement à cette échelle ;
- jeu de boîte retiré de l'espace utile ;
- jeux X/Y/Z entre corps intégrés par gonflement positif des enveloppes ;
- variantes locales certifiées et rotations X/Y transportées explicitement ;
- affectation des éléments aux conteneurs conservée comme décision BGIG amont ;
- appui complet exigé par le MIP, puis appuis et ratio recalculés par BGIG ;
- recertification finale par `certify_minimal_free_3d_plan` obligatoire.

Les réservations supérieures localisées de l'actuel contrat produit ne sont pas
silencieusement approximées. Un projet qui en contient est déclaré
`unsupported` par la lane SCIP et reprend immédiatement le solveur interne.
L'impossibilité du modèle SCIP produit n'est jamais promue en impossibilité BGIG,
car son appui complet est volontairement plus strict que le minimum interne.

Budgets natifs monotones :

| Effort | Temps SCIP | Mémoire | Threads |
| --- | ---: | ---: | ---: |
| Rapide | 1 s | 1 024 Mio | 1 |
| Normal | 5 s | 1 024 Mio | 1 |
| Approfondi | 30 s | 1 024 Mio | 1 |

Une solution recertifiée est publiée immédiatement. Un runtime absent, invalide,
non compatible, une règle non représentable, une erreur native ou un certificat
refusé déclenchent le fallback interne. Une expiration SCIP reste
`no_solution_within_budget` et ne double pas silencieusement le budget avec une
seconde recherche globale. Une annulation reste `stale_or_cancelled`.

## Conséquences

- le cœur Python reste indépendant de Fusion ; seul l'adaptateur configure le
  chemin du runtime installé ;
- HiGHS reste quarantiné hors Auto ;
- aucune dimension, tolérance, variante, certificat, géométrie, finalisation,
  CAD, scène, manifest métier ou valeur physique ne change ;
- aucun replay du holdout et aucun tuning post-holdout n'est effectué ;
- le paquet natif augmente la taille de l'add-in, mais reste environ trois fois
  plus petit non compressé que le candidat PyPI refusé en L08H ;
- le contrôle public réel 18 conteneurs / 20 éléments reste `bounded_unknown`
  aux budgets Normal et Approfondi : l'intégration est valide, mais aucun gain de
  solution n'est revendiqué sur ce cas ;
- `fusion-validated=false` et `print-validated=false` jusqu'au retour humain
  formel sur le paquet 0.1.61.

## Alternatives refusées

- **Continuer avec HiGHS** : ce moteur ne résout que le sol rectangulaire et ne
  satisfait pas la gate 3D réelle.
- **Lancer SCIP et toutes les lanes internes** : le benchmark a rejeté ce
  portefeuille et ce choix rallongerait le calcul sans preuve de gain.
- **Faire confiance au plan SCIP** : interdit ; BGIG reste l'autorité de
  certificat.
- **Approximer les top insets** : risque de faux positif ou faux négatif ; le
  fallback exact est préférable.
- **Ajouter un second interpréteur Python** : il agrandirait et élargirait le
  paquet sans audit produit préalable ; CPython `cp314` Fusion est la cible déjà
  qualifiée.
