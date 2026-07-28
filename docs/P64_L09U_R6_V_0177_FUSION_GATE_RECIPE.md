# P64-L09U-R6-V — recette Fusion 0.1.77

Statut : `ready-human-gate`, 0.1.77 installée et vérifiée depuis `e81737d`.

Avant verdict : `fusion-validated=false`, `print-validated=false`.

## Précondition

Codex a installé et vérifié 0.1.77 avec le marqueur `e81737d`. Ferme
complètement Fusion, rouvre-le puis recharge l'add-in BGIG.

Ne modifie et ne sauvegarde aucun projet personnel pendant cette gate.

## Contrôle prioritaire — CasLimite02+

Ouvre `CasLimite02+`, avec :

- plateau principal `110 × 120 × 4 mm`, ordre `0` ;
- livret `60 × 80 × 2 mm`, ordre `1`.

Puis :

1. clique sur `Calculer`, note le temps et exige un résultat ;
2. clique sur `Finaliser`, note le temps et exige un résultat ;
3. vérifie dans l'aperçu que plateau et livret ont chacun leur empreinte ;
4. clique sur `Matérialiser`, note le temps et laisse le rendu se terminer ;
5. contrôle `c4 / Bac cartes quatre`, en particulier la petite cavité de
   `10 mm` partiellement recouverte ;
6. mesure sa profondeur dans la partie hors plateau puis dans la petite partie
   sous plateau.

Résultat attendu :

- la profondeur utile reste `10 mm` dans les deux parties ;
- aucun palier de `6 mm` ne raccourcit la cavité sous plateau ;
- la jonction entre cavité et encastrement local est directe ;
- la partie hors plateau reste ouverte ;
- fonds, parois latérales et appuis restent présents.

KO immédiat si la partie sous plateau retombe à environ `4,4 mm`.

## Contrôle des deux encastrements

Observe séparément :

1. une zone couverte uniquement par le plateau : encastrement `4 mm` ;
2. une zone couverte uniquement par le livret : encastrement `2 mm` depuis le
   sommet local ;
3. une zone d'intersection : plateau inférieur `4 mm`, puis livret supérieur
   `2 mm`, soit `6 mm` au total ;
4. une zone sans élément plat : aucune profondeur ajoutée.

Les empreintes disjointes ne doivent jamais additionner artificiellement leurs
épaisseurs. Deux paliers différents doivent rester visibles lorsque leurs
empreintes diffèrent.

## Régressions à préserver

Rejoue ensuite `CasLimite01+` puis `CasLimite01++` :

- calcul, finalisation et matérialisation aboutissent ;
- aucune dalle ne sépare plateau et cavité ;
- les portions hors plateau restent ouvertes ;
- aperçu et scène Fusion sont cohérents ;
- aucun Combine rectangulaire, aucune scène partielle et aucun
  `ALL_TOOL_BODY_REFERENCE_LOST` ;
- le rendu reste progressif et Fusion reste utilisable.

## Preuves à transmettre

Pour chaque projet, donne :

- temps de calcul ;
- temps de finalisation ;
- temps de matérialisation ;
- capture de l'aperçu ;
- capture de la scène Fusion ;
- pour `c4`, mesure de profondeur sous et hors plateau ;
- pour les deux éléments plats, une vue montrant les paliers `4 mm`, `2 mm` et
  leur intersection `6 mm`.

Verdict attendu :

- `P64-L09U-R6-V Fusion OK 0.1.77` si tout passe ;
- sinon `P64-L09U-R6-V Fusion KO 0.1.77`, avec projet, conteneur, région,
  mesure, temps et capture utiles.

Même en cas de succès : `print-validated=false`.
