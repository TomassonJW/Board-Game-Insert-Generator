# ADR-0081 — tournoi de solveurs externes libres et portefeuille mesuré

## Statut

Accepté.

## Date

2026-07-23

## Carte liée

- `P64-L07A à P64-L07E — recherche, benchmark et intégration de solveurs externes`

## Contexte

P64-L06 a construit une chaîne de mesure reproductible, mais n'a pas comparé
BGIG aux meilleurs solveurs disponibles. Il a opposé le solveur courant à un
petit oracle exact interne, puis testé trois variantes mineures de ses propres
lanes. Sa décision négative est valable dans cette portée étroite, mais elle ne
répond pas à la question produit : quelle solution accessible et libre
d'utilisation donne aujourd'hui les meilleurs résultats sur les problèmes
rectangulaires réels de BGIG ?

Le holdout L06 est consommé. Il ne peut pas servir à choisir ou régler un
candidat dans une nouvelle campagne.

Des solutions crédibles existent dans plusieurs familles : solveurs spécialisés
de placement 3D, recherche exacte ou hybride, programmation par contraintes et
programmation linéaire en nombres entiers. Leur valeur pour BGIG ne peut pas être
déduite de leur réputation : il faut mesurer leur couverture, recertifier leurs
sorties et vérifier leur licence, leur maintenance, leur coût d'intégration et
leur fonctionnement hors ligne sous Windows et Fusion 360.

Thomas décide explicitement d'ouvrir ce travail et autorise l'intégration du
meilleur candidat, ou de plusieurs candidats complémentaires si la preuve
montre qu'un portefeuille est réellement supérieur.

## Options

### Option A — conserver uniquement les solveurs internes

- Principe : améliorer progressivement les lanes BGIG sans comparaison externe.
- Avantages : aucune nouvelle dépendance et packaging simple.
- Inconvénients : risque élevé de réinventer moins bien des méthodes éprouvées.
- Risques : optimisation locale sans connaître l'écart avec l'état de l'art.
- Coût de maintenance : faible à court terme, potentiellement élevé à long terme.
- Compatibilité MVP : directe.
- Facilité de test : élevée, mais réponse produit incomplète.

### Option B — intégrer immédiatement un outil connu

- Principe : choisir un nom réputé et adapter BGIG autour de lui.
- Avantages : démarrage rapide.
- Inconvénients : choix fondé sur la notoriété, pas sur les cas BGIG.
- Risques : mauvais modèle, licence inadaptée, dépendance lourde ou régression.
- Coût de maintenance : inconnu avant l'intégration.
- Compatibilité MVP : non démontrée.
- Facilité de test : moyenne.

### Option C — auditer, comparer puis intégrer un portefeuille mesuré

- Principe : présélection large, au moins trois concurrents externes réellement
  distincts, tournoi sur corpus public et BGIG, puis intégration conditionnelle.
- Avantages : décision vérifiable, choix réversible et couverture mesurée.
- Inconvénients : travail initial plus important.
- Risques : adaptation des modèles, packaging natif ou résultats sans gagnant.
- Coût de maintenance : mesuré avant décision finale.
- Compatibilité MVP : conservée par les adapters et le certificat BGIG.
- Facilité de test : élevée après normalisation commune.

## Décision

L'option C est retenue.

P64-L07 doit respecter les règles suivantes :

1. inventorier au moins huit candidats crédibles depuis leurs dépôts officiels,
   leur documentation officielle et les publications primaires utiles ;
2. enregistrer pour chacun la version, la source, la licence, l'activité du
   projet, la famille algorithmique, les plateformes, les dépendances, la taille
   et l'adéquation aux contraintes BGIG ;
3. comparer au minimum trois solveurs ou bibliothèques externes qui passent le
   filtre légal et technique et représentent des approches réellement
   distinctes ; le solveur BGIG et l'oracle interne ne comptent pas dans ces
   trois concurrents ;
4. utiliser à la fois des jeux de cas publics pertinents et un corpus BGIG V2,
   avec des données distribuables ou des instructions de téléchargement
   vérifiées ;
5. créer de nouveaux splits `regression`, `discovery`, `tuning` et `holdout` ;
   le holdout L06 reste archivé et interdit pour toute sélection ;
6. appliquer la même entrée normalisée, les mêmes limites de ressources et le
   même validateur BGIG à chaque candidat ;
