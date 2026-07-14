# P69 - Revue humaine UI/UX exhaustive apres V0.3

Statut : `blocked-by-p50`, `human-review-required`, `no-runtime-change`.

## Objectif

P69 est la revue complete, tres commentee et evidencee de l experience BGIG
apres livraison des formes/ergonomies P44-P46 et des couvercles/calibrations
P47-P50. Elle ne corrige rien dans la meme mission. Elle cadre les versions
ulterieures a partir d un produit fonctionnellement plus riche et de vrais usages.

## Preconditions

- P66 accepte comme MVP Fusion-only ;
- P67 termine et priorites V0.2/V0.3 documentees ;
- P46 accepte dans Fusion ;
- P50 termine avec statut physique honnete ;
- retours P68 disponibles quand des impressions ont ete realisees ;
- commit, package, projets et profils d impression identifies.

## Methode de revue

La revue doit etre realisee dans Fusion sur plusieurs profils d usage : premier
projet, projet existant, petit jeu, grande cardinalite, plateaux/livrets,
multi-etages, formes ergonomiques et couvercles. Chaque observation est reliee a
une capture, une etape, un attendu et un impact utilisateur.

Elle couvre au minimum :

1. decouverte, installation, launcher, taille et reprise de palette ;
2. vocabulaire, ordre du parcours et comprehension novice ;
3. densites Compact/Detaille et efficacite expert ;
4. saisie, presets, import/export, erreurs et recuperation ;
5. plateaux, orientations, conteneurs, tolerances et multi-etages ;
6. preview, score, appuis, retraits, formes, ergonomies et couvercles ;
7. materialisation, regeneration, scene, export et reprise apres erreur ;
8. clavier, focus, contrastes, lisibilite et petites/grandes palettes ;
9. coherence entre valeurs source, derivees, calculees et materialisees ;
10. charge cognitive, actions rares, aide contextuelle et details techniques.

## Classification

Chaque observation recoit :

- severite : bloquant, important, amelioration ou question ;
- profil touche : novice, intermediaire, expert ou tous ;
- frequence et reproductibilite ;
- valeur utilisateur ;
- cout/risque technique estime ;
- capability et version cible ;
- preuve : capture, projet, message, mesure ou video courte.

## Livrable humain

`docs/P69_FULL_UI_UX_REVIEW_REPORT.md` contient :

- matrice ecran x tache x profil ;
- journal commente des parcours ;
- captures annotees ;
- irritants et points forts ;
- dette de vocabulaire et d architecture d information ;
- dette d accessibilite ;
- top priorites valeur/effort/risque ;
- propositions de lots P70+ ;
- sujets explicitement refuses ou reportes ;
- decision humaine d ouverture de la version suivante.

## Articulation avec la fondation UX anticipee

La revue P67 du 2026-07-14 peut autoriser une fondation UX bornee dans P44
avant les geometries P45 : stabilite de saisie, densite, architecture
d information, cycle document et traduction des concepts. Cette passe corrige
un risque de construction ; elle ne remplace pas P69.

P69 reste la revue exhaustive du produit enrichi apres P50. Elle reexamine les
choix P44 sur plusieurs profils, les vraies formes, les couvercles, les retours
P68, l accessibilite et les parcours complets. Elle peut donc confirmer,
corriger ou remettre en cause la fondation avec des preuves plus riches.

## Sortie

P69 ne modifie aucun statut de capability par lui-meme. Il produit un backlog
priorise et, si necessaire, des ADR proposees. Aucun P70+ ne devient `ready`
avant validation humaine du rapport.

## Interdits

- corriger l UI pendant la revue ;
- confondre preference esthetique et defaut fonctionnel ;
- supprimer le mode expert pour simplifier artificiellement ;
- deduire une validation physique d une capture Fusion ;
- ouvrir plusieurs refontes structurantes sans lots et ADR separes.
