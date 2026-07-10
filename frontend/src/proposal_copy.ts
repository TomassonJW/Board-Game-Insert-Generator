export interface ProposalExplanation {
  title: string
  intent: string
  choose_if: string
  watch_for: string
}

const explanations: Record<string, ProposalExplanation> = {
  compact_origin: {
    title: 'Volume compact',
    intent: 'Rapproche les bacs pour garder une composition dense.',
    choose_if: 'tu veux limiter l espace disperse dans la boite.',
    watch_for: 'un bac peut etre moins immediat a atteindre.',
  },
  preserve_large_free_region: {
    title: 'Grand espace libre',
    intent: 'Tente de conserver une zone libre plus large et plus lisible.',
    choose_if: 'tu prevois un futur module, un sac ou un element variable.',
    watch_for: 'ce n est qu une heuristique, pas une garantie de volume utile.',
  },
  accessibility_front: {
    title: 'Acces frontal',
    intent: 'Favorise les modules qui se prennent facilement depuis le bord.',
    choose_if: 'tu veux sortir les elements frequents plus vite.',
    watch_for: 'la compacite peut etre moins prioritaire.',
  },
  minimal_rotation: {
    title: 'Rotation minimale',
    intent: 'Evite autant que possible de faire pivoter les bacs candidats.',
    choose_if: 'tu veux une lecture plus directe entre mesures et rangement.',
    watch_for: 'cela peut laisser moins de flexibilite au placement.',
  },
  balanced_footprint: {
    title: 'Empreinte equilibree',
    intent: 'Recherche un compromis borne entre densite, acces et espace libre.',
    choose_if: 'aucune priorite ne domine encore ton usage.',
    watch_for: 'ce n est pas une optimisation globale de la boite.',
  },
}

const scoreCopy: Record<string, string> = {
  compactness: 'Bacs rapproches dans la boite.',
  free_space: 'Espace non occupe rapporte.',
  accessibility: 'Facilite d acces estimee.',
  printability: 'Simplicite proxy pour l impression.',
  simplicity: 'Moins de compromis de placement.',
  coverage: 'Assets declares pris en compte.',
}

export function proposalExplanation(policyId: string): ProposalExplanation {
  return explanations[policyId] ?? {
    title: policyId,
    intent: 'Cette policy reste explicite dans les exports techniques.',
    choose_if: 'tu as verifie son plan et ses limites.',
    watch_for: 'son intention n est pas encore traduite dans le Studio.',
  }
}

export function scoreExplanation(scoreId: string): string {
  return scoreCopy[scoreId] ?? 'Indicateur de comparaison, pas une validation physique.'
}
