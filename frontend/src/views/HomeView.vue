<script setup lang="ts">
/**
 * HomeView — 首页，展示已发布文章的卡片列表。
 *
 * 功能：加载文章、分页、难度过滤、空状态。
 */
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useArticles } from '@/composables/useArticles'

const { articles, loading, error, total, page, pages, fetchArticles, goToPage } = useArticles()

onMounted(() => {
  fetchArticles()
})

function difficultyColor(d: string): string {
  switch (d) {
    case 'easy': return 'bg-green-100 text-green-700'
    case 'medium': return 'bg-yellow-100 text-yellow-700'
    case 'hard': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Articles</h1>
      <span class="text-sm text-gray-500">{{ total }} articles</span>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="i in 6" :key="i" class="animate-pulse rounded-lg border p-4 space-y-3">
        <div class="h-4 bg-gray-200 rounded w-3/4"></div>
        <div class="h-3 bg-gray-200 rounded w-1/2"></div>
        <div class="h-3 bg-gray-200 rounded w-1/4"></div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-500">{{ error }}</p>
      <button
        class="mt-3 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        @click="fetchArticles()"
      >
        Retry
      </button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="articles.length === 0" class="text-center py-12 text-gray-400">
      No articles yet.
    </div>

    <!-- 文章卡片列表 -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <RouterLink
        v-for="article in articles"
        :key="article.id"
        :to="`/articles/${article.id}`"
        class="block rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
      >
        <h2 class="font-semibold text-gray-900 line-clamp-2">{{ article.title }}</h2>

        <div class="mt-2 flex items-center gap-2">
          <span
            class="text-xs font-medium px-2 py-0.5 rounded"
            :class="difficultyColor(article.difficulty)"
          >
            {{ article.difficulty }}
          </span>
          <span v-if="article.topic" class="text-xs text-gray-400">{{ article.topic }}</span>
        </div>

        <div class="mt-2 text-xs text-gray-400">
          {{ article.word_count ?? 0 }} words
        </div>
      </RouterLink>
    </div>

    <!-- 分页 -->
    <div v-if="pages > 1" class="mt-6 flex justify-center gap-2">
      <button
        :disabled="page <= 1"
        class="px-3 py-1 rounded border text-sm disabled:opacity-40"
        @click="goToPage(page - 1)"
      >
        ← Prev
      </button>
      <span class="px-3 py-1 text-sm text-gray-500">
        {{ page }} / {{ pages }}
      </span>
      <button
        :disabled="page >= pages"
        class="px-3 py-1 rounded border text-sm disabled:opacity-40"
        @click="goToPage(page + 1)"
      >
        Next →
      </button>
    </div>
  </div>
</template>
