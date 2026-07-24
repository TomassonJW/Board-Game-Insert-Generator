# Human Gates

Les gates humaines protegent les decisions qui changent la vision, l'architecture
ou la credibilite physique du projet. Codex peut preparer les analyses, rapports,
options et prototypes hors gate, mais ne valide pas ces passages seul.

## Regle generale

Quand une gate est atteinte, Codex doit :

1. S'arreter avant mutation risquee.
2. Decrire le contexte.
3. Presenter les options.
4. Lister les impacts et risques.
5. Donner une recommandation argumentee si possible.
6. Attendre une validation humaine explicite.

## Delegation active pour l objectif MVP V0.1

Thomas a delegue les operations documentaires, Git et d integration normales
necessaires a l objectif V0.1. La revue P60 introduit toutefois des decisions
structurantes de modele produit, de reservation et de solveur. Conformement au
protocole, Codex documente les options mais ne reprend pas le runtime avant une
validation humaine explicite des ADR proposees.

Le GO humain du 2026-07-12 accepte ADR-0056 a ADR-0060 et ferme la gate
d architecture P60-R. P61 a P65 peuvent avancer sequentiellement selon leurs
dependances. La validation humaine finale reste l observation P66 dans Fusion
d un smoke prepare automatiquement.
Le produit observe est l add-in Fusion-only et sa palette embarquee ; aucun
Studio web ne participe a cette gate. Les gates physiques d impression et
les gates des V0.2/V0.3 restent hors de ce run.

## Operations Git standard

Les operations Git standard ne sont pas des gates humaines depuis la decision du
2026-07-03. La decision corrective du 2026-07-03 precise que le chemin standard
est l'integration directe dans `main`, puis le push de `main` vers `origin/main`,
quand les tests passent, que `git diff --check` passe, que la branche est basee
sur `origin/main` et qu'aucune vraie gate humaine n'est atteinte.

Codex peut donc pousser, integrer en fast-forward ou merge simple non conflictuel,
supprimer une branche integree et repartir de `origin/main` sans validation
humaine. Les pull requests sont seulement un repli si le push direct est refuse,
si une protection impose une PR, si une review humaine est requise, si un conflit
ou une divergence non triviale apparait, ou si la mission est risquee ou
structurante.

Une pause humaine reste obligatoire si l'infrastructure impose une review, si
l'authentification manque, si une protection de branche refuse le push ou le
merge, si un conflit reel apparait ou si une action risque de perdre du travail.

## Gates obligatoires

| Gate | Pourquoi elle existe | Ce que Codex peut preparer seul | Validation humaine | Rapport attendu |
| --- | --- | --- | --- | --- |
| Changement de North Star | La North Star protege la direction produit long terme. | Analyse d'ecart, options, impacts roadmap. | Accepter, refuser ou reformuler la nouvelle direction. | Contexte, ancienne formulation, nouvelle formulation, impacts. |
| Changement d'architecture majeure | Une architecture engage maintenance, tests et evolutivite. | ADR proposee, comparaison des options, prototype limite. | Choisir l'option et accepter les consequences. | ADR complete avec alternatives refusees. |
| Passage a une capability nouvelle structurante | Certaines capabilities changent le modele produit ou CAD. | Capability card, milestone, risques, validation matrix. | Autoriser le perimetre et le statut cible. | Capability, milestone, preconditions, tests, gates suivantes. |
| Changement du modele de tolerance | Les tolerances influencent la validite physique des inserts. | Analyse des cas, tests abstraits, tableau de valeurs. | Accepter la strategie et les valeurs par defaut. | Raison, valeurs, risques d'impression, plan de calibration. |
| Ajout de dependance lourde ou service externe | Les dependances augmentent cout, risque et complexite. | Justification, alternatives standard library, cout maintenance. | Autoriser la dependance et son perimetre. | Nom, usage, alternatives, plan de retrait. |
| Premiere integration Fusion 360 | Fusion ne doit pas aspirer la logique metier. | Rapport de readiness, contrat intermediaire, plan d'adaptateur. | Autoriser le debut de l'adaptateur. | Etat du moteur, tests, limites, surface Fusion ciblee. |
| Premiere generation Fusion exploitable | Une generation visible peut etre confondue avec une validation produit. | Script ou maquette, captures, verifications dimensionnelles. | Declarer le jalon comme accepte ou experimental. | Config source, sortie observee, ecarts, limites. |
| Premiere execution Fusion de cavites/features | Les cuts, booleans, fillets et geometries courbes peuvent echouer ou tromper sur la validation. | ADR technique, plan de smoke test, fixture CAD IR. | Autoriser types d'operations et limites. | Operations visees, risques Fusion, rollback, smoke test manuel. |
| Premier export STL/3MF | Un export imprimable engage le passage vers fabrication. | Plan d'export, fichiers tests locaux, checklist slicer. | Autoriser le format et les criteres minimaux. | Fichier, dimensions, warnings, tests realises. |
| Premiere impression 3D reelle | L'impression valide des hypotheses physiques non automatisables. | Coupon de test, protocole, tableau de mesure. | Confirmer les mesures et l'interpretation. | Imprimante, filament, slicer, photos ou notes, resultats. |
| Modification des valeurs de tolerance par defaut | Les valeurs par defaut affectent tous les utilisateurs. | Donnees de calibration, comparaison avant/apres, tests. | Accepter les nouvelles valeurs. | Anciennes valeurs, nouvelles valeurs, preuves, risques. |
| Passage aux modules composites | Les unions internes changent le modele geometrique. | Specification, tests de faces internes, ADR si necessaire. | Valider le modele et le premier scope. | Cas supportes, cas refuses, invariants, tests. |
| Passage aux couvercles, charnieres, mecanismes | Les mecanismes demandent des jeux fonctionnels reels. | Etude, representation abstraite, protocole de test. | Choisir les mecanismes autorises. | Type de mecanisme, jeux, risques, validation physique requise. |
| Decision esthetique structurante | L'esthetique ne doit pas casser fonction et modularite. | Options visuelles, contraintes epaisseur, impact CAD. | Choisir le langage visuel ou le reporter. | Intentions, options, contraintes, regles parametriques. |
| Suppression ou refonte massive de fichiers existants | Les refontes peuvent detruire le contexte autopilotable. | Inventaire, plan de migration, diff cible. | Autoriser le perimetre exact. | Fichiers touches, raison, rollback, tests. |
| Publication de release | Une release cree une promesse utilisateur. | Checklist, changelog, tests, limites connues. | Autoriser version, notes et publication. | Version, contenu, statuts, validations, risques. |
| Changement de licence ou de visibilite repo | Cela change les droits, obligations et exposition publique. | Inventaire, impacts, options. | Choisir licence ou visibilite. | Etat actuel, option proposee, consequences. |

## Gates de version canoniques

| Gate | Condition minimale | Ce qui reste humain | Effet |
| --- | --- | --- | --- |
| P60 - Base technique V0.1 | Parcours palette -> calcul -> apercu -> materialisation observe | Revue produit du parcours | Revue KO ; ne debloque pas V0.2 |
| ADR-0056 a ADR-0060 - Rebase produit | Alternatives, consequences et validations P61-P65 documentees | Acceptees par GO humain le 2026-07-12 | P61-P65 autorises sequentiellement |
| P66 - Acceptation V0.1 revisee Fusion-only | Etat reactif, plateaux encastres, orientations, multi-etages, conteneurs/reglages/apercu integres et scene sure | Observation Fusion du parcours complet, regeneration/export et absence de fuite technique | Clot le MVP et autorise P67 ainsi que les observations P68 ; n ouvre pas directement P44 |
| P67 - Priorisation post-MVP | P66 OK, rapport P67 et ADR-0062 proposee disponibles | Arbitrage humain de la fondation UX avant geometrie, des quatre onglets, du calcul, du cycle document, du premier P44 et des complements | Peut rendre uniquement P44-M001 ready |
| P46 - Acceptation V0.2 | Formes et ergonomie materialisees, contraintes de paroi et volume recalculees | Evaluation visuelle/ergonomique et observation Fusion | Autorise seulement alors le demarrage V0.3 |
| P50 - Validation V0.3 | Deux familles de couvercles conformes au contrat, coupons prepares | Impressions, mesures, glisse/tenue et interpretation | Autorise P69, sans qualifier automatiquement tout le produit |
| P69 - Revue UI/UX exhaustive | P44-P50 termines et retours P68 disponibles si des impressions existent | Audit commente, arbitrage du backlog et de la version suivante | Peut autoriser le cadrage P70+ ; aucun correctif n est implemente dans la gate |

