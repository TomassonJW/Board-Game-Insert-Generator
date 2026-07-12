import type { ContainerDerivationPlan } from './container_derivation'
import type { Dimension } from './types'

export interface VolumeClosurePlan {
  schema_version: 'bgig.volume_closure.v1'
  container_plan: ContainerDerivationPlan
  reservations: Array<{ id: string; kind: string; origin_mm: Dimension; size_mm: Dimension; printable: false }>
  placements: Array<{ id: string; name: string; origin_mm: Dimension; size_mm: Dimension; rotated_xy: boolean; printable: true }>
  free_regions: Array<{ id: string; origin_mm: Dimension; size_mm: Dimension; classification: string; printable: boolean }>
  support: { status: string; note: string }
  validation: { no_collisions: boolean; volume_conserved: boolean; classified_free_volume_mm3: number }
  summary: { status: 'constructed_plan' | 'impossible'; placed_container_count: number; reservation_count: number; classified_free_region_count: number; hollow_fill_candidate_count: number; solid_fill_candidate_count: number }
  blockers: string[]
}
