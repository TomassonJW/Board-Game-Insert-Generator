import type { ComposerDraft, Dimension } from './types'

export type ProjectShapeKind = 'round' | 'square' | 'rectangle' | 'cards' | 'cube' | 'meeple' | 'custom'
export type FlatItemKind = 'board' | 'rulebook' | 'other'
export type FillElementKind = 'hollow' | 'solid' | 'separator'
export type SolverPreference = 'balanced' | 'compact' | 'accessible' | 'print_simple'

export interface ContainerGroupDraft {
  id: string
  name: string
  wall_thickness_mm: number | null
  floor_thickness_mm: number | null
}

export interface ProjectContentDraft {
  id: string
  name: string
  shape_kind: ProjectShapeKind
  dimensions_mm: Dimension
  quantity: number
  container_group_id: string
  content_clearance_mm: number | null
  measurement_confidence: 'exact' | 'approximate'
}

export interface FlatItemDraft {
  id: string
  name: string
  kind: FlatItemKind
  dimensions_mm: Dimension
  quantity: number
  stack_order: number | null
}

export interface FillElementDraft {
  id: string
  name: string
  kind: FillElementKind
  mode: 'auto' | 'exact'
  dimensions_mm: Dimension | null
  container_group_id: string | null
}

export interface ProjectV1Draft {
  schema_version: 'bgig.project.v1'
  project_name: string
  box: {
    inner_dimensions_mm: Dimension
    usable_height_mm: number
    lid_clearance_mm: number
  }
  layout: {
    layout_clearance_mm: number
    default_wall_thickness_mm: number
    default_floor_thickness_mm: number
    default_content_clearance_mm: number
  }
  contents: ProjectContentDraft[]
  container_groups: ContainerGroupDraft[]
  flat_items: FlatItemDraft[]
  fill_elements: FillElementDraft[]
  solver_preference: SolverPreference
  deferred_features: {
    appearance: Record<string, unknown> | null
    mechanism: Record<string, unknown> | null
  }
  migration?: {
    source_schema: string
    legacy_snapshot: Record<string, unknown>
  }
}

export interface ProjectNormalization {
  project: ProjectV1Draft
  source_schema: ProjectV1Draft['schema_version'] | ComposerDraft['schema_version']
  migrated: boolean
}
