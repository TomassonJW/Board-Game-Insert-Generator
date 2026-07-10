import type { ComposerDraft, ExportBundle, Portfolio } from './types'

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

export async function loadStarter(): Promise<ComposerDraft> {
  const result = await request<{ draft: ComposerDraft }>('/starter')
  return result.draft
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