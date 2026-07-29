# P64-L09U-R9-A — Diagnostic causal de performance

## Verdict

R9-A est `complete`.

Le résultat fonctionnel de la candidate Fusion 0.1.79 reste l'autorité :

- géométrie, ordre et dispositions : `human-positive` ;
- pipeline plat strictement soustractif : `human-positive` ;
- performance : `human-KO` ;
- gate globale : `human-positive-partial` ;
- `fusion-validated=false` ;
- `print-validated=false`.

La régression ne vient ni de la grille de 0,1 mm, ni de l'epsilon interne, ni
de la préparation des variantes, ni de la finalisation, ni de la
matérialisation.

Le coût dominant vient de deux recherches SCIP successives sur un payload
strictement identique, suivies d'un rejet du seul témoin SCIP par le certificat
produit, puis du vrai travail utile dans le repli interne.

## Sources et garde de lecture seule

Les mesures utilisent uniquement :

- `CasLimite02+.bgig.json` ;
- `CasLimite02++.bgig.json` ;
- les fixtures et tests déjà versionnés ;
- le runtime SCIP 10.0.2 / PySCIPOpt 6.2.1 déjà livré par BGIG.

Le runtime natif a été exécuté avec le paquet CPython 3.14.0 épinglé par le
lockfile du dépôt :

- taille : `14 839 285` octets ;
- SHA-256 :
  `620FB3527428FB354F093B0B8B634DFB8E3023115DF68608FBA7E91DB69B4F4D`.

Aucune dépendance globale n'a été installée.

Les SHA personnels ont été contrôlés avant et après chaque replay :

| Projet | SHA-256 avant | SHA-256 après |
|---|---|---|
| `CasLimite02+` | `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` | identique |
| `CasLimite02++` | `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743` | identique |

## Payload de recherche

Les quatre préparations suivantes produisent exactement le même payload
SCIP :

1. `CasLimite02+` avec éléments plats ;
2. `CasLimite02+` sans éléments plats ;
3. `CasLimite02++` avec éléments plats ;
4. `CasLimite02++` sans éléments plats.

Preuve :

- digest problème :
  `77182c190d700132a8b200a57d467c16b0530175fcbc16216429e157900bc183` ;
- 8 participants ;
- 12 variantes brutes ;
- 12 variantes uniques ;
- 24 choix orientés ;
- 0 zone plate active dans le modèle SCIP ;
- contraintes actives identiques :
  `xyz`, `stacking`, `support`, `p45_variant_front`, `rotations`.

Il n'existe donc aucune redondance de variantes à éliminer dans ce payload.
La duplication est au niveau de l'appel solveur lui-même.

## Reproduction du KO Normal

Le replay natif de `CasLimite02+` en Normal reproduit l'observation Fusion :

| Mesure | Fusion 0.1.78/0.1.79 | Replay R9-A |
|---|---:|---:|
| calcul total | 22,823 s | 23,408 s |
| statut | sans solution | sans solution |

Chronologie mesurée :

1. analyse locale, préparation et synchronisation : moins de 0,1 s ;
2. projection sans éléments plats :
   - limite demandée : 4,996 s ;
   - durée native réelle : 11,598 s ;
   - aucune solution ;
3. calcul complet :
   - limite restante demandée : 8,355 s ;
   - durée native réelle : 11,760 s ;
   - aucune solution.

Chaque appel construit le même modèle :

- 483 variables initiales ;
- 1 212 contraintes initiales ;
- 278 variables transformées ;
- 434 contraintes transformées ;
- 1 nœud ;
- 17 LP ;
- aucun incumbent.

Le timeout est observé tardivement dans le travail racine/presolve. Il ne
constitue pas une preuve d'impossibilité.

## Reproduction du succès Approfondi

Le replay natif de `CasLimite02++` en Approfondi maximal produit :

- calcul total : 92,968 s ;
- solution certifiée ;
- SHA personnel inchangé.

Chronologie :

1. première recherche SCIP identique : 12,115 s, sans solution ;
2. seconde recherche SCIP : 56,031 s, une solution native ;
3. certification commune du témoin SCIP : rejet
   `MINIMAL_ENVELOPE_EXPANDED` ;
