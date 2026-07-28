# P64-L09U-R5-V — recette Fusion 0.1.76

Statut : `ready-human-gate`, 0.1.76 installée et vérifiée.

Avant verdict : `fusion-validated=false`, `print-validated=false`.

## Précondition

Codex a installé et vérifié 0.1.76 avec son marqueur de commit. Ferme
complètement Fusion avant le replay.

## Vérification prioritaire

Sur un conteneur dont une cavité d'asset est seulement partiellement recouverte
par un plateau :

1. calcule, finalise puis matérialise le plan final ;
2. vérifie que la partie sous plateau rejoint directement son encastrement ;
3. vérifie que la partie hors plateau est ouverte jusqu'au-dessus de l'asset ;
4. vérifie qu'aucun plafond imprimé ne rend la cavité inaccessible ;
5. vérifie que les parois latérales et les appuis hors cavité sont toujours
   présents ;
6. compare la position, la profondeur et l'empreinte avec l'aperçu.

KO si la cavité reste presque fermée hors plateau, si une paroi disparaît autour
de la cavité ou si sa profondeur change.

## Régressions à conserver

Rejoue ensuite les contrôles R4 utiles sur `CasLimite01+`, `CasLimite02+` et
`CasLimite01++` :

- aucune dalle entre plateau et cavité ;
- paliers locaux corrects ;
- cavités sans coupe locale ouvertes ;
- aperçu et scène Fusion identiques ;
- matérialisation progressive, sans Combine rectangulaire ni scène partielle ;
- temps de calcul, finalisation et matérialisation séparés et honnêtes.

## Rapport

Donne :

- `P64-L09U-R5-V Fusion OK 0.1.76` si tout passe ;
- sinon `P64-L09U-R5-V Fusion KO 0.1.76`, avec projet, conteneur, cavité,
  région sous/hors plateau, défaut exact, temps et capture utile.

Même en cas de succès : `print-validated=false`.
