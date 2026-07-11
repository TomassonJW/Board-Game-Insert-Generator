export type Axis = 'x' | 'y' | 'z'

export interface Dimension {
  x: number
  y: number
  z: number
}

export interface Point {
  x: number
  y: number
  z: number
}

export interface AssetDraft {
  id: string
  name: string
  kind: 'cards' | 'tokens' | 'dice' | 'meeples' | 'other'
  quantity: { count: number; grouping: string }
  dimensions_mm: Dimension
  containment_intent: 'store' | 'protect' | 'separate' | 'access_first'
  dimension_confidence: 'exact' | 'approximate'
}

export interface LayerDraft {
  id: string
  origin_z_mm: number
  height_mm: number
  role: string
}

export interface ReservationDraft {
  id: string
  kind: 'board' | 'rulebook' | 'existing_tray' | 'generic'
  origin_mm: Point
  size_mm: Dimension
  layer_id: string
}

export interface ManualModuleDraft {
  id: string
  name: string
  origin_mm: Point
  size_mm: Dimension
  layer_id: string
  locked: boolean
}

export interface CandidateDraft {
  id: string
  name: string
  size_mm: Dimension
  allowed_layers: string[]
  allow_xy_rotation: boolean
  priority: number
  asset_ids: string[]
}

export interface AppearanceDraft {
  schema_version: 'bgig.appearance.v0'
  shape: {
    corner_style: 'rounded' | 'straight' | 'chamfered'
    corner_radius_mm: number
    chamfer_mm: number
    notch_style: 'none' | 'front_scoop' | 'thumb_notch'
  }
  visual: {
    theme: 'atelier' | 'graphite' | 'playful'
    label_mode: 'none' | 'module_name' | 'module_name_and_role'
    typography: 'quiet' | 'bold'
  }
}
export interface MechanismDraft {
  schema_version: 'bgig.mechanism.v0'
  kind: 'none' | 'sliding_lid'
  slide_axis: 'x' | 'y'
  lid_thickness_mm: number
  rail_height_mm: number
  rail_clearance_mm: number
  end_overlap_mm: number
}
export interface ComposerDraft {
  schema_version: 'bgig.local_composer.v0'
  project_name: string
  box: {
    inner_dimensions_mm: Dimension
    usable_height_mm: number
    lid_clearance_mm: number
  }
  assets: AssetDraft[]
  layers: LayerDraft[]
  reservations: ReservationDraft[]
  manual_modules: ManualModuleDraft[]
  candidates: CandidateDraft[]
  preference: 'balanced' | 'compact' | 'accessible' | 'print_simple'
  appearance: AppearanceDraft
  mechanism: MechanismDraft
}
export interface StarterTemplate {
  id: string
  title: string
  description: string
  highlights: string[]
  draft: ComposerDraft
}

export interface EngineModule {
  id: string
  name: string
  origin_mm: Point
  size_mm: Dimension
  layer_id: string | null
  locked: boolean
  manual: boolean
  metadata?: Record<string, unknown>
}

export interface EngineReservation {
  id: string
  kind: string
  origin_mm: Point
  size_mm: Dimension
  layer_id: string | null
}

export interface Solution {
  status: 'solved' | 'partial' | 'blocked'
  solved_plan: {
    box: { inner_dimensions_mm: Dimension }
    layers: Array<{ id: string; origin_z_mm: number; height_mm: number; role: string }>
    reservations: EngineReservation[]
    modules: EngineModule[]
    warnings: Array<{ message?: string }>
  }
}

export interface Variant {
  id: string
  policy_id: string
  status: 'solved' | 'partial' | 'blocked'
  weighted_score: number
  subscores: Record<string, number>
  reasons: string[]
  recommended: boolean
  pareto: boolean
  solution: Solution
}

export interface Portfolio {
  schema_version: 'box_fill_variants.v0'
  source_plan_id: string
  preference: { id: string; weights: Record<string, number> }
  recommended_variant_id: string | null
  pareto_variant_ids: string[]
  portfolio_digest: string
  variants: Variant[]
  limits: string[]
}

export interface ExportBundle {
  schema_version: 'bgig.local_composer_export.v0'
  selection: { selected_variant_id: string; selected_by: string; variant: Variant; appearance?: AppearanceDraft; mechanism?: MechanismDraft }
  cad_ir: Record<string, unknown>
  limits: string[]
  appearance?: AppearanceDraft
  mechanism?: MechanismDraft
  mechanism_readiness?: Array<Record<string, unknown>>
}