Le smoke P34 n'est plus une gate active : le coupon ne correspond pas au
mecanisme coulissant canonique et la V0.3 est bloquee par P66, P67, P44-P46.

## Format minimal d'un rapport de gate

```markdown
# Gate report - <titre>

## Declencheur

Pourquoi cette gate est atteinte.

## Etat actuel

Ce qui existe, ce qui est teste, ce qui est experimental.

## Options

1. Option A.
2. Option B.
3. Option C.

## Recommandation

Choix propose et raison.

## Risques

Risques techniques, produit, validation et maintenance.

## Validation demandee

Decision concrete attendue de l'humain.
```

## P66 accepte - 2026-07-14

Thomas a confirme `P66 Fusion OK 0.1.20 - commit 6e351bb`. La gate P66 est
fermee : le MVP V0.1 Fusion-only est `mvp-accepted` et `fusion-validated`.
Cette decision ne qualifie pas l impression : `print-validated: false`.

P67 est maintenant `in-review`. P67-M000 a capture la revue UX sans runtime ;
P67-V est la prochaine decision humaine. Elle doit accepter, corriger ou refuser
le rapport et ADR-0062 proposee. Elle peut seule rendre P44-M001 `ready` ;
P44-P50 restent bloques jusque-la. P68 demeure une boucle de retours volontaires
`planned-after-p66`. Aucun tag ou release n est autorise par cette gate seule.

## P67 accepte - 2026-07-14

Thomas accepte explicitement D67-01 a D67-11, l option C et ADR-0062. La
fondation UX bornee devient la premiere partie de P44 ; les geometries restent
dans P45 et P46 reste la gate V0.2 complete.

Effet de gate : P67 est `done-human-gate` et seule P44-M001 devient `ready`
selon `docs/P44_M001_UI_STATE_STABILITY_CONTRACT.md`. P44-M002 et les missions
suivantes ne sont pas autorisees automatiquement. Les complements restent en
quarantaine pour maintenant ; leur reactivation exige toujours un contrat
separe.

La demande de jeux herites et surchargeables X/Y/Z par objet est acceptee comme
intention produit, pas comme formule ni changement de default. P44-M008 doit
produire le contrat de tolerance, les valeurs et les regles de resolution avant
P44-M009 et avant toute mutation du runtime. La valeur 0,2 mm observee n est pas
declaree universelle.

P45, P46, P47-P50 et P69 restent bloques par leurs dependances.
`print-validated: false` reste obligatoire.

## P44-M002V - Densite technique 0.1.23

Declencheur : le package 0.1.22 a passe les preuves automatisees mais a recu un
KO humain de compacite reelle.

Etat actuel : P44-M002V2 implemente l hybride A+B dans la palette 0.1.23, sans
changement metier. Les tests automatises peuvent prouver la structure, les
seuils responsives et la permanence des controles, mais pas le confort final
dans la palette Fusion.

Validation demandee : verifier a largeur normale et etroite au moins une carte
Asset, une carte Plateau/livret et une carte Conteneur. Confirmer que les bandes
sont denses et lisibles, que X/Y/Z/quantite restent groupes, que Placement,
Prise/tolerances et Solidite restent visibles, et que les calculs secondaires
sont replies.

Retour OK attendu :
`P44-M002V Fusion OK 0.1.23 - commit <sha>`

Un KO doit nommer la carte, la largeur approximative et le probleme observe.
P44-M003 reste bloque tant que cette gate n est pas fermee.

## P44-M002V acceptée - 2026-07-14

Thomas a retourné
`P44-M002V Fusion OK 0.1.23 - commit 2f78a99`.

La densité technique hybride A+B est `fusion-validated`. P44-M002V est
fermée et débloque P44-M003. La validation ne s’étend ni à la géométrie, ni à
l’impression : `print-validated: false`.

Le même retour ajoute une exigence de qualité linguistique : les futurs textes
utilisateur emploient les accents et caractères français corrects. P44-M003
l’applique aux textes qu’il touche ; P44-M006 effectue la passe exhaustive.


## P44-M003V - Quatre onglets et interversion X/Y 0.1.24

Déclencheur : P44-M003 est intégrée avec des preuves automatisées. La palette
change son parcours principal, mais n’a ni modifié le modèle produit ni la
scène Fusion.

Validation humaine demandée : observer les quatre onglets, les sections
réunies, les libellés français accentués, l’ordre de retrait et les quatre
portées d’interversion X/Y. Confirmer qu’une origine ne bouge pas et que la
rotation historique reste compatible sans encombrer le parcours normal.

Retour OK : `P44-M003V Fusion OK 0.1.24 - commit <sha>`.
Un KO ouvre seulement un hotfix P44-M003Hxx borné. P44-M004 reste bloquée tant
que cette gate n’est pas fermée.


## P44-M003V acceptée et P44-M004V ouverte — 2026-07-14

Thomas a retourné P44-M003V Fusion OK 0.1.24 - commit 7b71d01. La navigation à
quatre onglets et l’interversion X/Y de P44-M003 sont fusion-validated ; cette
preuve ne qualifie ni l’impression ni les futures formes.

P44-M004 est autorisée et ouvre P44-M004V pour le package 0.1.25. La gate
observe uniquement la projection conteneur parent / contenus enfants, le
déplacement secondaire, les modes Auto/Cible/Fixe, le cas historique
Personnalisé, le contrôle global confirmé et la préservation de l’état de
saisie. Elle ne valide ni géométrie, ni tolérance, ni scène automatique, ni
impression.

Retour OK : P44-M004V Fusion OK 0.1.25 - commit <sha>.

## P44-M004V2 ouverte — densité hybride C

Le retour humain sur 0.1.25 n’accepte pas la densité de P44-M004. Il ne constitue
ni une validation Fusion complète ni un échec du modèle parent/enfants.
P44-M004V2 ouvre une nouvelle observation bornée sur le package 0.1.26.

Observer à largeur habituelle et plus étroite : utilisation horizontale,
apparition rapide du premier conteneur, comparaison de plusieurs parents et
enfants, lisibilité des champs, stabilité des menus et cibles de 40 px. Vérifier
qu’aucun calcul ou scène Fusion ne part automatiquement.

Retour OK : P44-M004V2 Fusion OK 0.1.26 - commit <sha>.

Cette gate ne valide ni géométrie, ni tolérance, ni impression. P44-M005 reste
bloquée tant qu’elle n’est pas fermée.

## P44-M004V2H01 — gate 0.1.27

La revue 0.1.26 valide l’orientation de compacité mais demande de garder les
commandes de création accessibles pendant le défilement et de temporiser les
notifications.

Observer dans 0.1.27 que la barre Créer et la ligne Plateaux et livrets restent
juste sous les onglets, sans chevauchement à largeur habituelle ou étroite.
Confirmer qu’une notification de succès disparaît après environ 3 secondes et
qu’elle ne masque plus les premiers champs.

Retour OK : P44-M004V2 Fusion OK 0.1.27 - commit <sha>.

Cette gate ne valide ni géométrie, ni tolérance, ni impression.

## P44-M004V2 acceptée — 2026-07-15

Thomas a retourné "P44-M004V2 Fusion OK 0.1.27 - commit 80c1a6c".

La gate ferme P44-M004V2 et son hotfix H01 : la densité hybride C, la
comparaison conteneur / éléments, les deux barres collantes et les notifications
temporisées sont fusion-validated comme comportement UX observé. Cette preuve
ne valide ni schéma, ni bridge, ni solveur, ni tolérance, ni géométrie, ni CAD
IR, ni scène automatique, ni impression. print-validated: false.

P44-M005 devient prête mais ne commence pas sans GO explicite de Thomas.

## P44-M005V — création pilotée et presets 0.1.28

Déclencheur : P44-M005 est implémentée sans changement métier. La gate observe
seulement le parcours de création dans la palette Fusion.

