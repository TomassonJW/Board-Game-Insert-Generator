# P64-L09U-R2-V — recette Fusion 0.1.73

## But

Vérifier dans Fusion réel que le calcul, l'aperçu et la matérialisation
représentent le même plan, sans Combine perdu ni cavité modifiée.

Ne valide pas l'impression : `print-validated=false`.

## Préparation déjà faite par Codex

- package 0.1.73 installé ;
- projet de démarrage forcé à vierge et non enregistré ;
- fixture publique et reçus copiés ;
- marqueur du commit installé vérifié ;
- projets personnels laissés inchangés.

Tu n'as aucune commande PowerShell à lancer.

## Recette

### 1. Redémarrage propre

1. Ferme complètement Fusion.
2. Rouvre Fusion et recharge BGIG.
3. Vérifie que BGIG affiche la version 0.1.73.
4. Vérifie que le projet BGIG est vierge et non enregistré.

Tout ancien projet rouvert automatiquement vaut KO.

### 2. CasLimite01+ avec plateau

1. Ouvre explicitement `CasLimite01+.bgig.json`.
2. Lance `Calculer` en effort Normal et note le temps.
3. Compare l'aperçu minimal au projet, puis matérialise le plan minimal.
4. Note le temps de matérialisation et la réactivité de Fusion.
5. Lance `Finaliser`, note le temps et garde l'aperçu final visible.
6. Matérialise le plan final et note le temps.
7. Vérifie :
   - aucune erreur `ALL_TOOL_BODY_REFERENCE_LOST` ;
   - aucune feature Combine rectangulaire cassée ;
   - aucune scène BGIG partielle ;
   - mêmes conteneurs et mêmes positions que dans l'aperçu ;
   - cavités aux mêmes positions et dimensions ;
   - plateau encastré à la pose affichée ;
   - jeux externes visibles, sans trou résiduel imprimable.

### 3. CasLimite01+ sans plateau

1. Sans enregistrer le fichier source, retire le plateau dans BGIG.
2. Relance `Calculer`, puis `Finaliser`.
3. Vérifie que la finalisation publie un plan final au lieu de s'arrêter sur
   `xy_composite_residual_owner_not_found`.
4. Matérialise et vérifie la fidélité à l'aperçu.
5. Ferme ce projet sans enregistrer la modification.

### 4. CasLimite02+

1. Ouvre explicitement `CasLimite02+.bgig.json`.
2. Lance `Calculer`, matérialise le minimum et note le temps.
3. Lance `Finaliser`, matérialise le final et note les deux temps.
4. Vérifie la disposition, les deux réservations supérieures, les profondeurs
   de cavité, les jeux externes et l'absence de scène partielle.

### 5. CasLimite01++

1. Ouvre explicitement `CasLimite01++.bgig.json`.
2. Lance `Calculer` en effort Normal.
3. Vérifie qu'un plan minimal est trouvé.
4. Lance `Finaliser` et vérifie qu'un plan final à résiduel nul est publié.
5. Matérialise le plan final et note le temps.
6. Ne sauvegarde aucune modification du fichier personnel.

### 6. Second démarrage

1. Ferme complètement Fusion.
2. Rouvre Fusion et recharge BGIG.
3. Vérifie un nouveau projet vierge.
4. Ouvre un cas explicitement et lance `Calculer`.
5. Vérifie qu'il s'agit d'un vrai calcul, pas d'une restitution instantanée
   intersession.

## Verdict attendu

Envoie :

- `P64-L09U-R2-V Fusion OK 0.1.73` si tout passe ;
- sinon `P64-L09U-R2-V Fusion KO 0.1.73`, l'étape exacte, le message complet,
  les temps observés et une capture.

Un résultat géométrique différent de l'aperçu, une cavité déplacée ou
redimensionnée, un Combine perdu, une scène partielle ou une réactivité que tu
juges inexploitable vaut KO.

Avant ton verdict : `fusion-validated=false`, `print-validated=false`.
