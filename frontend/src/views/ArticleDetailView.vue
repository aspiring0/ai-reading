<script setup lang="ts">
/**
 * ArticleDetailView — 文章详情页。
 *
 * 展示：标题、难度、阅读时间、分段内容（heading 高亮，paragraph 正常）。
 * 路由参数：/articles/:id
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticle } from '@/api/articles'
import type { ArticleResponse, SegmentResponse } from '@/api/articles'

const route = useRoute()
const router = useRouter()

const article = ref<ArticleResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    article.value = await getArticle(route.params.id as string)
  } catch (e: any) {
    error.value = e.response?.status === 404 ? 'Article not found' : 'Failed to load article'
  } finally {
    loading.value = false
  }
})

function difficultyColor(d: string): string {
  switch (d) {
    case 'easy': return 'bg-green-100 text-green-700'
    case 'medium': return 'bg-yellow-100 text-yellow-700'
    case 'hard': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function segmentClass(seg: SegmentResponse): string {
  return seg.segment_type === 'heading'
    ? 'text-xl font-bold text-gray-900 mt-6 mb-2'
    : 'text-gray-700 leading-relaxed mb-3'
}
</script>

<template>
  <div>
    <!-- 加载状态 -->
    <div v-if="loading" class="space-y-4 animate-pulse">
      <div class="h-8 bg-gray-200 rounded w-2/3"></div>
      <div class="h-4 bg-gray-200 rounded w-1/3"></div>
      <div class="mt-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-4 bg-gray-200 rounded"></div>
      </div>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-500">{{ error }}</p>
      <button
        class="mt-3 px-4 py-2 text-blue-500 border border-blue-300 rounded hover:bg-blue-50"
        @click="router.push('/')"
      >
        ← Back to Articles
      </button>
    </div>

    <!-- 文章内容 -->
    <article v-else-if="article">
      <!-- 返回按钮 -->
      <button
        class="mb-4 text-sm text-gray-500 hover:text-gray-700"
        @click="router.push('/')"
      >
        ← Back to Articles
      </button>

      <!-- 标题 -->
      <h1 class="text-3xl font-bold text-gray-900">{{ article.title }}</h1>

      <!-- 元信息 -->
      <div class="mt-3 flex items-center gap-3 text-sm text-gray-500">
        <span
          class="font-medium px-2 py-0.5 rounded"
          :class="difficultyColor(article.difficulty)"
        >
          {{ article.difficulty }}
        </span>
        <span v-if="article.topic">{{ article.topic }}</span>
        <span>{{ article.word_count ?? 0 }} words</span>
        <span v-if="article.estimated_reading_time_minutes">
          {{ article.estimated_reading_time_minutes }} min read
        </span>
      </div>

      <!-- 分段内容 -->
      <div class="mt-6">
        <div
          v-for="seg in article.segments"
          :key="seg.id"
          :class="segmentClass(seg)"
        >
          {{ seg.content }}
        </div>
      </div>

      <!-- 无分段时显示全文 -->
      <div v-if="article.segments.length === 0" class="mt-6 text-gray-700 leading-relaxed whitespace-pre-line">
        {{ article.content }}
      </div>
    </article>
  </div>
</template>
