# P64-L09U-R8-F — preuve de fidélité de bout en bout

Date : 2026-07-29.

Statut : `done-automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## But

R8-F ferme la dernière divergence automatisée entre ce que le produit affiche
et ce que le BRep doit retirer. L’aperçu, le certificat, la CAD IR, le plan
Fusion et l’outil BRep projettent désormais les mêmes opérations négatives
issues de `bgig.flat_inset_subtraction_plan.v1`.

## Écart trouvé et fermé

Après R8-E, l’aperçu final continuait à redessiner les réservations amont. Ces
réservations étaient cohérentes dans les cas simples, mais elles restaient une
seconde source de vérité distincte des opérations réellement exécutées.

`partition_result_view.py` :

- reconstruit et valide le plan soustractif depuis les conteneurs finalisés ;
- refuse un digest, un certificat ou une opération divergente ;
- publie `flat_inset_subtractions` comme projection exacte des opérations ;
- conserve `top_inset_reservations` seulement comme alias de présentation
  historique ;
- ignore le miroir `placement.top_inset_cuts` pour toute décision.

La palette préfère `flat_inset_subtractions` lorsqu’il existe. En coupe X/Z,
chaque rectangle affiché utilise exactement :

```text
z depuis le haut = hauteur de boîte - intervalle.top
hauteur affichée = intervalle.top - intervalle.bottom
```

Le texte visible précise qu’un plateau ou livret creuse les conteneurs
finalisés sans créer matière, union ou nouveau corps.

## Régression produit `2/4/6 mm`

Un cas automatisé partiellement recouvert force :

- livret seul : `2 mm` ;
- plateau seul : `4 mm` ;
- recouvrement : `6 mm`.

Pour chaque opération, le test compare :

```text
plan soustractif
= aperçu final
= paramètres CAD IR
= plan Fusion
= intervalle déclaré de l’outil BRep
```

Une mutation du miroir de compatibilité ne change pas l’aperçu. Une mutation du
plan canonique est refusée.

## Replays personnels strictement en lecture seule

Un seul replay fonctionnel borné a été exécuté pour chacun des deux projets.
Les sources ont été lues directement, mais toutes les sorties ont vécu dans
`<worktree>/.codex-work`.

| Projet | SHA-256 avant | SHA-256 après | Inchangé |
|---|---|---|---|
| `CasLimite02+` | `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` | identique | oui |
| `CasLimite02++` | `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743` | identique | oui |

Aucun témoin persistant exact n’était compatible avec les dépendances
courantes. Aucun cache n’a donc été revendiqué.

Le runtime SCIP natif de Fusion n’est pas configuré dans le Python local.
Malgré cela, le replay fonctionnel Normal courant a trouvé un plan certifié
pour les deux cas :

| Projet | Calcul local | Finalisation | Opérations plates |
|---|---:|---:|---:|
| `CasLimite02+` | `16 775,800 ms` | `1 718,899 ms` | `20` |
| `CasLimite02++` | `14 846,677 ms` | `2 398,427 ms` | `23` |

Ces temps sont des observations de validation uniques, pas un benchmark ni une
preuve de performance. Ils ne remplacent pas les temps humains autoritaires de
0.1.78 : `22,823 s`, `61,799 s`, `90,991 s` et `87,192 s`.

Pour chaque projet :

- le certificat minimal conserve les réservations `printable=false` ;
- volume, corps, union, opération et compensation Z positifs valent zéro ;
- la finalisation sélectionne un plan matérialisable ;
- le certificat d’ancrage des cavités est positif ;
- l’aperçu, la CAD IR, Fusion et le BRep portent le même nombre d’opérations ;
- tous leurs identifiants et intervalles sont identiques ;
- le certificat Fusion est égal au certificat du cœur ;
- toutes les coordonnées restent sur la grille `0,1 mm` ;
- le digest positif reste inchangé.

Résultats exacts :

- `CasLimite02+` : `20 = 20 = 20 = 20` opérations, profondeurs locales
  observées `4/6 mm` ;
- `CasLimite02++` : `23 = 23 = 23 = 23` opérations, profondeurs locales
  observées `2/4/6 mm`.

## Préservations

- Cavités calibrées et poses monde : inchangées.
- Continuité et accès verticaux : recertifiés avant matérialisation.
- Fonds, parois minimales et fragments de matière : recertifiés.
- Ordre automatique petit-dessous/grand-dessus : inchangé.
- Grille produit `0,1 mm` et epsilon numérique : distincts.
- BRep transitoire, BaseFeature unique et rollback : inchangés.
- Projets personnels : jamais sauvegardés, normalisés en place ou versionnés.
- Aucun benchmark, holdout, corpus, tournoi solveur ou contrôle manuel ajouté.

## Vérifications automatisées

Lot ciblé R8-F :

- fidélité `2/4/6` et cavités locales ;
- plan soustractif pur ;
- finalisation composite ;
- réservations, parois et ordre ;
- aperçu et explications ;
- CAD IR ;
- squelette Fusion ;
- BRep et rollback ;
- calcul par étapes et gates correctives ;
- palette, transport projet et synchronisation CAD.

Résultat : `302/302` tests en `32,905 s`.

Tests de pilotage documentaire : `11/11`.

Compilation Python ciblée et `git diff --check` : `OK`.

## Limite et suite

R8-F prouve la cohérence automatisée et les deux replays locaux. Elle ne
transforme pas cette preuve en observation humaine Fusion :
`fusion-validated=false`, `print-validated=false`.

R8-G doit exécuter la suite autorisée complète, construire la nouvelle
candidate, l’intégrer, l’installer automatiquement puis ouvrir une seule
nouvelle recette humaine.
