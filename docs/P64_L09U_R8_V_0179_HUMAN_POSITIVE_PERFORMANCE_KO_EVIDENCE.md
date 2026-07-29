# P64-L09U-R8-V — observation Fusion 0.1.79 positive, performance KO

Date : 2026-07-29.

## Verdict humain autoritaire

Thomas confirme sur la candidate Fusion 0.1.79 :

- un résultat « beaucoup mieux » ;
- un ordre, des dispositions et une composition qui lui semblent impeccables ;
- un résultat fonctionnel conforme en dehors du temps de calcul ;
- une durée d'environ `1 min 30`, contre environ `4 s` auparavant, jugée
  beaucoup trop longue.

Cette observation ferme le défaut géométrique autoritaire de la candidate
0.1.78 : aucune nouvelle plaque, aucun rail, appui, support ou volume positif
lié aux plateaux/livrets n'est signalé, et les cavités, l'ordre et les
dispositions observés sont conformes.

La gate 0.1.79 reste toutefois positive seulement sur son contrat fonctionnel.
La régression de performance est un défaut produit majeur et ouvre
P64-L09U-R9. La candidate n'est donc pas promue globalement
`fusion-validated`.

Statut :

- géométrie, ordre, dispositions et pipeline soustractif :
  `human-positive` dans Fusion ;
- performance de calcul : `human-KO` ;
- gate globale : `human-positive-partial` ;
- `fusion-validated=false` ;
- `print-validated=false`.

## Faits de performance déjà établis

Le temps humain observé est cohérent avec le profil versionné :

- `CasLimite02+` : succès en Approfondi maximal après `90,991 s` ;
- `CasLimite02++` : succès en Approfondi maximal après `87,192 s` ;
- finition historique : environ `2,1 s` ;
- matérialisation historique : environ `0,8 s`.

Le profil Approfondi maximal autorise actuellement jusqu'à `180 s`. Cette
durée est explicable par l'implémentation actuelle, mais elle n'est pas
acceptable comme cible produit.

Les temps exacts de chaque phase du dernier replay 0.1.79 n'ont pas été
transmis séparément. Il est donc interdit de leur inventer une valeur. La
preuve antérieure localise néanmoins le goulet principal dans la recherche de
disposition, pas dans la finition ni dans la matérialisation.

## Grille produit

La grille de recherche produit est déjà `0,1 mm`.

L'epsilon interne, généralement `0,0001 mm`, sert seulement aux comparaisons
numériques et topologiques. Il ne crée aucune position candidate et ne doit
pas être transformé en pas de recherche. Le relever à `0,1 mm` risquerait de
fausser contacts, parois et intersections sans apporter le gain attendu.

Les mesures R7 montrent que la quantification peut fusionner des ancres, mais
qu'elle ne réduit pas nécessairement les poses réellement évaluées :
`2450 -> 2450` sur un replay et `2500` poses sur `CasLimite02+`.

## Conséquence

R8 n'est pas à rejouer. Ses invariants géométriques deviennent des acquis
humains obligatoires de R9.

P64-L09U-R9 doit retrouver une performance de calcul maximale sous contrat
fonctionnel constant :

- même grille produit `0,1 mm` ;
- aucune modification d'épaisseur, de jeu ou de tolérance physique ;
- aucune perte de solution certifiée ;
- aucune régression de géométrie, d'ordre, de disposition, de cavité, de
  paroi, d'accès, de finalisation, de CAD IR, de plan Fusion ou de BRep ;
- aucun budget augmenté pour masquer le coût ;
- mesures avant/après honnêtes et décomposées par phase, lane, candidat,
  rejet, solveur, temps et mémoire.

La preuve canonique de départ est
`docs/P64_L09U_R8_A_SUBTRACTIVE_PIPELINE_DIAGNOSTIC_EVIDENCE.md`.
