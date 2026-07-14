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
| P67 - Priorisation post-MVP | P66 OK, retours d usage disponibles si existants et contrat P67 prepare | Arbitrage humain du sous-scope, de l ordre P44-P50, des preuves et du devenir des complements | Peut rendre P44-M001 ready |
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

P67 est maintenant `ready` pour la priorisation humaine post-MVP. Il peut seul
rendre P44-M001 `ready`; P44-P50 restent bloques jusque-la. P68 demeure une
boucle de retours volontaires `planned-after-p66`. Aucun tag ou release n est
autorise par cette gate seule.
