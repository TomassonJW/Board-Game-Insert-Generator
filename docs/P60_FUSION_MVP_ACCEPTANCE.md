# P60 - Acceptance du MVP V0.1 Fusion-only 0.1.9

## Statut

prepared, automated-evidence-green, human-fusion-observation-required,
print-validated: false.

## Perimetre accepte

Le produit teste est uniquement l add-in Fusion 360 et sa palette embarquee.
Aucun frontend, serveur localhost, navigateur ou Vite ne participe au parcours.

Le fixture scripts/fusion/p60_mvp_project.json demande :

- Bac jetons avec les cavites Pieces et Cubes, dimension locale X verrouillee
  exactement a 80 mm ;
- Bac cartes avec la cavite Cartes sleevees ;
- Cale pleine avant, corps explicite solid sans cavite ;
- un livret reserve au-dessus ;
- trois corps imprimes demandes au total ;
- aucun corps automatique.

Le chargement doit aussi rendre visibles les presets Jetons, Cartes sleevees,
Des et Pions, puis Bac vide, Bloc plein / cale et Separateur. Les presets sont
des valeurs de depart editables, pas des corps ajoutes automatiquement.

## Preparation automatique

scripts/fusion/prepare_p60_mvp_acceptance.ps1 installe l add-in du commit
courant, package tout le coeur pur, verifie les marqueurs 0.1.9, sauvegarde un
projet courant different dans
Documents/BGIG/projects/bgig_project_v1.before-p60.json, installe le fixture de
gate de facon atomique et enregistre le commit installe.

Le preparateur ne remplace jamais la sauvegarde par le fixture lui-meme lors
d un second lancement idempotent.

Preuves attendues avant ouverture de Fusion :

- partition construite : 3 corps finaux, 1 complement explicite, 0 automatique ;
- Bac jetons final local X = 80 mm ;
- Cale pleine avant finale locale 20 x 238,8 x 63,4 mm et aucune cavite ;
- CAD IR : 3 composants, 3 cavites top-open, digest deterministe ;
- plan Fusion hors API : 3 occurrences compactes, aucune occurrence eclatee ;
- installateur : manifeste 0.1.9 et project_presets.py package.

## Checklist humaine Fusion

1. Ouvrir un nouveau design Fusion compatible Assembly.
2. Arreter puis relancer l add-in, cliquer BGIG - Atelier de rangement dans
   Utilities et confirmer que seule la palette locale s ouvre.
3. Confirmer une ouverture proche de 1280 x 1100, sous reserve du clamp de
   l espace disponible par Fusion.
4. Parcourir les six vues et confirmer dans Pieces les presets Jetons, Cartes
   sleevees, Des et Pions.
5. Dans Bacs, confirmer Bac jetons avec X final = 80 mm et Y/Z en automatique.
6. Dans Fabrication, confirmer les actions Bac vide, Bloc plein / cale et
   Separateur, puis cliquer Calculer la partition.
7. Confirmer : 3 corps finaux, 1 complement, 0 corps automatique.
8. Dans Resultat, observer les deux bacs, Cale pleine avant, les trois cavites,
   la vue dessus et la coupe X/Z.
9. Cliquer Materialiser dans Fusion.
10. Confirmer une seule scene BGIG, trois composants compacts, trois cavites
    ouvertes et aucune cavite dans la cale pleine.
11. Cliquer Regenerer la scene BGIG et confirmer une seule scene, trois
    composants et aucun doublon.
12. Cliquer Inspecter sans modifier la scene.
13. Cliquer Exporter les imprimables et confirmer trois STL plus les manifestes
    JSON et Markdown.

## Criteres KO

- navigateur ou serveur externe requis ;
- chargement infini ou absence de reponse versionnee ;
- presets ou champs X/Y/Z absents ;
- Bac jetons different de 80 mm en X local ;
- nombre de corps different de trois ;
- complement different de un ou corps automatique visible ;
- cale pleine contenant une cavite ;
- cavite de bac fermee, absente ou redimensionnee ;
- scene dupliquee apres regeneration ;
- objet non-BGIG supprime ;
- export different de trois bodies imprimables ou manifeste absent.

## Retour attendu

P60 Fusion OK 0.1.9, ou P60 Fusion KO avec le numero d etape, le texte visible
et le nombre de scenes/composants/bodies observe. Cette gate ne vaut pas
validation d impression.
