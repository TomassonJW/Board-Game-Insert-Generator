# P44-M007H01 - Focus stable, cartes explicites et conteneurs repliables

Date : 2026-07-16

Le package 0.1.37 a reçu un retour humain KO sur la saisie rapide. Autosave,
validation et solve rendaient chacun toute la palette ; la reconstruction des
champs retirait le focus, la sélection et parfois la position de saisie.

Le package 0.1.38 conserve le calcul adaptatif mais sépare ses réponses du DOM
éditable. Les statuts et l’Aperçu se mettent à jour en arrière-plan ; les faits
calculés de la zone de saisie sont peints de façon ciblée et différés jusqu’à ce
qu’aucun champ éditable ne soit actif. Les rendus complets restent réservés aux
changements structurels.

Les cartes exposent une Méthode de mesure en première ligne. Le mode Épaisseur
paquet affiche Z seul ; le mode Épaisseur carte × nb affiche Qté et Épaisseur
carte sans Z. Activer les sleeves propose 2,0 mm pour le delta commun X/Y et
0,08 mm pour le delta Z par carte. Ces champs sont optionnels : les anciens
projets sans overrides conservent le catalogue historique.

Les conteneurs deviennent des sections repliables indépendantes. Leur en-tête
complet reste visible et seuls les assets sont masqués.

Preuves : 481 tests, syntaxe JavaScript, tests ciblés, parse PowerShell, dry-run
du préparateur de gate, compileall, exemple CLI, frontière adsk et diff-check.
P44-M007H01V est préparée pour le package 0.1.38. fusion-validated: false ;
print-validated: false.
