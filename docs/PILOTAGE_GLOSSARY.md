# Glossaire de pilotage BGIG

Derniere mise a jour : 2026-07-14.

## Identifiants P, M, V et H

Le depot n avait pas defini de developpement lexical normatif de `Pxx`.
Historiquement, `P` numerote une phase ou un lot de pilotage stable. Ce n est
ni un numero de version, ni une priorite, ni un ordre Git. Pour lever
l ambiguite, la lecture canonique devient :

- `Pxx` : **phase ou lot de pilotage** ; exemple `P67` ;
- `Pxx-Myyy` : **mission atomique** dans ce lot ; exemple `P66-M000` ;
- `Pxx-V` ou `Pxx-MyyyV` : **validation humaine** d un lot ou d une mission ;
- `Pxx-Hyy` : **hotfix borne** ouvert par un ecart de gate ;
- `C-*` : **capability**, donc aptitude produit ou technique durable ;
- `M*` sans prefixe `P` dans `CAPABILITY_MAP` : **milestone de capability**.

Le `xx` de `Pxx` est un identifiant historique. Il ne faut donc pas deduire
que P44 s execute avant P67. Les dependances, le statut `ready` et les gates
portent l ordre reel.

## Roadmap et backlog

### Roadmap

La roadmap decrit la trajectoire macro : resultats produit, versions, ordre des
grands lots, dependances et gates. Elle repond surtout a :

- ou va le produit ;
- pourquoi cette sequence ;
- quels resultats sont attendus avant de passer a la version suivante ;
- quelles frontieres ne doivent pas etre franchies trop tot.

Elle ne doit pas devenir une liste exhaustive de micro-taches.

### Backlog

Le backlog est l inventaire actionnable du travail. Il transforme la trajectoire
en cartes suffisamment bornees pour etre executees une par une. Une carte utile
precise objectif, capability, dependances, livrable, criteres d acceptation,
tests, gate et statut.

Il repond surtout a :

- quel travail concret existe ;
- quelle carte est `ready`, `blocked`, `done` ou `deferred` ;
- comment prouver qu une mission est terminee ;
- quels risques ou travaux futurs ont ete decouverts.

### Regle pratique

Une nouvelle idee ne modifie pas automatiquement les deux documents :

- si elle change l ordre des versions ou la promesse d un lot, mettre a jour la
  roadmap et le backlog ;
- si elle ajoute seulement une tache dans une trajectoire deja acceptee, mettre
  a jour le backlog ;
- si elle change une decision structurante, proposer aussi une ADR ;
- si elle decrit seulement un fait observe, mettre a jour STATUS ou un rapport
  de gate ;
- si elle change la prochaine action immediate, mettre a jour NEXT_ACTIONS.

L utilisateur n a pas besoin de demander systematiquement « roadmap et
backlog ». L instruction « integre ce retour au pilotage produit » autorise
l agent a choisir et synchroniser les artefacts necessaires selon ces regles.

## Roles des principaux documents

| Document | Question a laquelle il repond | Ce qu il ne remplace pas |
| --- | --- | --- |
| `NORTH_STAR.md` | Quelle valeur finale cherche-t-on ? | Une specification de mission |
| `CANONICAL_PRODUCT_VISION.md` | Quelles promesses par version ? | Le statut reel |
| `ROADMAP.md` | Dans quel ordre macro avance-t-on ? | Les taches atomiques |
| `BACKLOG.md` | Quelles cartes sont a faire et comment les accepter ? | La preuve courante |
| `NEXT_ACTIONS.md` | Quelle est l unique prochaine action recommandee ? | Le backlog complet |
| `STATUS.md` | Qu est-ce qui est reellement implemente et prouve ? | Une intention future |
| `CAPABILITY_MAP.md` | Quelles aptitudes produit sont servies et a quel niveau ? | L ordre detaille des missions |
| `HUMAN_GATES.md` | Quelles decisions ou observations restent humaines ? | Les tests automatises |
| `DECISIONS/ADR-*` | Pourquoi une decision structurante a-t-elle ete prise ? | Une liste de taches |
| `LOGS/*` | Quel changement significatif date faut-il transmettre ? | Le statut canonique |

## Termes utiles pour formuler une demande

Selon le resultat souhaite, les formulations suivantes sont plus precises :

- « Transforme cette vision en capabilities, epics et missions testables. »
- « Integre ce retour au cadrage produit et au backlog, sans implementation. »
- « Mets a jour la trajectoire si l ordre des versions change. »
- « Propose les options d architecture et ouvre les decisions, sans les
  accepter a ma place. »
- « Redige le contrat fonctionnel et les criteres d acceptation du prochain
  lot. »
- « Fais une revue UX heuristique » pour une analyse experte sans utilisateurs.
- « Fais un test d utilisabilite » quand un humain execute des taches observees.
- « Fais une recette fonctionnelle » pour verifier un contrat deja defini.
- « Fais une revue de gate » pour decider si la version suivante peut commencer.

## Hierarchie de travail recommandee

La hierarchie BGIG reste volontairement simple :

1. vision produit ;
2. version ou outcome de roadmap ;
3. capability concernee ;
4. lot `Pxx` ;
5. mission atomique `Pxx-Myyy` ;
6. criteres d acceptation et tests ;
7. gate humaine si necessaire ;
8. preuve dans STATUS et les logs.

Un « epic » peut etre utilise comme regroupement de backlog, mais ne doit pas
ajouter un deuxieme systeme d identifiants si un lot `Pxx` remplit deja ce role.
