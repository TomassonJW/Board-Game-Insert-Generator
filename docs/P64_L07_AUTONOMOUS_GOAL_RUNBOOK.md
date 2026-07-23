# P64-L07 — runbook du Goal de benchmark externe

## 1. Rôle et statut

Ce runbook exécute le vrai benchmark externe décidé par ADR-0081.

Statut avant lancement : `ready-for-explicit-go`.

Le lancement `/goal` de Thomas dans la tâche de reprise vaut GO pour toute la
séquence L07A à L07E. Ne pas redemander une seconde autorisation pour une
recherche, un téléchargement isolé, un benchmark ou une intégration déjà
couvert par ce document.

## 2. Résultat final exigé

Le Goal est terminé seulement si :

- au moins huit candidats ont été audités ;
- au moins trois candidats externes réellement distincts ont été adaptés et
  mesurés ;
- un nouveau holdout indépendant a été créé et ouvert une seule fois ;
- le meilleur choix a été mesuré contre BGIG et les autres candidats ;
- un gagnant, ou jusqu'à trois gagnants complémentaires, a été intégré si les
  gates produit sont satisfaites ;
- un rapport négatif explicite est produit si aucun candidat n'est intégrable.

Une campagne avec trois réglages internes ou moins de trois concurrents externes
ne satisfait pas ce Goal.

## 3. Préflight bloquant

Avant toute écriture :

1. lire `AGENTS.md`, `PILOTAGE_CURRENT.md`, `NEXT_ACTIONS.md`,
   `HUMAN_GATES.md`, `AUTONOMY_PROTOCOL.md`, ADR-0068, ADR-0079, ADR-0081,
   le programme P64 multi-solveurs et le programme P64-L07 ;
2. vérifier le worktree dédié, `HEAD`, `origin/main`, le dernier commit et
   `HEAD...origin/main` ;
3. vérifier que le worktree est propre et ne toucher à aucun autre worktree ;
4. créer une branche `codex/p64-l07a-*` depuis `origin/main` ;
5. vérifier les outils déjà présents avant tout téléchargement ;
6. créer les fichiers temporaires uniquement sous `.codex-work/p64-l07/`.

Un écart Git, une modification étrangère ou un conflit est un arrêt, pas une
invitation à nettoyer un autre travail.

## 4. Enveloppe globale

- Durée maximale du premier Goal : 36 heures écoulées.
- Espace temporaire maximal : 8 Gio sous `.codex-work/p64-l07/`.
- Concurrence : au plus deux processus lourds ; les mesures comparatives fixent
  explicitement le nombre de threads par candidat.
- Réseau : autorisé seulement pour consulter les sources officielles et
  acquérir les versions auditées.
- Exécution produit : entièrement hors ligne.
- Installation : environnement isolé dans le workspace, jamais globale.
- Données personnelles : aucune promotion automatique.
- Rapports à Thomas : français courant, résultat et prochaine action d'abord.

Le plafond est global. Une étape coûteuse est précédée des filtres de licence,
de plateforme et d'adéquation pour ne pas brûler du calcul sur un candidat déjà
inintégrable.

## 5. Sources et traçabilité

Pour chaque source téléchargée, enregistrer avant exécution :

- URL officielle ;
- version, tag ou commit ;
- date de consultation ;
- SHA-256 de l'archive ou du binaire ;
- licence principale et licences transitives ;
- méthode de reproduction ;
- destination isolée.

Ne pas exécuter un binaire sans source officielle, empreinte ou licence claire.
Ne jamais télécharger depuis un miroir aléatoire lorsqu'un dépôt ou une version
officielle existe.

## 6. Mission P64-L07A — recherche et sélection

1. inventorier au moins huit candidats ;
2. couvrir solveur spécialisé, contraintes/SAT, nombres entiers et au moins une
   approche exacte ou hybride crédible ;
3. vérifier les licences et les composants optionnels ;
4. vérifier Windows, hors ligne, interface automatisable, délais et mémoire ;
5. estimer la perte de modèle pour rotations, réservations, niveaux et variantes
   P45 ;
6. retenir au moins trois candidats externes distincts ;
7. livrer l'audit et la décision avant toute compilation lourde ;
8. tester, committer, intégrer dans `main`, pousser et vérifier le SHA distant.

