/**
 * 文章 API — 封装所有文章相关的后端请求。
 *
 * 对应后端端点：
 *   GET  /api/v1/articles           → getArticles()
 *   GET  /api/v1/articles/{id}      → getArticle()
 */

import apiClient from './index'

// --- 类型定义（和后端 schemas 对应）---

export interface ArticleListItem {
  id: string
  title: string
  difficulty: string
  topic: string | null
  cefr_level: string | null
  word_count: number | null
  is_published: boolean
  published_at: string | null
  created_at: string
}

export interface ArticleListResponse {
  items: ArticleListItem[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface SegmentResponse {
  id: string
  segment_index: number
  segment_type: string // 'paragraph' | 'heading'
  content: string
}

export interface ArticleResponse {
  id: string
  title: string
  source: string
  difficulty: string
  topic: string | null
  cefr_level: string | null
  word_count: number | null
  quality_score: number | null
  is_published: boolean
  published_at: string | null
  created_at: string
  updated_at: string
  content: string
  segments: SegmentResponse[]
  estimated_reading_time_minutes: number | null
}

export interface ArticlesQuery {
  difficulty?: string
  topic?: string
  page?: number
  page_size?: number
}

// --- API 函数 ---

export async function getArticles(query?: ArticlesQuery): Promise<ArticleListResponse> {
  const params = new URLSearchParams()
  if (query?.difficulty) params.set('difficulty', query.difficulty)
  if (query?.topic) params.set('topic', query.topic)
  if (query?.page) params.set('page', String(query.page))
  if (query?.page_size) params.set('page_size', String(query.page_size))

  const qs = params.toString()
  const { data } = await apiClient.get<ArticleListResponse>(`/api/v1/articles${qs ? '?' + qs : ''}`)
  return data
}

export async function getArticle(id: string): Promise<ArticleResponse> {
  const { data } = await apiClient.get<ArticleResponse>(`/api/v1/articles/${id}`)
  return data
}
