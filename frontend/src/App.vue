<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <nav class="mx-auto max-w-7xl px-4 py-3 flex items-center gap-6">
        <RouterLink to="/" class="text-lg font-bold text-gray-900">AI Reading</RouterLink>
        <RouterLink to="/" class="text-gray-600 hover:text-gray-900">Home</RouterLink>
        <RouterLink to="/articles" class="text-gray-600 hover:text-gray-900">Articles</RouterLink>
        <RouterLink to="/corpus" class="text-gray-600 hover:text-gray-900">Corpus</RouterLink>
        <RouterLink to="/about" class="text-gray-600 hover:text-gray-900">About</RouterLink>
      </nav>
    </header>
    <main class="mx-auto max-w-7xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
