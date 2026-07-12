import type { ContainerDerivationPlan } from './container_derivation'
import type { Dimension } from './types'

export interface FlatStackItem {
  id: string
  name: string
  kind: 'board' | 'rulebook' | 'other'
  quantity: number
  stack_order: number | null
  physical_size_mm: Dimension
  total_thickness_mm: number
  stack_origin_z_mm: number
}

export interface FlatStackReservationPlan {
  schema_version: 'bgig.flat_stack_reservation.v1'
  container_plan: ContainerDerivationPlan
  flat_stack: {
    status: 'not_required' | 'reserved' | 'blocked'
    reservation_clearance_mm: number
    physical_footprint_mm: Dimension | null
    reservation_size_mm: Dimension | null
    storage_height_mm: number
    items: FlatStackItem[]
  }
  support_requirement: {
    status: 'not_required' | 'blocked' | 'area_budget_sufficient_pending_placement' | 'support_extension_required'
    required_footprint_mm: Dimension | null
    required_area_mm2: number
    candidate_container_top_area_mm2: number
    note: string
  }
  summary: {
    status: 'ready_for_p41' | 'blocked'
    flat_family_count: number
    flat_copy_count: number
    storage_height_mm: number
    ready_container_count: number
    blocked_container_count: number
  }
  blockers: string[]
  limitations: string[]
}