Vérifier successivement : preset BGIG vers Nouveau conteneur lié, preset BGIG
vers conteneur existant, preset personnel vers les deux destinations, raccourci
+ local, suppression d’un preset personnel et persistance des éléments déjà
créés. Confirmer qu’aucun complément, calcul ou scène Fusion ne part.

Retour OK : P44-M005 Fusion OK 0.1.28 - commit <sha>.

Cette gate ne valide ni géométrie, ni tolérance, ni impression.

## P44-M005 acceptée — gate Fusion 0.1.28

Preuve humaine : "P44-M005 Fusion OK 0.1.28 - commit b8cf884".

Statut : done-human-gate, fusion-validated pour le parcours UX P44-M005 ;
print-validated: false.

La validation couvre la barre de création persistante, le preset et la
destination explicite (nouveau conteneur lié ou existant), les presets
personnels, le raccourci local "+", leur suppression locale et l'absence de
complément, calcul ou scène Fusion automatique. Elle ne qualifie ni schéma,
bridge, solveur, tolérance, géométrie, CAD IR ou impression.

P44-M006 devient ready-for-explicit-go et ne commence pas sans GO explicite.


## P44-M006V — cycle document, réglages et diagnostic Fusion

Statut : validated, package 0.1.30.

Preuve humaine : P44-M006 Fusion OK 0.1.30 - commit d82def6.

Le KO 0.1.29 est fermé : l’état Fusion de démarrage et Inspecter reste lisible,
et l’avertissement protège l’abandon d’une édition non enregistrée.

La preuve humaine doit couvrir le FileDialog natif Fusion pour Ouvrir et
Enregistrer sous, l’annulation sans perte, le nom du document courant, la
récupération après modification, l’ouverture d’un fichier et d’un récent, les
réglages visibles et la hauteur dérivée. Elle doit aussi constater que le
diagnostic reste replié, que l’effacement demande confirmation et qu’aucun
calcul, aucune scène ou matérialisation ne part automatiquement.

Preuve reçue : P44-M006 Fusion OK 0.1.30 - commit d82def6.
Cette gate ne valide pas l’impression réelle.

## P44-M009H01V - Volets de jeux X/Y + Z 0.1.32

Déclencheur : le retour humain sur 0.1.31 refuse les champs X, Y et Z visibles
dans les lignes principales et corrige le besoin en un jeu X/Y commun plus un
jeu Z distinct.

Observer dans Fusion que les volets Tolérance cavité, Jeu d’encastrement et
Jeu externe sont repliés par défaut. Les ouvrir et confirmer que X/Y est un
champ unique, que Z reste séparé lorsqu’il existe et qu’une modification X/Y
sur un asset, un plat et un conteneur est conservée après recalcul, sans
matérialisation automatique.

Retour reçu le 2026-07-16 :
P44-M009H01 Fusion OK 0.1.32 - commit 8fc5157.

Retour initialement accepté pour la présentation des volets et la saisie X/Y +
Z. La validation fonctionnelle est révoquée par l’observation suivante : elle ne
prouve ni l’isolation des overrides, ni la cohérence des defaults, ni les valeurs
physiques ou l’impression. P44-M007 reste bloquée par P44-M009H02V.

## P44-M009H02V - Isolation fonctionnelle des jeux 0.1.33

Déclencheur : après le retour P44-M009H01 initialement positif, une observation
plus poussée montre que les champs globaux et les defaults par rôle pouvaient
être désynchronisés et que la palette pouvait afficher des valeurs effectives
périmées. La preuve fonctionnelle H01 est donc révoquée ; sa validation visuelle
des volets reste seulement historique.

Observer dans Fusion sur au moins deux assets et trois conteneurs : override
asset inférieur puis supérieur, modification du default global, absence de
copie des valeurs entre cartes et deux gaps de conteneurs distincts. Le gap
d’une paire vaut le max des deux voisins de cette paire uniquement. Confirmer
aussi que « Hauteur de conception » est grisée et non éditable. Aucune scène ne
doit partir automatiquement.

Retour OK :
P44-M009H02 Fusion OK 0.1.33 - commit <sha>.

Cette gate qualifie uniquement le comportement UI/moteur observé dans Fusion.
Elle ne valide ni les valeurs physiques ni l’impression. P44-M007 reste bloquée
jusqu’à ce retour.
## P44-M009H03V - Jeux globaux et Réglages dense 0.1.34

Déclencheur : la revue produit annule la gate P44-M009H02V et retire le concept de jeu externe par bac. L’add-in 0.1.34 doit être installé depuis le commit intégré dans `main`.

Vérifier dans Fusion :

1. aucun conteneur n’affiche de réglage de jeu externe ;
2. les overrides asset, plateau et livret restent locaux et fonctionnels ;
3. Réglages sépare « Épaisseurs minimales » et « Jeux (tolérances) » ;
4. le tableau global affiche X/Y et Z pour jeu entre conteneurs, jeu conteneur-boîte et jeu élément-cavité par défaut ;
5. les jeux de conteneurs modifiés dans Réglages s’appliquent globalement ;
6. Z conteneur-boîte pilote la marge sous couvercle et la hauteur de conception reste grisée ;
7. aucune scène Fusion n’est créée ou modifiée automatiquement.

Retour OK :

`P44-M009H03 Fusion OK 0.1.34 - commit <sha>`

Cette gate qualifie uniquement le comportement UI/moteur observé dans Fusion. Elle ne valide ni les valeurs physiques ni l’impression. P44-M007 reste bloquée jusqu’à ce retour.

## P44-M009H04V - Densité finale UI 0.1.35

Déclencheur : la revue 0.1.34 confirme la fonction H03 mais demande une composition moins étirée dans Réglages et les cartes conteneur. L’add-in 0.1.35 doit être installé depuis le commit intégré dans `main`.

Vérifier dans Fusion :

1. Réglages forme un bloc compact aligné à gauche ; le tableau X/Y–Z ne rejette plus les champs à l’extrémité de la fenêtre ;
2. Épaisseurs minimales et Comportement sont compacts et lisibles ;
3. le nom du conteneur porte le nombre d’éléments juste dessous et le minimum reste proche ;
4. Auto n’affiche ni X/Y/Z explicites ni flèche ;
5. Cible et Fixe affichent X, la flèche, Y et Z dans l’en-tête, sans rangée supplémentaire ;
6. « Épaisseur paroi » et « Épaisseur fond » sont explicites ;
7. aucun comportement métier ou scène Fusion automatique ne change.

Retour OK :

`P44-M009H04 Fusion OK 0.1.35 - commit <sha>`

Cette gate qualifie uniquement la composition UI observée et la non-régression fonctionnelle dans Fusion. Elle ne valide ni les valeurs physiques ni l’impression. P44-M007 reste bloquée jusqu’à ce retour.

## P44-M009H05V - Distribution finale et mode global 0.1.36

Déclencheur : la revue 0.1.35 accepte la densité H04 mais demande la justification gauche/droite des cartes et révèle que le sélecteur global affiche toujours Auto, indépendamment de l’état réel.

Vérifier dans Fusion :

1. identité, nombre d’éléments et minimum restent groupés à gauche ;
2. Mode, dimensions contextuelles, épaisseurs et actions sont justifiés à droite ;
3. le mode global se trouve sur la ligne Conteneurs, sans bande supplémentaire ;
4. il affiche Mixte lorsque les cartes diffèrent et le mode réel lorsqu’elles sont uniformes ;
5. Appliquer Auto, Cible ou Fixe modifie les trois axes de tous les conteneurs ;
6. aucune scène Fusion n’est créée ou modifiée automatiquement.

Retour reçu le 2026-07-16 :

P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0

Cette gate qualifie uniquement la composition UI et le comportement du sélecteur global observés dans Fusion. Elle ne valide ni les valeurs physiques ni l’impression. P44-M007 est désormais ready-for-explicit-go.

## P44-M007V - Calcul adaptatif et Aperçu priorisé 0.1.37

Statut : KO fonctionnel observé en saisie rapide ; le package reconstruisait le DOM éditable et perdait focus/sélection. Gate remplacée par P44-M007H01V.

