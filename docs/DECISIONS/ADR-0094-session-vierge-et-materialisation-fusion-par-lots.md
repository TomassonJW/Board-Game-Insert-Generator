# ADR-0094 — Session vierge et matérialisation Fusion par lots

## Statut

Acceptée par la demande corrective de Thomas le 2026-07-27.

Cette décision prépare une nouvelle gate Fusion. Elle ne vaut ni validation
Fusion, ni validation d'impression.

## Contexte

La gate humaine de 0.1.70 confirme que le calcul, la finalisation et l'aperçu
peuvent réussir sur `CasLimite01+` et `CasLimite02+`. Deux défauts empêchent
cependant la validation :

- la matérialisation finale construit plusieurs centaines de features
  paramétriques et immobilise Fusion pendant environ douze à quinze minutes ;
- le redémarrage restaure automatiquement le projet précédent et peut
  réinjecter un témoin certifié intersession, ce qui contredit le recalcul
  explicite complet décidé par ADR-0093.

Le témoin persistant masquait en plus une condition circulaire : la voie dense
de piles au sol attendait une réservation supérieure déjà posée, alors que la
pose devait être calculée conjointement.

## Options

### Option A — Conserver la persistance et ajouter un bouton de purge

Cette option laisse le comportement par défaut ambigu et oblige Thomas à
nettoyer manuellement l'état avant chaque preuve.

### Option B — Remplacer Fusion par un autre moteur ou supprimer la chronologie

Cette option élargit fortement l'architecture et ne traite pas la cause
immédiate : le nombre de features créées par l'adaptateur courant.

### Option C — Session vierge, recalcul frais et booléens Fusion groupés

Cette option conserve le cœur, le CAD IR et les certificats. Elle change
seulement la politique de session produit et l'exécution physique des
opérations rectangulaires dans Fusion.

## Décision

Retenir l'option C.

### 1. Une session Fusion commence toujours vierge

Au chargement de la palette :

- BGIG fournit un projet neuf non enregistré ;
- `current_path` est vide ;
- aucun fichier de récupération historique n'est lu ;
- la liste des fichiers récents reste disponible ;
- un fichier nommé n'est ouvert que par une action explicite.

Les fichiers historiques restent sur disque et ne sont ni modifiés ni
supprimés automatiquement.

### 2. Aucun témoin certifié n'est réutilisé entre deux sessions

Le chemin produit :

- ne lit plus de témoin certifié intersession ;
- n'en écrit plus ;
- passe toujours `initial_incumbent=None` au calcul explicite ;
- rapporte cette politique comme `disabled`.

Le cache exact de la session reste un mécanisme interne borné, consulté
uniquement à la suite d'une action explicite. Il ne traverse pas un redémarrage
de Fusion.

### 3. La voie dense résout sa réservation avant certification

Pour douze corps ou plus, lorsque la partition entièrement au sol échoue :

- la voie déterministe de piles au sol reste admissible même si le problème de
  base n'expose pas encore de zone supérieure résolue ;
- elle reçoit la pose automatique déterministe issue du plan de réservation ;
- elle construit les piles sous cette zone ;
- le certificat commun valide ensuite la réservation, les parois, les
  cavités et la priorité plancher d'abord ;
- le premier candidat certifié est accepté, car la liste de cette voie est
  déjà classée lexicographiquement plancher d'abord.

Les autres voies restent disponibles pour les projets où une autre pose
automatique est nécessaire. Aucune cavité n'est déplacée.

### 4. Le CAD IR logique reste l'autorité

Chaque prisme d'annexe et chaque coupe rectangulaire reste présent dans le CAD
IR, dans les digests, les mesures et les certificats.

Le groupement Fusion ne fusionne pas les identités logiques et ne change ni
les dimensions, ni l'ordre sémantique :

1. toutes les unions du corps ;
2. toutes les coupes rectangulaires du corps ;
3. les autres features spécialisées déjà ordonnées.

### 5. Fusion exécute un lot booléen par corps et par phase

Pour chaque corps propriétaire :

- les boîtes outils sont construites comme BRep transitoires ;
- elles sont persistées dans une BaseFeature unique pour la phase ;
- un seul Combine `Join` applique les annexes ;
- un seul Combine `Cut` applique les coupes rectangulaires ;
- les outils ne sont pas conservés comme corps utilisateur.

Le nombre de features principales devient donc proportionnel au nombre de
corps, tout en préservant le nombre d'opérations logiques.

### 6. La performance reste une preuve humaine

Les tests hors Fusion certifient :

- le groupement complet et sans perte ;
- les coordonnées et profondeurs ;
- l'ordre unions puis coupes ;
- les comptes logiques et les comptes de lots.

Seule la gate humaine peut confirmer :

- le temps réellement observé ;
- la réactivité de Fusion ;
- la géométrie visible ;
- la synchronisation de scène.

## Conséquences

- 0.1.70 reste `human-KO` et `do-not-run`.
- 0.1.71 devient le premier candidat correctif.
- La récupération automatique de brouillons est temporairement supprimée du
  parcours produit.
- Les fichiers nommés et récents restent disponibles.
- Les témoins historiques restent lisibles par les outils de diagnostic, mais
  sont hors du chemin produit.
- La chronologie Fusion devient beaucoup plus compacte.
- `fusion-validated=false` et `print-validated=false` jusqu'à la gate humaine.

## Alternatives refusées

- Faire attendre Thomas quinze minutes.
- Masquer le message « ne répond pas » sans réduire les opérations.
- Réactiver un témoin intersession sous un autre nom.
- Supprimer les fichiers personnels historiques.
- Déplacer une cavité pour libérer la réservation supérieure.
- Aplatir les opérations logiques du CAD IR en une géométrie non certifiable.
