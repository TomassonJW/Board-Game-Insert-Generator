import type { VolumeClosurePlan } from './volume_closure'

export interface FunctionalCadBuild {
  schema_version: 'bgig.functional_cad_build.v1'
  status: 'planned_for_fusion_smoke' | 'impossible'
  volume_plan: VolumeClosurePlan
  cad_ir: Record<string, unknown> | null
  materialization: {
    status: string
    component_count: number
    container_component_count?: number
    hollow_fill_component_count?: number
    solid_component_count?: number
    cavity_count?: number
    skipped_regions: Array<{ region_id: string; classification: string; reason: string }>
  }
  blockers: string[]
  limitations: string[]
}
