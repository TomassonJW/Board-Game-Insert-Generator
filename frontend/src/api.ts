import type { ComposerDraft, ExportBundle, Portfolio, StarterTemplate } from './types'
import type { ContainerDerivationPlan } from './container_derivation'
import type { FlatStackReservationPlan } from './flat_stack_reservation'
import type { ProjectNormalization, ProjectV1Draft } from './project_v1'

const apiBase = import.meta.env.VITE_BGIG_API_URL ?? 'http://127.0.0.1:8001/api'

class ApiError extends Error {
  constructor(message: string, readonly code?: string) {
    super(message)
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  const payload = await response.json().catch(() => null) as { error?: { code?: string; message?: string } } | null
  if (!response.ok) {
    throw new ApiError(payload?.error?.message ?? `Erreur API (${response.status})`, payload?.error?.code)
  }
  return payload as T
}

export async function loadStarters(): Promise<StarterTemplate[]> {
  const result = await request<{ starters: StarterTemplate[] }>('/starters')
  return result.starters
}

export async function loadProjectV1Starter(): Promise<ProjectV1Draft> {
  const result = await request<{ project: ProjectV1Draft }>('/project-v1/starter')
  return result.project
}

export async function normalizeProjectV1(project: ProjectV1Draft | ComposerDraft): Promise<ProjectNormalization> {
  return request<ProjectNormalization>('/project-v1/normalize', {
    method: 'POST',
    body: JSON.stringify(project),
  })
}

export async function deriveContainers(project: ProjectV1Draft): Promise<ContainerDerivationPlan> {
  return request<ContainerDerivationPlan>('/project-v1/derive-containers', {
    method: 'POST',
    body: JSON.stringify(project),
  })
}

export async function reserveFlatStack(project: ProjectV1Draft): Promise<FlatStackReservationPlan> {
  return request<FlatStackReservationPlan>('/project-v1/reserve-flat-stack', {
    method: 'POST',
    body: JSON.stringify(project),
  })
}

export async function generatePortfolio(draft: ComposerDraft): Promise<Portfolio> {
  const result = await request<{ portfolio: Portfolio }>('/portfolio', {
    method: 'POST',
    body: JSON.stringify(draft),
  })
  return result.portfolio
}

export async function createExport(draft: ComposerDraft, variantId: string): Promise<ExportBundle> {
  return request<ExportBundle>('/export', {
    method: 'POST',
    body: JSON.stringify({ draft, variant_id: variantId }),
  })
}

export { ApiError }