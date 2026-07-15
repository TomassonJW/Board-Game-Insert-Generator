# Journal P44-M006 — cycle de document et diagnostic

Date : 2026-07-15
Statut : implémenté, validation automatisée et gate Fusion à effectuer.

P44-M006 ajoute un cycle de document nommé à la palette Fusion : Nouveau,
Ouvrir, Enregistrer sous, Enregistrer, récents bornés et récupération locale
atomique. Les dialogues de fichiers restent dans l’adaptateur Fusion ; le bridge
et le cœur restent sans adsk.

Les réglages essentiels sont visibles avec des intitulés français explicités.
La hauteur de conception est désormais seulement dérivée : hauteur intérieure Z
moins le jeu sous le couvercle. L’ancien champ utilisable reste toléré par la
normalisation historique mais n’est plus une commande normale.

Les outils Inspecter et Effacer la scène sont regroupés dans un diagnostic
replié ; Effacer demande confirmation. Aucun calcul, aucune matérialisation et
aucune scène Fusion ne se déclenchent par la récupération.

Hors périmètre : changement de schéma, solveur, tolérances, géométrie, CAD IR,
compléments, impression, P44-M007, P44-M008 et P44-M009.
