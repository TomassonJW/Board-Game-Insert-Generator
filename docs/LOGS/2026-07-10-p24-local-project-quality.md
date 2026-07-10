# 2026-07-10 - P24 Qualite du projet local

## Mission

Rendre l edition d un projet local plus explicite sans changer le moteur, le schema V0 ou la frontiere Fusion.

## Livrables

- Module TypeScript de prevalidation et de filtrage structurel des imports.
- Liste d erreurs actionnables avant generation : dimensions, quantites, IDs, layers, types et allocations.
- Selection multi-assets par module candidat, avec prevention visuelle des allocations en doublon.
- Messages moteur plus lisibles dans l interface.

## Preuves

- Build TypeScript/Vite passe.
- Verification comportementale isolee : draft valide, import non structurel refuse, allocation manquante et doublon detectes.
- Test Python P24 : un candidat peut declarer cards + tokens et la sortie P21 transporte les deux allocations dans le plan resolu.

## Limites

- La prevalidation aide l utilisateur mais ne remplace pas le moteur.
- Aucun schema incompatible, solveur, cloud, persistence serveur, Fusion ou export imprimable.
- L inspection navigateur reste a rejouer lorsque le runtime local sera disponible.