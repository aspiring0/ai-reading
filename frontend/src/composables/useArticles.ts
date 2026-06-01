/**
 * useArticles composable — 文章列表的状态管理。
 *
 * 封装：加载状态、文章数据、分页、过滤、错误处理。
 * 组件里只需要 const { articles, loading, fetchArticles } = useArticles()
 */

import { ref } from 'vue'
import { getArticles } from '@/api/articles'
import type { ArticleListItem, ArticlesQuery } from '@/api/articles'

export function useArticles() {
  const articles = ref<ArticleListItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const page = ref(1)
  const pages = ref(0)
  const pageSize = ref(20)

  async function fetchArticles(query?: Omit<ArticlesQuery, 'page' | 'page_size'>) {
    loading.value = true
    error.value = null
    try {
      const res = await getArticles({
        ...query,
        page: page.value,
        page_size: pageSize.value,
      })
      articles.value = res.items
      total.value = res.total
      pages.value = res.pages
    } catch (e: any) {
      error.value = e.message || 'Failed to load articles'
    } finally {
      loading.value = false
    }
  }

  async function goToPage(p: number) {
    if (p < 1 || p > pages.value) return
    page.value = p
    await fetchArticles()
  }

  return {
    articles,
    loading,
    error,
    total,
    page,
    pages,
    pageSize,
    fetchArticles,
    goToPage,
  }
}
