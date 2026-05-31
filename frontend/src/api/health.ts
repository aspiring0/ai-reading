import apiClient from '.'

export interface HealthResponse {
  status: string
  version: string
  database: string
  redis: string
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/health')
  return data
}