Si moins de trois candidats passent, arrêter le Goal comme incomplet avec les
raisons exactes. Ne pas abaisser silencieusement le minimum.

## 7. Mission P64-L07B — corpus V2

1. conserver les régressions utiles de L05D1/L06 ;
2. générer de nouveaux cas BGIG couvrant toutes les familles obligatoires ;
3. ajouter au moins deux sources publiques 3D indépendantes quand leur licence
   le permet, ou un téléchargeur à empreinte si les données ne sont pas
   redistribuables ;
4. documenter la correspondance exacte entre chaque objectif public et BGIG ;
   exclure du classement produit tout cas qui exige de perdre une contrainte ;
5. séparer les familles, projets et graines entre les splits ;
6. créer un nouveau holdout inconnu des étapes de réglage ;
7. sceller manifest, recettes, sources et holdout par digest ;
8. vérifier témoins faisables et preuves négatives ;
9. ne lancer aucun candidat sur le holdout ;
10. tester, committer, intégrer dans `main`, pousser et vérifier le SHA distant.

Le holdout L06 consommé ne peut apparaître que comme archive ou régression
ouverte, jamais comme arbitre final.

## 8. Mission P64-L07C — adapters

1. installer chaque candidat retenu dans son environnement isolé ;
2. verrouiller version, source, licence et empreinte ;
3. convertir l'entrée BGIG sans supprimer de contrainte ;
4. signaler `unsupported` si le modèle ne représente pas le cas ;
5. normaliser statuts, temps, mémoire, threads, graine et placement ;
6. reconstruire chaque placement positif ;
7. recertifier avec le certificat BGIG courant ;
8. contrôler les statuts sur les petits cas exacts ;
9. couvrir au moins trois candidats externes ;
10. tester, committer, intégrer dans `main`, pousser et vérifier le SHA distant.

Les dépendances expérimentales et leurs caches restent hors Git. Seuls les
adapters, verrous reproductibles, avis permis et preuves entrent dans le dépôt.

## 9. Mission P64-L07D — tournoi progressif

Exécuter strictement :

1. petits contrôles exacts ;
2. régressions ;
3. discovery pour tous les candidats ;
4. élimination des sorties invalides, candidats dominés ou coûts
   disproportionnés ;
5. tuning borné, avec un nombre d'essais annoncé et identique dans son principe ;
6. comparaison du meilleur candidat seul et des portefeuilles complémentaires ;
7. sélection scellée avant holdout ;
8. ouverture unique du nouveau holdout ;
9. soak seulement si une instabilité observée le justifie.

Mesurer au minimum :

- cas représentables ;
- cas certifiés résolus ;
- erreurs et résultats invalides ;
- qualité selon les scores BGIG existants ;
- temps au premier résultat certifié ;
- temps total et CPU ;
- mémoire maximale ;
- coût de démarrage ;
- taille et coût de distribution.

Un portefeuille est comparé sous une enveloppe totale comparable au meilleur
moteur seul. Conserver tous les résultats, checkpoints et digests nécessaires à
une reprise sans double exécution.

## 10. Choix avant holdout

Le fichier de sélection scellé contient :

- candidat principal ;
- éventuels candidats complémentaires ;
- routeur défini à partir des caractéristiques d'entrée seulement ;
- familles attribuées à chaque moteur ;
- enveloppe totale ;
- raisons de rejet des autres candidats ;
- digest du code, du corpus ouvert et des réglages.

Après scellement, aucun réglage, candidat ou routeur ne change. Une anomalie
invalide le holdout ; elle ne se corrige pas en regardant ses réponses.

## 11. Mission P64-L07E — intégration

1. intégrer le gagnant principal s'il passe toutes les gates ;
2. intégrer un deuxième ou troisième gagnant seulement pour un gain distinct,
   répété et rentable ;
3. créer une ADR factuelle par dépendance produit ;
4. verrouiller version, empreinte, licence et avis ;
5. valider installation, démarrage, arrêt, délai et fonctionnement hors ligne ;
6. valider le fallback si le moteur manque, échoue ou dépasse sa limite ;
7. conserver les statuts honnêtes et le certificat commun ;
8. comparer le produit intégré à la baseline sous ressources équivalentes ;
9. lancer la suite complète et les vérifications de packaging pertinentes ;
10. publier le rapport final ;
11. committer, intégrer dans `main`, pousser et vérifier le SHA distant.

