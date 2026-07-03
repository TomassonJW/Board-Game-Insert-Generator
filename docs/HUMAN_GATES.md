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

## Gates obligatoires

| Gate | Pourquoi elle existe | Ce que Codex peut preparer seul | Validation humaine | Rapport attendu |
| --- | --- | --- | --- | --- |
| Changement de North Star | La North Star protege la direction produit long terme. | Analyse d'ecart, options, impacts roadmap. | Accepter, refuser ou reformuler la nouvelle direction. | Contexte, ancienne formulation, nouvelle formulation, impacts. |
| Changement d'architecture majeure | Une architecture engage maintenance, tests et evolutivite. | ADR proposee, comparaison des options, prototype limite. | Choisir l'option et accepter les consequences. | ADR complete avec alternatives refusees. |
| Changement du modele de tolerance | Les tolerances influencent la validite physique des inserts. | Analyse des cas, tests abstraits, tableau de valeurs. | Accepter la strategie et les valeurs par defaut. | Raison, valeurs, risques d'impression, plan de calibration. |
| Ajout de dependance lourde ou service externe | Les dependances augmentent cout, risque et complexite. | Justification, alternatives standard library, cout maintenance. | Autoriser la dependance et son perimetre. | Nom, usage, alternatives, plan de retrait. |
| Premiere integration Fusion 360 | Fusion ne doit pas aspirer la logique metier. | Rapport de readiness, contrat intermediaire, plan d'adaptateur. | Autoriser le debut de l'adaptateur. | Etat du moteur, tests, limites, surface Fusion ciblee. |
| Premiere generation Fusion exploitable | Une generation visible peut etre confondue avec une validation produit. | Script ou maquette, captures, verifications dimensionnelles. | Declarer le jalon comme accepte ou experimental. | Config source, sortie observee, ecarts, limites. |
| Premier export STL/3MF | Un export imprimable engage le passage vers fabrication. | Plan d'export, fichiers tests locaux, checklist slicer. | Autoriser le format et les criteres minimaux. | Fichier, dimensions, warnings, tests realises. |
| Premiere impression 3D reelle | L'impression valide des hypotheses physiques non automatisables. | Coupon de test, protocole, tableau de mesure. | Confirmer les mesures et l'interpretation. | Imprimante, filament, slicer, photos ou notes, resultats. |
| Modification des valeurs de tolerance par defaut | Les valeurs par defaut affectent tous les utilisateurs. | Donnees de calibration, comparaison avant/apres, tests. | Accepter les nouvelles valeurs. | Anciennes valeurs, nouvelles valeurs, preuves, risques. |
| Passage aux modules composites | Les unions internes changent le modele geometrique. | Specification, tests de faces internes, ADR si necessaire. | Valider le modele et le premier scope. | Cas supportes, cas refuses, invariants, tests. |
| Passage aux couvercles, charnieres, mecanismes | Les mecanismes demandent des jeux fonctionnels reels. | Etude, representation abstraite, protocole de test. | Choisir les mecanismes autorises. | Type de mecanisme, jeux, risques, validation physique requise. |
| Decision esthetique structurante | L'esthetique ne doit pas casser fonction et modularite. | Options visuelles, contraintes epaisseur, impact CAD. | Choisir le langage visuel ou le reporter. | Intentions, options, contraintes, regles parametriques. |
| Suppression ou refonte massive de fichiers existants | Les refontes peuvent detruire le contexte autopilotable. | Inventaire, plan de migration, diff cible. | Autoriser le perimetre exact. | Fichiers touches, raison, rollback, tests. |
| Publication de release | Une release cree une promesse utilisateur. | Checklist, changelog, tests, limites connues. | Autoriser version, notes et publication. | Version, contenu, statuts, validations, risques. |
| Changement de licence ou de visibilite repo | Cela change les droits, obligations et exposition publique. | Inventaire, impacts, options. | Choisir licence ou visibilite. | Etat actuel, option proposee, consequences. |

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