7. choisir le candidat ou le portefeuille avant d'ouvrir une seule fois le
   nouveau holdout ;
8. intégrer un gagnant principal et jusqu'à deux gagnants complémentaires
   seulement si chacun gagne une famille de cas identifiée et si le portefeuille
   bat objectivement le meilleur candidat seul sous une enveloppe totale
   comparable ;
9. conserver un seul gagnant si les deux autres ne fournissent pas de gain
   distinct ; « prendre les trois premiers » n'est pas une règle acceptable ;
10. produire une décision négative honnête si aucun candidat ne passe les gates,
    sans présenter P64-L07 comme un benchmark réussi.

La liste de départ inclut notamment PackingSolver, LAFF/
`3d-bin-container-packing`, OR-Tools CP-SAT, SCIP et HiGHS. Cette liste amorce la
recherche ; elle ne présélectionne aucun gagnant et doit être élargie.

Une solution externe n'est jamais crue sur parole. Tout placement positif est
converti vers le contrat BGIG et repasse par le certificat commun. Une preuve
d'impossibilité n'est acceptée que dans la portée exacte réellement modélisée.
Une expiration ou une limite de mémoire reste `bounded_unknown`.

Les expérimentations sont isolées dans le workspace. Aucune installation
globale, aucun service distant et aucune télémétrie ne sont autorisés. Une
dépendance produit doit fonctionner hors ligne, être verrouillée à une version
et une empreinte, autoriser l'usage commercial, la modification et la
redistribution nécessaires, et inclure ses avis de licence. Une licence
incertaine, une obligation de redistribution non tranchée ou un composant
propriétaire place le candidat hors intégration jusqu'à une décision humaine
distincte.

Le `/goal` lancé par Thomas dans la tâche de reprise vaut GO d'exécution pour
P64-L07A à P64-L07E, y compris l'acquisition isolée des candidats conformes,
leurs benchmarks et l'intégration d'un à trois gagnants conformes. Aucun second
GO n'est demandé pour une étape déjà couverte par cette ADR et le runbook.

Cette décision amende ADR-0068 : la priorité reste un portefeuille honnête et
certifié, mais les dépendances externes ne sont plus exclues par principe. Elle
ne modifie pas ADR-0079 : la vérité fonctionnelle reste prioritaire sur la
vitesse.

## Conséquences

### Positives

- BGIG sera comparé à des solutions éprouvées au lieu de se comparer seulement
  à lui-même.
- La licence, le coût de packaging et la maintenance deviennent des critères de
  choix mesurés.
- Un portefeuille complémentaire est possible sans être imposé.
- Le validateur BGIG reste l'autorité de vérité.

### Négatives

- Le benchmark demande plusieurs adapters et environnements isolés.
- Certains candidats performants pourront être refusés pour incompatibilité de
  licence, de plateforme ou de distribution.
- Le meilleur résultat académique peut ne pas être le meilleur choix produit.

### Risques

- Biais de corpus : nouveau holdout, cas publics et familles BGIG séparées.
- Budget injuste : enveloppe totale comparable et mesure CPU, mémoire et temps.
- Sortie invalide : recertification systématique et échec fermé.
- Dépendance fragile : version, empreinte, licence, source et plan de retrait
  consignés avant intégration.
- Coût de calcul inutile : filtres légaux et techniques avant compilation, puis
  tournoi progressif avec arrêts précoces.

## Alternatives refusées

- Continuer seulement les variantes internes : ne répond pas à la demande de
  comparer le meilleur accessible.
- Choisir un outil sur sa réputation : aucune preuve sur les contraintes BGIG.
- Intégrer automatiquement les trois meilleurs scores : gaspille ressources et
  maintenance si leurs gains se recouvrent.
- Utiliser un service en ligne : incompatible avec le produit local, la
  confidentialité et la reproductibilité.

## Suivi

- Exécuter `P64-L07A` à `P64-L07E` selon
  `docs/P64_L07_AUTONOMOUS_GOAL_RUNBOOK.md`.
- Produire une fiche d'audit de chaque candidat et un rapport de tournoi
  reproductible.
- Ajouter une ADR de dépendance précise pour chaque gagnant intégré dans L07E ;
  elle documente le fait mesuré sans demander un nouveau GO si toutes les gates
  de cette ADR sont satisfaites.
- Conserver `fusion-validated: false` et `print-validated: false` sans preuves
  correspondantes.