4. repli interne complet : 24,132 s ;
5. résultat final : solution interne certifiée.

Le modèle SCIP de la seconde recherche reste au nœud racine :

- 483 variables et 1 212 contraintes initiales ;
- 278 variables et 451 contraintes transformées ;
- 1 nœud ;
- 19 LP ;
- une solution native après 56 s ;
- solution native non admissible par le produit.

Le témoin SCIP agrandit notamment la dimension fixe de `container:c2`.
L'autorité produit conserve au contraire l'enveloppe minimale. Le temps SCIP
ne produit donc pas le résultat visible validé par Thomas.

## Travail interne utile

Le repli Approfondi sélectionne :

- lane : `historical_legacy_corner` ;
- ordre : `placement_rarity` ;
- propagation : `inward_contact` ;
- digest de placement :
  `a3ef2f440a212ed29496fe50072e065a0c861388e6e55e68c548c2bf8817bc46`.

La première lane suffit à reproduire ce digest :

- recherche beam : environ 2,35 à 2,59 s ;
- 4 286 états ;
- 6 258 essais de pose ;
- 4 562 options admissibles ;
- 12 complétions géométriques ;
- 12 complétions certifiées ;
- candidat retenu : index 10 ;
- durée totale de la lane, certifications et revalidation finale :
  13,363 s.

Les huit lanes suivantes ne produisent aucune complétion. Elles consomment
environ 10 s supplémentaires sans changer le résultat.

## Coût des réservations plates

Sur la première lane seule :

- 13 certifications minimales complètes ;
- 15 résolutions automatiques de poses plates ;
- environ 10,8 s dans les résolutions plates et leur certification ;
- 32 298 appels à `_automatic_layout_rank` dans le profilage ;
- 23,975 s profilées sous `sorted` avec l'instrumentation `cProfile` ;
- 32 326 résolutions de couches verticales ;
- 31 679 contrôles de collision avec les prismes réservés ;
- 32 326 certificats de fragments de matière.

Un cache expérimental exact des rangs, clé par géométrie et limité au run,
conserve le digest autoritaire mais ne réduit la lane que de 13,363 s à
11,852 s. Ce gain est réel mais insuffisant seul.

## Mémoire

Le replay Normal passe d'environ 46,4 Mio à 54,0 Mio de working set, avec un
pic à 71,8 Mio.

Le replay Approfondi termine autour de 80,1 Mio, avec un pic à 82,8 Mio.

Ces mesures ne montrent ni croissance non bornée ni fuite dominante. Le coût
est du calcul répété.

## Variantes comparées

| Option mesurée | Temps calcul | Résultat | Verdict |
|---|---:|---|---|
| voie 0.1.79 complète | 92,968 s local ; 87–91 s Fusion | digest autoritaire `a3ef…bc46` | trop lente |
| projection interne Normal, puis recertification | 4,118 s (`+`) ; 3,902 s (`++`) | digest `3ca1…696a` | rapide mais disposition différente, refusée |
| première lane interne Approfondie complète | 13,363 s | digest autoritaire `a3ef…bc46` | base fonctionnelle retenue |
| première lane + cache exact de rang | 11,852 s | digest autoritaire | gain marginal seul |
| optimisation SCIP seule | non retenue | premier témoin SCIP rejeté | mauvais chemin d'autorité |
| hausse de budget ou de candidats | non mesurée | masquerait le coût | interdite |
| grille ou epsilon modifiés | non mesurée | changerait le modèle physique | interdite |

## Conclusion causale

Le chemin à optimiser est :

1. exécuter d'abord la lane interne qui produit le résultat certifié
   autoritaire ;
2. conserver les bornes existantes ;
3. retenir les meilleurs complétions d'un même front sans augmenter leur
   nombre publié ;
4. arrêter le portfolio quand une lane possède une solution certifiée ayant
   autorité produit ;
5. supprimer les classements et contrôles plats strictement répétés à
   l'intérieur d'un même appel, avec des clés géométriques exactes et locales ;
6. ne lancer SCIP qu'en repli si aucune solution interne certifiée n'existe.

Cette décision est formalisée par ADR-0106.
