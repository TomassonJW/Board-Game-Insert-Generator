# P60 - Acceptance du MVP V0.1 Fusion-only

## Statut

`prepared`, `automated-evidence-green`, `human-fusion-observation-required`,
`print-validated: false`.

## Perimetre accepte

Le produit teste est uniquement l add-in Fusion 360 et sa palette embarquee.
Aucun frontend, serveur localhost, navigateur ou Vite ne participe au parcours.

Le fixture `scripts/fusion/p60_mvp_project.json` demande deux bacs :

- `Bac jetons` avec les cavites `Pieces` et `Cubes` ;
- `Bac cartes` avec la cavite `Cartes sleevées` ;
- un livret reserve au-dessus ;
- aucun complement explicite ;
- aucun corps automatique.

## Preparation automatique

`scripts/fusion/prepare_p60_mvp_acceptance.ps1` installe l add-in du commit
courant, package tout le coeur pur, verifie les marqueurs P59, ecrit le projet
courant de facon atomique et enregistre le commit installe.

Preuves attendues avant ouverture de Fusion :

- partition construite : 2 corps finaux, 0 complement, 0 automatique ;
- CAD IR : 2 composants, 3 cavites top-open, digest deterministe ;
- plan Fusion hors API : 2 occurrences compactes, aucune occurrence eclatee ;
- installateur : manifeste 0.1.8 et `partition_cad.py` package.

## Checklist humaine Fusion

1. Ouvrir un nouveau design Fusion compatible Assembly.
2. Cliquer `BGIG - Atelier de rangement` dans Utilities et confirmer que seule la palette locale s ouvre.
3. Parcourir les six vues : Boite, Pieces, Plateaux, Bacs, Fabrication, Resultat.
4. Dans Fabrication, cliquer `Calculer la partition`.
5. Confirmer : 2 corps finaux, 0 complement, 0 corps automatique.
6. Dans Resultat, observer la vue dessus, la coupe X/Z, les deux noms de bacs et les trois cavites.
7. Cliquer `Materialiser dans Fusion`.
8. Confirmer une seule scene BGIG, deux composants compacts et trois cavites ouvertes sur le dessus.
9. Cliquer `Regenerer la scene BGIG`.
10. Confirmer qu il reste une seule scene, deux composants et aucun doublon.
11. Cliquer `Inspecter` et verifier l ownership BGIG sans modification de scene.
12. Cliquer `Exporter les imprimables` et confirmer deux STL plus les manifestes JSON et Markdown.

## Criteres KO

- navigateur ou serveur externe requis ;
- chargement infini ou absence de reponse versionnee ;
- nombre de corps different de deux ;
- corps automatique ou filler historique visible ;
- cavite fermee, absente ou redimensionnee ;
- scene dupliquee apres regeneration ;
- objet non-BGIG supprime ;
- export different de deux bodies imprimables ou manifeste absent.

## Retour attendu

`P60 Fusion OK`, ou `P60 Fusion KO` avec le numero d etape, le texte visible et
le nombre de scenes/composants/bodies observe. Cette gate ne vaut pas validation
d impression.