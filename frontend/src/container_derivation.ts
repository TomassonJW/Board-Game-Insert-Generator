import type { Dimension } from './types'

export type ContainerDerivationStatus = 'ready' | 'blocked' | 'pending_fill_resolution'

export interface DerivedCompartment {
  id: string
  content_id: string
  content_name: string
  shape_kind: string
  inner_dimensions_mm: Dimension
  quantity: {
    declared_count: number
    capacity_per_stack: number
    pile_count: number
    items_per_pile: number
    pile_grid_columns: number
    pile_grid_rows: number
    count_semantics: string
  }
  blockers: string[]
  warnings: string[]
}

export interface DerivedContainer {
  container_group_id: string
  container_name: string
  status: ContainerDerivationStatus
  source_content_ids: string[]
  inner_dimensions_mm: Dimension | null
  outer_dimensions_mm: Dimension | null
  compartments: DerivedCompartment[]
  blockers: string[]
  warnings: string[]
}

export interface ContainerDerivationPlan {
  schema_version: 'bgig.container_derivation.v1'
  containers: DerivedContainer[]
  summary: {
    status: 'ready_for_p40' | 'blocked'
    requested_container_count: number
    ready_container_count: number
    blocked_container_count: number
    pending_fill_container_count: number
    content_family_count: number
    content_item_count: number
  }
  blockers: Array<{
    container_group_id: string
    container_name: string
    message: string
  }>
  limitations: string[]
}
