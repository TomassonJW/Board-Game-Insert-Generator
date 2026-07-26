# P64-L09S-V 0.1.67 - preuve humaine KO

## 1. Statut

- Date : 2026-07-26.
- Package observe : `0.1.67`.
- Verdict : `human-KO`, `do-not-run`, non accepte.
- Successeur correctif : `0.1.68`.
- Fusion : aucune nouvelle validation acquise.
- Impression : `print-validated=false`.

## 2. Faits observes

`CasLimite01` calcule sans plateau dans le journal de reference, mais ne trouve plus de solution des qu un plateau, puis plusieurs, sont ajoutes, y compris avec les efforts Normal, Long et Approfondi.

`CasLimite02` trouve un plan minimal avec deux plateaux, mais la finalisation ne publie aucun plan final. Thomas signale aussi des enveloppes d elements visuellement rabotees dans certains cas retournes ou contraints.

Ces deux echecs invalident la gate complete, meme si les cas simples restent fonctionnels.

## 3. Diagnostic CasLimite01

Le succes historique sans plateau utilise la lane produit `external_scip_real_3d`. SCIP reste donc necessaire pour cette forte cardinalite. Le chemin plateau imposait trop tot les reservations hautes au solveur complexe et pouvait epuiser son budget avant de retrouver le placement minimal deja faisable sans plateau.

La correction `0.1.68` projette d abord le probleme sans les reservations plateau/livret, autorise un unique appel SCIP si le runtime est configure, puis recertifie obligatoirement chaque candidat contre les vrais prismes reserves. Aucun second appel SCIP n est lance pour cette recertification. Un conflit avec une reservation produit un rejet ferme, jamais une croissance de support ni un faux succes.

Le CPython 3.10 local ne dispose pas du runtime SCIP produit. Le rejeu exact de `CasLimite01` reste donc une obligation de la gate Fusion, ou SCIP est installe et verifie.

## 4. Diagnostic CasLimite02

Le plan minimal selectionne n est pas toujours le meilleur point de depart pour couvrir exactement tout le volume imprimable. La correction conserve donc un pool borne de douze plans minimaux deja certifies et les essaie sous une seule date limite de finition.

Le second defaut etait un rejet de certificat : quand la palette ne transmettait pas explicitement les variantes internes, le finaliseur reconstruisait un probleme generique et rejetait certains corps composites pourtant valides, notamment avec axe fixe. `0.1.68` reconstruit maintenant les frontieres certifiees avant toute fermeture.

Le rejeu prive exact de `CasLimite02` obtient un calcul certifie, puis une finalisation certifiee au deuxieme candidat, avec residuel imprimable nul et certificat de materialisation composite valide.

## 5. Protection des minima

La correction ne modifie aucune tolerance ni valeur physique. Pour chaque proprietaire final, l union du coeur et de ses annexes doit contenir l enveloppe minimale source. Chaque dimension finale reste superieure ou egale au minimum, et tout axe fixe conserve exactement sa dimension minimale. Le conteneur `c2` de `CasLimite02` conserve notamment son axe X fixe.

Tout rabotage, toute croissance artificielle pour soutenir un plateau ou toute perte de volume minimal vaut rejet du plan et `human-KO` immediat.

## 6. Validation automatisee exigee

- projection plateau avec un unique appel SCIP simule, suivie de la recertification des reservations ;
- pool de candidats borne et date limite partagee ;
- reconstruction des variantes internes en finalisation ;
- fermeture complete avec `printable_residual_volume_mm3=0` ;
- union composite contenant chaque enveloppe minimale et respect des axes fixes ;
- contrat de timeout historique preserve ;
- aucun benchmark, holdout ou corpus execute.

## 7. Gate successeur

La seule gate courante est `P64-L09S-V` sur le package `0.1.68`. Elle doit rejouer `CasLimite01` avec un puis plusieurs plateaux et `CasLimite02` avec ses deux plateaux, jusqu a la materialisation reelle. Aucune acceptation partielle n est permise.