Déclencheur : P44-M007 est intégrée dans `main`, le package 0.1.37 est installé avec `scripts/fusion/prepare_p44_m007_adaptive_preview_test.ps1`, et les validations automatisées sont passées.

Vérifier dans Fusion :

1. modifier rapidement plusieurs dimensions ; le focus, la sélection et le scroll actifs restent stables ;
2. arrêter la saisie ; après environ 1,5 seconde, seule la proposition correspondant aux dernières valeurs devient visible ;
3. ouvrir Aperçu ; le statut compact et les vues dessus/X-Z précèdent les alertes et détails ;
4. modifier une valeur ; l’ancienne proposition est marquée à recalculer puis remplacée par la proposition courante ;
5. utiliser `Recalculer maintenant` ; la proposition se met à jour sans création ou modification de scène ;
6. vérifier que `Hauteur de conception` est grisée, dérivée et non éditable ;
7. vérifier qu’aucune scène BGIG ne change avant un clic explicite sur `Matérialiser dans Fusion`.

Retour OK :

`P44-M007 Fusion OK 0.1.37 - commit <sha>`

Cette gate qualifie uniquement l’orchestration UI et l’ordre de l’Aperçu observés dans Fusion. Elle ne valide ni les valeurs physiques, ni la géométrie imprimée, ni l’impression. `print-validated: false` reste inchangé et P44-V demeure la gate globale suivante.

## P44-M007H01V - Focus stable, cartes explicites et conteneurs repliables 0.1.38

Statut : superseded-before-observation par P44-M007H02V.

Déclencheur : P44-M007H01 est intégrée dans `main`, le package 0.1.38 est
installé avec `scripts/fusion/prepare_p44_m007_adaptive_preview_test.ps1`, et
les validations automatisées sont passées.

Vérifier dans Fusion :

1. sélectionner entièrement la valeur d’un champ numérique, saisir son
   remplacement puis enchaîner immédiatement sur au moins deux autres champs ;
   les réponses d’autosave, minima et proposition ne retirent ni focus ni
   sélection ;
2. arrêter la saisie ; après environ 1,5 seconde, seule la proposition
   correspondant aux dernières valeurs devient visible ;
3. sur une carte, vérifier que `Méthode de mesure` est entre Forme et X ;
4. avec `Épaisseur paquet`, vérifier que Z apparaît et que Qté et Épaisseur
   carte sont masqués ;
5. avec `Épaisseur carte × nb`, vérifier que Z est masqué et que Qté et
   Épaisseur carte apparaissent ;
6. activer les sleeves : vérifier le delta X/Y et, en mode compté, le delta Z
   par carte ; les deux restent modifiables ;
7. replier puis déplier un conteneur ; son en-tête complet reste visible et
   seuls ses assets disparaissent lorsqu’il est replié ;
8. ouvrir Aperçu ; statut compact et vues dessus/X-Z précèdent alertes et
   détails ;
9. utiliser `Recalculer maintenant` sans création ou modification de scène ;
10. vérifier que `Hauteur de conception` est grisée, dérivée et non éditable ;
11. vérifier qu’aucune scène BGIG ne change avant un clic explicite sur
    `Matérialiser dans Fusion`.

Retour OK :

`P44-M007H01 Fusion OK 0.1.38 - commit <sha>`

Cette gate qualifie uniquement l’orchestration UI, la stabilité de saisie et la
composition des cartes et conteneurs observées dans Fusion. Elle ne valide ni
les valeurs physiques, ni la géométrie imprimée, ni l’impression.
`print-validated: false` reste inchangé et P44-V demeure la gate globale
suivante.

## P44-M007H02V - Focus stable et calcul sleeves cartes 0.1.39

Statut : superseded-after-contextual-KO par P44-M007H03V. Le retour Fusion sur
0.1.39 a montré un delta X/Y manuel absent de `Résolu` et des faits dérivés
visuellement anciens. Cette gate remplaçait P44-M007H01V, non observée.

Déclencheur : P44-M007H02 est intégrée dans `main`, le package 0.1.39 est
installé avec `scripts/fusion/prepare_p44_m007_adaptive_preview_test.ps1`, et
les validations automatisées sont passées.

Vérifier dans Fusion :

1. remplacer rapidement la sélection complète d’au moins trois champs ;
   autosave, minima et proposition ne retirent ni focus ni sélection ;
2. après stabilisation, seule la proposition correspondant aux dernières valeurs
   devient visible ;
3. le preset `Cartes` est non sleevé par défaut ;
4. `Méthode de mesure` est le dernier champ avant le menu `...`, après Z en
   épaisseur paquet et après Épaisseur carte en mode compté ;
5. les champs Z ou Qté/Épaisseur carte sont affichés selon la méthode ;
6. activer les sleeves expose 3 mm sur X/Y et 0,19 mm par carte sur Z dans les
   deux méthodes ;
7. avec Z paquet = 24 mm, le champ grisé estime 77 cartes et le Z résolu vaut
   38,63 mm ; désactiver les sleeves ramène le Z résolu à 24 mm ;
8. le repli d’un conteneur conserve son en-tête ;
9. Aperçu, fallback manuel, hauteur grisée et matérialisation exclusivement
   explicite restent conformes.

Retour OK :

`P44-M007H02 Fusion OK 0.1.39 - commit <sha>`

Cette gate qualifie la stabilité de saisie, la composition UI et le calcul
logiciel observés. Elle ne calibre pas physiquement 3 mm, 0,19 mm ou 0,31 mm,
ne valide pas la géométrie imprimée et ne vaut pas validation d’impression.
`print-validated: false` reste inchangé.

## P44-M007H03V - Repli global et résolution sleeves cohérente 0.1.40

Statut : fusion-validated: true. Retour Fusion reçu le 2026-07-16 :
`P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`. Le delta X/Y manuel,
les faits dérivés et l’estimation sont cohérents dans le parcours observé.
P44-M007H02V est supersédée par cette gate corrective.

Déclencheur : P44-M007H03 est intégrée dans `main`, le package 0.1.40 est
installé avec `scripts/fusion/prepare_p44_m007_adaptive_preview_test.ps1`, et
les validations automatisées sont passées.

Vérifier dans Fusion :

1. remplacer rapidement la sélection complète d’au moins trois champs sans perte
   de focus ni de sélection ;
2. pendant le recalcul, le fait carte affiche `À recalculer`, puis uniquement le
   résultat correspondant à la dernière saisie ;
3. les boutons `Compact` et `Détaillé` sont absents ;
4. le bouton discret à droite de `Conteneurs` replie et déplie tous les
   conteneurs, tandis que chaque conteneur reste pilotable individuellement ;
5. les placeholders des épaisseurs de paroi et de fond indiquent `Défaut` ;
6. les contrôles cartes tiennent sur une ligne large et le champ grisé est nommé
   `Nb cartes` ;
7. pour X = 66, Y = 88, Z = 27, sleeves actifs, delta X/Y = 3 et delta Z/carte =
   0,19, `Nb cartes` vaut 87 et `Résolu` vaut 69 × 91 × 43,53 mm ;
8. désactiver les sleeves ramène `Résolu` à 66 × 88 × 27 mm sans cumul ;
9. l’Aperçu, le fallback manuel, la hauteur grisée et la matérialisation
   exclusivement explicite restent conformes.

Retour OK :

`P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`

Cette gate qualifie l’UX et le calcul logiciel observés. Elle ne calibre pas les
valeurs physiques, ne valide pas la géométrie imprimée et ne vaut pas validation
d’impression. `print-validated: false` reste inchangé.

## P44-V - Gate globale de fondation UX 0.1.40

Statut : ready-for-human-fusion-check sur 0.1.55. Voir docs/P44_V_FOUNDATION_UX_GATE.md.

Vérifier les sept scénarios novice/expert, largeur, clavier/focus, conteneurs, import historique et scène préservée du dossier.

Retour 0.1.40 interdit après KO : `P44-V Fusion OK 0.1.40 - package 92f07c8`.

Cette gate ne valide ni P45, ni les valeurs physiques ou l’impression. `print-validated: false`.


## P44-VH01V - Hauteur dérivée et reprise multi-étages 0.1.41