Si un candidat gagne en laboratoire mais ne passe pas licence, packaging,
sécurité ou fallback, il reste `benchmark-winner-not-integrated`.

## 12. Gate d'acceptation finale

Une intégration est acceptée seulement si :

- aucune régression fonctionnelle ;
- aucune sortie positive non certifiée ;
- gain répété sur tuning et nouveau holdout ;
- contraintes BGIG explicitement couvertes ou refusées ;
- enveloppe totale respectée ;
- fonctionnement hors ligne sous Windows ;
- licence et redistribution vérifiées ;
- source et version reproductibles ;
- coût de maintenance documenté ;
- fallback BGIG testé.

Un portefeuille de deux ou trois candidats doit aussi battre le meilleur
candidat seul et justifier chaque membre par une famille distincte.

## 13. Checkpoints et reprise

Après chaque unité coûteuse, écrire atomiquement :

- entrée et digest ;
- candidat et version ;
- commande logique et limites ;
- statut de fin ;
- résultat et certificat ;
- temps, CPU, mémoire et threads ;
- prochaine unité.

Au redémarrage, vérifier les digests et reprendre l'unité suivante. Ne jamais
relancer une unité valide. Une unité interrompue sans résultat atomique peut être
rejouée une fois.

## 14. Arrêts obligatoires

Arrêter et faire un rapport si :

- trois candidats externes conformes ne peuvent pas être réunis ;
- une licence ou un binaire reste douteux ;
- une dépendance demande un compte, un service ou une installation globale ;
- le holdout est contaminé ;
- une régression ne peut pas être corrigée dans le lot ;
- les 36 heures ou 8 Gio sont atteintes ;
- une sortie externe contourne le certificat ;
- Git diverge, un conflit apparaît ou `main` ne peut pas être poussé.

Une pause sûre conserve le travail intégré des missions précédentes.

## 15. Frontières absolues

- T0/T1 seulement.
- Aucune forme T2-T4.
- Aucun changement silencieux de budget, deadline, certificat, schéma,
  tolérance, géométrie, propriété P45/P64, finalisation, CAD, scène, manifest ou
  valeur physique.
- Aucun service distant, secret, compte ou télémétrie.
- Aucune auto-modification.
- Aucune nouvelle revendication dense 11 × 34 sans mesure P64-L07.
- `fusion-validated: false` et `print-validated: false` sans preuve dédiée.

## 16. Rapport final minimal

Le rapport final donne en français courant :

- les candidats examinés et les raisons de tri ;
- les trois concurrents minimum réellement testés ;
- les corpus et limites ;
- le tableau de résultats ;
- le choix avant holdout ;
- le résultat du holdout ;
- le ou les moteurs intégrés ;
- les licences, tailles et coûts ;
- les tests et SHA intégrés ;
- les limites restantes.

## 17. Prompt `/goal` canonique

> Exécute le programme P64-L07 défini par ADR-0081,
> `P64_L07_OPEN_SOLVER_TOURNAMENT_PROGRAM.md` et ce runbook. Cherche d'abord
> largement les meilleures solutions libres d'utilisation et accessibles.
> Audite au moins huit candidats et compare réellement au moins trois moteurs
> externes distincts ; BGIG et l'oracle interne ne comptent pas dans ces trois.
> Crée un corpus V2 avec sources publiques et BGIG, un nouveau holdout fermé et
> des adapters qui recertifient toutes les sorties. Exécute le tournoi
> progressif sous ressources comparables. Intègre le meilleur moteur et jusqu'à
> deux compléments seulement si chacun gagne une famille distincte et si le
> portefeuille bat le meilleur moteur seul. Travaille une mission atomique à la
> fois, avec tests, preuve, commit, intégration directe dans main, push et SHA
> distant avant la suivante. Ne redemande pas de GO. Respecte 36 h, 8 Gio,
> T0/T1, le fonctionnement hors ligne, les licences, les checkpoints et toutes
> les frontières du runbook. Un résultat négatif honnête est préférable à une
> fausse victoire, mais moins de trois concurrents externes ne constitue pas un
> benchmark terminé.