Statut : superseded par P64-H01V après observation contextuelle du cas initial. Aucun retour formel P44-VH01 n'a été reçu ; fusion-validated reste false.

Déclencheur : P44-VH01 intégrée dans main, package 0.1.41 installé par scripts/fusion/prepare_p44_vh01_design_height_test.ps1 et validations automatisées vertes.

Vérifier dans Fusion :

1. ouvrir le projet dense qui échouait avec ses plateaux/livrets ;
2. modifier Z et confirmer que Hauteur de conception vaut Z moins le jeu Z conteneur-boîte ;
3. avec une hauteur volontairement très grande, recalculer et observer plusieurs étages sans anciens diagnostics de fond liés à une hauteur cachée ;
4. remettre une hauteur réaliste et vérifier que tout refus restant dépend de cette hauteur réelle ;
5. confirmer qu’aucune scène ne change avant Matérialiser dans Fusion.

Retour OK : P44-VH01 Fusion OK 0.1.41 - commit <sha>.

Cette gate ne valide aucune dimension physique, aucune géométrie imprimée et aucune impression. print-validated: false.


## P64-H01V - Recherche dense et équilibre spatial 0.1.42

Statut : fusion-validated: true. Preuve Fusion reçue le 2026-07-17 : `P64-H01 Fusion OK 0.1.42 - commit 5865645`. Cette gate remplace P44-VH01V sans
transformer l'observation contextuelle précédente en fusion-validation.

Déclencheur : P64-H01 intégrée dans main, package 0.1.42 installé par
scripts/fusion/prepare_p64_h01_balanced_dense_solver_test.ps1 et validations
automatisées vertes.

Vérifier dans Fusion :

1. rouvrir le projet réel avec environ 30 conteneurs et 77 éléments en mode
   Équilibré ;
2. conserver une hauteur utile réaliste proche de 183 mm et ajouter le petit
   asset qui déclenchait le faux impossible ;
3. vérifier que le calcul reste constructible, utilise plusieurs niveaux Z et
   n'affiche plus les anciens diagnostics sans rapport avec le volume restant ;
4. observer que la composition répartit X, Y et Z au lieu d'attendre
   systématiquement la saturation XY ;
5. modifier encore un petit asset et vérifier que la proposition reste courante
   et cohérente ;
6. confirmer qu'aucune scène ne change avant Matérialiser dans Fusion.

Retour reçu : P64-H01 Fusion OK 0.1.42 - commit 5865645.

Cette gate valide uniquement le comportement logiciel observé dans Fusion. Elle
ne calibre aucune valeur physique, ne valide aucune géométrie imprimée et ne
vaut pas validation d'impression. print-validated: false.


## P44-VH02V - Suppression directe et noms de conteneurs non ambigus 0.1.43

Statut : human-fusion-check-required. P44-VH02 est implementee et automated-validated dans le package 0.1.43.

Preparation : `scripts/fusion/prepare_p44_vh02_direct_delete_test.ps1`.

Verifier dans Fusion :

1. la croix de suppression est visible a cote du menu `...` de chaque element et ne supprime que cet element ;
2. supprimer un conteneur non vide demande une confirmation explicite ; Annuler ne modifie rien ;
3. confirmer supprime atomiquement le conteneur et tous ses elements ;
4. les nouveaux conteneurs au meme nom recoivent un suffixe numerique incrementiel ;
5. aucune scene ne change avant `Materialiser dans Fusion`.

Retour OK : `P44-VH02 Fusion OK 0.1.43 - commit <sha>`.

Cette gate valide uniquement le comportement logiciel observe dans Fusion. Elle ne valide ni valeurs physiques, ni geometrie imprimee, ni impression reelle. `print-validated: false`.
Retour contextuel reçu le 2026-07-17 : annulation, suppression atomique et noms
sont observés comme OK, mais la croix apparaît sur une ligne séparée. Le package
0.1.43 ne reçoit donc pas de preuve Fusion OK ; P44-VH02V est supersédée par
P64-H02V. Le même retour révèle aussi un nouveau faux impossible du solveur.

## P64-H02V — Reprise diversifiée et actions alignées 0.1.44

Statut : contextual-KO. P64-H02 et P44-VH02H01 sont implemented et
automated-validated dans le package 0.1.44, mais aucun retour Fusion OK ne doit
être envoyé pour ce package.

Préparation historique — ne pas relancer : `scripts/fusion/prepare_p64_h02_diversified_portfolio_test.ps1`.

Vérifier dans Fusion :

1. recharger l’add-in sans modifier les dimensions du projet problématique laissé
   ouvert ;
2. vérifier que chaque croix d’élément est sur la même ligne que `...`, juste à
   sa droite ;
3. cliquer `Recalculer maintenant` : les 8 conteneurs doivent être placés sur
   2 niveaux, sans `TOP_INSET_PIERCES_CAVITY_FLOOR` ni `Calcul impossible` ;
4. modifier ou ajouter un petit élément et vérifier que le recalcul reste courant
   et constructible ;
5. confirmer qu’aucune scène BGIG ne change avant `Matérialiser dans Fusion`.

Retour historique non reçu — ne pas envoyer : `P64-H02 Fusion OK 0.1.44 - commit <sha>`.

La portée prévue se limitait à ces comportements logiciels. Le KO conserve les
observations UX partielles, mais n'accorde aucune `fusion-validation` au package
0.1.44. Il ne calibre aucune valeur physique, ne valide aucune géométrie
imprimée et ne vaut pas impression réelle. `print-validated: false`.

## P64-V2 — Gate portefeuille multi-solveurs 0.1.51

Statut : contextual-KO. Les contrôles sont visibles, mais le projet dense réel
laissé dans Fusion reste faussement sans solution et la répartition n'est pas
jugée suffisamment harmonieuse. Aucun retour P64-V2 Fusion OK 0.1.51 ne doit
être envoyé.

Cette observation ne valide ni valeurs physiques ni impression.

## P64-V2H01 — Gate fermeture continue corrective 0.1.52

Statut : contextual-KO après extension du projet réel à 11 conteneurs et 34
contenus. Le package 0.1.52 ne doit pas recevoir de preuve Fusion OK.

La fixture automatisée à 9 corps reste certifiée et devient une non-régression
du portefeuille. La préparation historique est
`scripts/fusion/prepare_p64_v2h01_continuous_closure_test.ps1`, mais elle n'est
plus la gate active.

Retour historique non reçu — ne pas envoyer :
`P64-V2H01 Fusion OK 0.1.52 - commit <sha>`.

Les comportements acquis sont conservés dans 0.1.53 par la variante EMS
historique. Aucune validation physique ou d'impression n'est revendiquée.
`print-validated: false`.

## P64-V2H02R — Correctif de repère de la vue de dessus 0.1.54

Statut : fusion-validated. Preuve reçue le 2026-07-18 : `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`. La gate est fermée ; cette preuve ne couvre pas les valeurs physiques, l'impression ni la résolution du cas dense.
Préparation historique : `scripts/fusion/prepare_p64_v2h02_capacity_search_test.ps1`.

Checklist observée dans Fusion sur un projet simple résolu, puis sur le projet dense laissé
dans son état reproductible :

1. la carte de capacité affiche volume utilisable, enveloppes minimales et marge
   théorique en cm³ et mm³ sur succès comme sur absence de candidat ;
2. une marge positive est présentée comme borne nécessaire, jamais comme promesse
   de placement ;
3. le cas dense affiche `non résolu dans le budget` et non `impossible`, sans
   mesure négative issue d'une branche rejetée ;
4. Rapide, Normal et Approfondi exposent respectivement 1, 2 et 4 priorités beam,
   des largeurs 8, 24 et 64 et leur durée réelle ;
5. Auto intelligent et Placement 3D libre affichent leur chaîne distincte, même
   lorsqu'ils aboutissent au même statut ou au même meilleur candidat ;
6. la vue de dessus peint les corps supérieurs au-dessus des cavités inférieures
   et représente Y comme observée depuis le dessus (miroir autour de l'axe X), sans modifier la coupe X/Z ;
7. aucune scène ne change avant `Matérialiser dans Fusion`.

Retour reçu : `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`.


Cette gate ne demande pas de confirmer que le cas dense est soluble. Elle valide
la vérité du résultat, la capacité informative, les budgets et la vue. Elle ne
calibre aucune valeur physique, ne valide aucune géométrie imprimée et ne vaut
pas impression réelle. `print-validated: false`.

## P64-V2H03A — Arbitrage de propriété accepté

Le GO explicite transmis le 2026-07-18 autorise la reprise directe de
P64-V2H03 / P45 et délègue l'arbitrage borné nécessaire avant code. ADR-0070
retient une frontière à deux certificats : P45 possède la sémantique et le
certificat local ; P64 possède les budgets, la sélection globale et le
certificat du plan complet.

Effet de gate : l'arbitrage architectural P64-V2H03A est fermé et seule
P64-V2H03B devient `ready`. Cette autorisation n'ouvre ni les modes ou formes
P45, ni P64-V2H03C avant les fixtures/caps de B, ni P44-V/P46.

Aucune nouvelle preuve Fusion ou physique n'est acquise.
`fusion-validated: false` et `print-validated: false` pour P64-V2H03.

## P64-V2H03B — Frontière locale clôturée automatiquement

Statut : `implemented-core`, `automated-validated`. Le lot ne modifie ni
sélection publique, ni UI, ni scène et ne demande aucune observation Fusion.

P64-V2H03C devient `ready`. Une gate humaine ne sera préparée qu'après C si
un comportement visible doit être observé. `fusion-validated: false` et
`print-validated: false` pour P64-V2H03.

## P64-V2H03C — Sélection globale clôturée automatiquement

Statut : `implemented-core`, `automated-validated`. Le cul-de-sac minimal et la
réservation localisée sont certifiés hors Fusion ; les profils, caps, digests,
annulation et non-régressions denses sont couverts par 566 tests.

Le mécanisme dense 11 × 34 reste `no_solution_within_budget` jusque dans la lane
Deep. H03C ne transforme ni cette absence de certificat en impossibilité, ni une
marge volumique positive en promesse de disposition.

Le résultat public pouvant changer sur un projet multi-cavités, P64-V2H03V
devient `ready`. Aucune preuve Fusion ou physique n'est acquise par C.
`fusion-validated: false`, `print-validated: false`.

## P64-V2H03V — Gate Fusion préparée

Statut : `ready-for-human-fusion-check`. Le package 0.1.55 et les fixtures sont
préparés par `scripts/fusion/prepare_p64_v2h03v_variant_gate.ps1`. Le préparateur
installe l'add-in, préserve le projet et l'état document existants dans des
backups bornés, charge la fixture variantes, conserve un contrôle canonique
récent, règle `Auto intelligent + Rapide` et vérifie le marqueur de commit.

Thomas observe seulement :

1. le cul-de-sac multi-cavités produit une solution visible avec deux variantes
   internes non canoniques ;
2. le diagnostic secondaire expose effort, lane, budgets, compteurs, variantes
   retenues, certificat global, canonique-first et absence de produit cartésien,
   tout en restant replié dans le parcours normal ;
3. le contrôle `p64-v2h03v-simple-control.bgig.json` conserve une solution
   `Étages et piles` sans trace de fallback ;
4. la palette reste stable et aucune scène ne change avant l'action explicite
   `Matérialiser dans Fusion` ;
5. tout cas dense éventuellement observé reste présenté comme
   `no_solution_within_budget`, jamais comme impossible sur le seul volume.

Retour attendu :
`P64-V2H03V Fusion OK 0.1.55 - commit <sha>`, ou un KO contextuel avec projet,
méthode, effort, statut visible et diagnostic.

Cette préparation n'est pas une preuve Fusion. Elle ne calibre aucune valeur
physique, ne valide aucune forme P45 et ne vaut pas impression réelle.
`fusion-validated: false`, `print-validated: false`.


## P64-A02 — Arbitrage de calcul étagé et capacité accepté

Statut : gate d'architecture fermée le 2026-07-21 par le GO explicite de Thomas.
ADR-0071 et ADR-0072 sont acceptées comme cible produit. Cette décision autorise
la documentation détaillée et le découpage des futures missions ; elle ne
constitue ni une preuve runtime, ni une preuve Fusion, ni une preuve physique.

Décisions humaines acquises :

1. une édition déclenche seulement les dérivations locales et bornes globales
   nécessaires ; elle ne doit plus imposer à terme un solve global complet ;
2. le solve global devient une action primaire explicite ;
3. la finalisation du volume devient une action séparée, remplaçable ou
   désactivable ;
4. les meilleurs candidats locaux sont expliqués dans une section repliée ; une
   shortlist de trois est un choix UX, pas un plafond de recherche ;
5. les opportunités post-solve peuvent accélérer une insertion locale, mais
   toute modification est recertifiée et aucune zone technique n'est assimilée
   à une réserve fonctionnelle ;
6. l'ajout d'un conteneur autonome sans baie réservée déclenche un solve global,
   il ne bénéficie pas d'une promesse de réutilisation locale.

Les gates P64-L03V et P64-CV sont déclarées pour les futurs comportements
visibles, mais elles ne sont pas actives. P64-V2H03V est clôturée ; la prochaine
gate à requalifier est P44-V. fusion-validated reste false pour P64-A02 et
print-validated reste false.


## P64-V2H03V — Gate Fusion clôturée

Statut : fusion-validated par le retour humain reçu le 2026-07-21 :
`P64-V2H03V Fusion OK 0.1.55`.

Cette preuve clôt la gate 0.1.55 pour son périmètre : le cul-de-sac
multi-cavités montre des variantes internes non canoniques et un certificat
global ; le diagnostic secondaire reste replié et expose la trace attendue ; le
contrôle canonique conserve Étages et piles ; la palette reste stable et aucune
scène ne change avant Matérialiser dans Fusion.

La preuve ne déclare pas le mécanisme dense 11 × 34 soluble, ne transforme pas
no_solution_within_budget en impossible, ne valide aucune forme P45, ne calibre
aucune valeur physique et ne vaut pas impression réelle.
`print-validated: false`.

Effet : P64-V2H03 est clôturée. P44-V devient la prochaine gate à requalifier ;
P45 reste bloquée jusqu'à cette requalification.


## P44-V - Validation Fusion 0.1.55 (2026-07-21)

Statut : done-human-gate, fusion-validated pour la fondation UX P44. Retour humain : P44-V Fusion OK 0.1.55 - commit 70d45c6.

Reserve explicite : le scenario d environ 50 conteneurs n a pas ete observe, car il ne pouvait pas etre controle dans un volume raisonnable. Cette gate ne revendique donc pas cette preuve de charge. Elle valide la palette actuelle, la saisie, le repli, la preservation de scene et l absence de materialisation automatique. P45 est debloque pour son cadrage contractuel. print-validated: false.


## P45-M001V — Contrat accepté avec interface de pile unifiée

Statut : done-human-gate le 2026-07-21. Aucun test Fusion n'était demandé :
P45-M001 est documentaire.

Retour humain : `P45-M001 contrat accepté` sous réserve intégrée d'un composant
commun aux cartes et aux autres assets :

- `Pile` active les dimensions unitaires, l'épaisseur et le nombre par pile ;
- les cartes neuves sont empilées par défaut ;
- `Basculer` révèle `Poser sur : Grand côté / Petit côté` ;
- le sleeving reste spécifique aux cartes ;
- pose, disposition locale P45 et placement global P64 restent séparés ;
- aucune permutation avec Z ni fallback silencieux n'est autorisé.

Effet : P45-M001 et ADR-0073 sont `architecture-accepted`. P64-L01 devient la
prochaine mission `ready`. Aucun runtime, schéma, UI ou calcul P45 n'est validé
par cette gate. `fusion-validated: false`, `print-validated: false`.

## P64-L02 — Preuve automatisée, aucune gate Fusion ouverte

- P64-L02 ne requiert aucune nouvelle gate humaine pour être intégré : il ne génère ni géométrie ni scène et ne revendique aucune validation Fusion ou impression.
- Les statuts fusion-validated et print-validated restent false.
- Toute future revendication physique ou Fusion demeure soumise aux gates existantes et à une preuve humaine distincte.

## P64-L03V — Gate Fusion du cycle explicite

Statut : historique, supersédé par le KO contextuel documenté ci-dessous.

Le package 0.1.56 avait été préparé pour observer édition locale, actions
Calculer/Finaliser, stale, absence de scène automatique, focus et diagnostic.
La revue a ensuite refusé la sémantique géométrique minimal/final.

`fusion-validated: false`, `print-validated: false`.

## P64-L03V — KO contextuel et gate corrective

Statut : `contextual-KO` sur Fusion 0.1.56, retour humain du 2026-07-21.

Observations acquises : l'édition locale ne lance plus le solve global, les
actions sont explicites, le stale est visible et aucune scène ne change
automatiquement.

Refus : `Calculer` présente déjà des enveloppes remplies par surplus,
`Finaliser` conserve cette géométrie sans transformation, la matérialisation
minimale est interdite et une scène ancienne peut masquer l'action de mise à
jour après nouveau solve/finalisation.

Effet : aucune preuve `fusion-validated` n'est accordée à P64-L03. ADR-0074 et
P64-L03R-A sont acceptés comme correction documentaire. La prochaine gate
humaine sera P64-L03R-V, seulement après L03R-B et L03R-C automatisés.

P64-L03R-V devra observer : volumes minimaux non étendus, résiduel visible,
matérialisation avant finition, scène stale après édition, remplacement sans
doublon et objets utilisateur préservés. Elle ne valide ni valeur physique ni
impression. `print-validated: false`.

## P64-L03R-B — Preuve automatisée, aucune gate humaine

Statut : `implemented-core`, `automated-validated`.

L03R-B ne modifie ni bridge, ni CAD IR, ni palette, ni scène Fusion. Il produit
un artefact cœur minimal certifié, conserve le résiduel non attribué et ne
revendique aucune observation Fusion ou impression. Le cas dense 11 × 34 reste
`no_solution_within_budget`.

Effet historique : P64-L03R-C est ensuite devenu `ready`, puis a été clôturé
automatiquement. Il n'y avait aucune revue humaine à demander entre B et C.
`fusion-validated: false`, `print-validated: false`.

## P64-L03R-C — Preuve automatisée, aucune revue humaine

Statut : `implemented-core`, `implemented-fusion-bridge`,
`implemented-fusion-ui`, `automated-validated`.

C matérialise le plan minimal avant finition, transporte l'identité exacte de
l'artefact et remplace uniquement une scène BGIG possédée et non ambiguë. Les
tests simulés ne valent aucune observation Fusion. La preuve est
`docs/P64_L03R_C_DUAL_MATERIALIZATION_EVIDENCE.md`.

Effet : P64-L03R-V devient la prochaine gate humaine. `fusion-validated: false`,
`print-validated: false` tant que Thomas n'a pas observé le parcours 0.1.57.

## P64-L03R-V — Gate Fusion corrective active

Statut : `ready-human-gate`. Cible : package Fusion 0.1.57, préparé par
`scripts/fusion/prepare_p64_l03r_v_corrective_test.ps1` après intégration du
commit de C.

Thomas doit observer :

1. édition locale sans solve global ni mutation de scène ;
2. plan minimal non étendu et résiduel visible après calcul ;
3. matérialisation des volumes minimaux avant toute finition ;
4. ancienne scène visible mais désynchronisée après édition ;
5. action `Mettre à jour la scène` après nouveau calcul ;
6. exactement une scène BGIG après remplacement ;
7. conservation d'un corps utilisateur témoin non tagué ;
8. identité technique exacte et aucun corps automatique.

Retour attendu : `P64-L03R-V Fusion OK 0.1.57 - commit <sha>`, ou KO contextuel
avec projet, étape, statut visible et diagnostic. Cette gate ne valide ni
calibration physique, ni imprimabilité, ni impression réelle.


## P64-L03R-V — observation exploratoire reprise par P64-L04

Statut au 2026-07-22 : observation humaine réelle mais retour formel de gate non
reçu. Le package 0.1.57 montre un plan minimal nettement plus prometteur et la
séparation calcul / matérialisation est comprise. Les réserves portent sur la
réutilisation locale, l’effort Approfondi et l’absence d’indication pendant les
opérations longues.

Cette observation ne doit pas être transformée en `P64-L03R-V Fusion OK` et ne
promeut aucune capability en `fusion-validated`. ADR-0075 reprend les réserves
dans P64-L04A/B/C. La prochaine gate Fusion est regroupée dans P64-L04V après
les lots B et C ; l’ancien préparateur 0.1.57 reste une preuve historique.

## P64-L04A — clôture automatisée sans revue humaine

Statut : `implemented-core`, `implemented-fusion-bridge`,
`implemented-fusion-ui`, `automated-validated`.

Le lot tente une insertion ou modification locale dans l’enveloppe exacte d’un
conteneur déjà placé, puis rejoue le certificat global sans recherche de
placement. Un succès garde toutes les poses monde ; un échec rend l’ancien plan
obsolète et demande un solve explicite. Toute scène reste inchangée et devient
seulement désynchronisée.

Aucune revue humaine n’est requise entre L04A et L04B : les invariants sont
prouvables hors Fusion et la mission ne revendique aucune observation Fusion.
Le package passe à 0.1.58 pour la future gate combinée.
`fusion-validated: false`, `print-validated: false`.

## P64-L04B / P64-L04C — aucune gate intermédiaire

P64-L04B est `implemented-core` et `automated-validated` : le préfixe Normal
fournit l’incumbent et les trois lanes Deep partagent une deadline de 30 s. Le
manifest Fusion reste à 0.1.58 ; aucune installation ou revue humaine n’est
requise pour cette clôture cœur.

P64-L04C est implemented-core, implemented-fusion-bridge,
implemented-fusion-ui et automated-validated. Il expose identité, étape et temps
écoulé sans faux pourcentage ni annulation décorative. Aucune gate humaine
n'était requise pendant son implémentation automatisée.

## P64-L04V — prochaine gate Fusion combinée

Statut : ready-human-gate. L04A, L04B et L04C sont automated-validated ;
la préparation et l'installation appartiennent à une mission de gate distincte.

La gate devra observer au minimum :

1. insertion locale réussie sans solve global ni déplacement de voisins ;
2. fallback explicite lorsque l’enveloppe ne suffit pas ;
3. plan minimal toujours non finalisé et matérialisable ;
4. scène ancienne désynchronisée puis remplacée sans doublon ;
5. activité immédiate, étape et temps écoulé pendant calcul et matérialisation ;
6. absence de faux pourcentage et de double lancement ;
7. identité technique et compteur global à zéro sur la voie locale.

Cette gate ne valide ni valeur physique, ni imprimabilité, ni impression réelle.

### Mise a jour P64-L04V preparation (2026-07-22)

Statut : preparation automatisee validee, ready-human-gate. Le preparateur, la baseline portable et la checklist sont versionnes ; la preuve hors Fusion est docs/P64_L04V_FUSION_GATE_PREPARATION_EVIDENCE.md. Installation reelle et observation visuelle restent humaines.

## Retour P64-L04V — gate globalement KO (2026-07-22)

Observation humaine réelle sur « Mon insert » :

- positif : ajout d'assets dans le volume libre d'un conteneur existant ;
- positif partiel : Approfondi conserve le résultat Normal lorsqu'un incumbent existe ;
- KO : aucun chemin incrémental pour un nouveau conteneur dans le vide global ;
- KO : un plan certifié matérialisé n'est pas reconstructible depuis zéro ;
- KO UX/correctness : un échec Approfondi pouvait être restitué du cache en 0 s.

R1 corrige automatiquement le dernier point, sans observation Fusion nouvelle.
Les autres KO ouvrent L05A à L05D. P64-L04 n'est pas promu
fusion-validated ; print-validated: false.

## P64-L05A / L05B — aucune gate intermédiaire

P64-L05A est automated-validated. Aucune observation Fusion n’est nécessaire
pour ouvrir L05B, conformément au GO humain du programme correctif. L05B capture
des cas de développement mais ne déclenche aucun solve, aucune finalisation et
aucune scène. Une future gate Fusion sera cadrée seulement après les lots
automatisés pertinents.

fusion-validated: false, print-validated: false pour L05A.

## P64-L05V - gate Fusion de capture reelle

Statut : ready-human-gate. Preparation et installation locales verifiees par P64-L05V-A.

P64-L05V ne valide aucune impression. Elle doit observer dans le package issu du
commit integre :

1. insertion d'un nouveau petit conteneur dans le vide global a voisins figes ;
2. fallback explicite si cette insertion locale n'est pas certifiable ;
3. rechargement d'un witness certifie apres changement temporaire d'effort ;
4. recherche courante toujours executee, sans cache hit revendique ;
5. bouton DEV rouge visible ;
6. capture sans solve, finalisation, CAD ni modification de scene ;
7. SolverCaseBundle cree localement avec identite, digests et statut observes ;
8. activite, budgets, lanes, temps et raison d'arret toujours honnetes.

Avant Thomas, Codex doit preparer et installer l'add-in courant, verifier ses
marqueurs et fournir uniquement la checklist Fusion restante. Le bundle reste
local, n'entraine aucune auto-modification et ne peut entrer dans le corpus
qu'apres anonymisation et revue.

Le projet personnel reste hors capacite de reconstruction automatisée a l'issue
de L05D2 ; la gate collecte une preuve de developpement, elle ne suppose pas sa
resolution.

Preparation reelle : add-in 0.1.58 et commit 261f7cc installes ; fixture
p64-l05v-global-void-baseline.bgig.json ecrite dans Documents/BGIG/projects.
Checklist : docs/P64_L05V_FUSION_GATE_CHECKLIST.md.
fusion-validated: false avant retour humain explicite.
print-validated: false.

## Retour P64-L05V - observation positive, preuve partielle (2026-07-22)

Thomas confirme le comportement de la fixture 0.1.58 installee depuis le commit 261f7cc : deux conteneurs sont proposes sur un etage, dont `Bac 888`, et le plan temoin est ecrit atomiquement. La palette declare `Recherche poursuivie : Oui` et `Cache revendique : Non`. L inspection de scene reste read-only et ne trouve aucune scene BGIG ; ce resultat est coherent avec une gate sans materialisation.

Cette observation valide humainement le mecanisme L05A dans la fixture et la premiere ecriture du witness. Elle ne constitue ni un test de capacite du solveur, ni une preuve que des volumes affiches suffisent a un nouveau placement, ni une revendication sur le projet personnel complexe.

Les traces recues indiquent `Warm start : non fourni` et `no_initial_incumbent`. Ce n est pas un echec : c est le premier calcul, anterieur a tout rechargement compatible. Elles ne prouvent donc pas encore le rechargement du witness. Aucun chemin de SolverCaseBundle DEV n est joint non plus. Ces deux observations restent ouvertes et ne sont pas promues en fusion-validated.

Prochaine preuve humaine minimale : recharger le meme projet apres un changement temporaire d effort et verifier un witness/warm start acceptes ; puis, sur `Mon insert.bgig.json`, capturer explicitement un SolverCaseBundle DEV apres une manipulation representative et transmettre seulement son chemin local et son digest pour anonymisation/revue.

Statut de gate : positif partiel ; L05V ne devient pas globalement fusion-validated. print-validated: false.

## P64-L05V-R1 - gate de recapture fidele

Statut : automated-validated, installation requise avant observation.

Les trois bundles du 2026-07-23 sont valides et utiles, mais la version installee au moment de leur capture a perdu le rapport exact de l insertion locale. Apres installation de R1, Thomas ne refait pas tout le parcours :

1. repartir du dernier plan certifie de Mon insert ;
2. ajouter le meme petit conteneur et cliquer DEV apres le refus affiche ;
3. lancer le calcul, puis cliquer DEV apres l echec ;
4. transmettre les deux chemins et digests.

Aucune materialisation ni impression n est requise. Aucun bundle n entre automatiquement dans le depot. fusion-validated: false avant ce retour ; print-validated: false.

Installation P64-L05V-R1 confirmee : add-in 0.1.58, commit e817432, marqueur et settings verifies. La gate de recapture est active ; Thomas ne doit executer que les quatre actions humaines listees ci-dessus.
## P64-L05V-R2 - remplacement de la recapture manuelle

Décision humaine du 2026-07-23 : la gate de recapture par bouton DEV est fermée et remplacée par ADR-0080.

La palette 0.1.59 journalise automatiquement chaque action utile et référence les états locaux dédupliqués. Thomas n'a plus à cliquer au bon instant, à produire une paire exacte ni à répéter des ajouts pour débloquer P64-L06.

Les captures déjà présentes restent des observations locales utiles mais ne sont pas promues automatiquement. Elles ne valent ni preuve géométrique générale, ni validation Fusion, ni validation d'impression.

Statut : aucune action humaine requise pour lancer ou poursuivre P64-L06. fusion-validated: false. print-validated: false.

## P64-L06E — clôture du premier Goal

La décision `no_algorithm_change_v1` ne demande aucune validation humaine : aucun comportement produit, géométrie, budget, certificat, Fusion ou scène ne change. P64-L06V reste une observation future facultative et ne bloque pas la clôture.

Statut : aucune action humaine requise. fusion-validated: false. print-validated: false.

## P64-L07 — lancement du benchmark externe

Décision humaine enregistrée le 2026-07-23 : Thomas veut comparer BGIG au
meilleur de ce qui est accessible et libre d'utilisation, puis intégrer le
meilleur moteur ou jusqu'à trois moteurs complémentaires si les mesures le
justifient.

La seule action humaine requise pour démarrer est d'envoyer `/goal` dans la
tâche de reprise P64-L07. Ce message vaut GO pour :

- la recherche officielle et l'audit d'au moins huit candidats ;
- l'acquisition isolée des candidats conformes ;
- le benchmark d'au moins trois concurrents externes distincts ;
- la création d'un corpus V2 et d'un nouveau holdout ;
- l'intégration d'un à trois gagnants conformes à ADR-0081.

Ne pas demander une seconde autorisation dans ce périmètre.

Une nouvelle gate humaine apparaît seulement si le meilleur candidat exige une
licence ambiguë ou incompatible, un composant propriétaire, un service distant,
une installation globale, un dépassement de l'enveloppe 36 h / 8 Gio ou une
extension T2-T4. Dans ce cas, conserver le résultat de benchmark sans intégrer
le composant concerné.

Le `/goal` a été reçu et L07A à L07E sont terminées historiquement. ADR-0083
requalifie toutefois ce résultat : les adapters L07 n'ont couvert qu'un modèle
de sol à un niveau. Aucun résultat L07 ne vaut décision sur le solvage 3D global.

Statut : L07 archivé comme benchmark partiel ; P64-L08 prend le relais.
fusion-validated: false. print-validated: false.

## P64-L07V — gate Fusion suspendue

ADR-0083 suspend cette observation. Elle ne mesurerait que la lane HiGHS de sol
et ne répondrait pas au besoin obligatoire de solvage 3D des cas limites.

Le GO explicite de Thomas du 2026-07-24 autorise P64-L08A à P64-L08G dans le
cadre du programme versionné. Une nouvelle gate humaine ne sera demandée qu'une
fois un portefeuille gagnant sur le corpus 3D réel prêt à observer dans Fusion.

Statut : `superseded-by-P64-L08`, aucune action Fusion demandée maintenant.
fusion-validated: false. print-validated: false.

## P64-L08F — SCIP retenu, gate Fusion encore fermée

Le holdout réel 3D a été ouvert une seule fois après sélection scellée. La
récupération du verdict n'a rouvert aucun secret et n'a rappelé aucun worker.
Le portefeuille est rejeté ; SCIP seul démontre 18 gains et 0 perte face au
comportement BGIG corrigé.

SCIP reste toutefois `benchmark-only` tant que la redistribution du paquet
Windows, de ses dépendances natives et de ses avis n'est pas entièrement
versionnée. P64-L08G peut fermer cette gate technique sans modifier le
benchmark. Thomas n'a aucune manipulation à faire avant une intégration
automatisée réussie et un package Fusion installé par Codex.

Statut : aucune gate humaine active maintenant. Une gate Fusion sera ouverte
uniquement si L08G intègre SCIP sans régression.
`fusion-validated=false`. `print-validated=false`.
