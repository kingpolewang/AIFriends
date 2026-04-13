<script setup>
import { onMounted, ref, nextTick } from "vue"
import { useRoute } from "vue-router"
import api from "@/js/http/api.js"

import Vditor from "vditor"
import "vditor/dist/index.css"

const route = useRoute()
const blog = ref(null)
const loading = ref(true)

async function renderMarkdown(markdown) {
  await nextTick()

  Vditor.preview(document.getElementById("preview"), markdown, {
    mode: "dark", // 你喜欢深色代码块可以用 dark
    hljs: {
      enable: true,
      style: "github-dark", // highlight 风格（vditor 内部支持）
      lineNumber: true
    },
    markdown: {
      toc: true, // 自动目录（可选）
    },
    theme: {
      current: "light", // 页面主题
    }
  })
}

async function load() {
  const res = await api.get("api/blog/list/", { params: { items_count: 0 } })
  blog.value = res.data.blogs.find(b => b.id == route.params.blog_id)
  loading.value = false

  if (blog.value?.content) {
    await renderMarkdown(blog.value.content)
  }
}

onMounted(load)
</script>

<template>
  <div class="page-container max-w-3xl mx-auto px-4 py-8">

    <div v-if="loading" class="flex justify-center py-20">
      <span class="loading loading-spinner loading-lg text-primary/30"></span>
    </div>

    <article v-else-if="blog" class="glass-card shadow-2xl rounded-3xl overflow-hidden border border-white/20">

      <!-- 封面背景 -->
      <div v-if="blog.cover_photo" class="relative w-full h-[200px] bg-slate-900 overflow-hidden">
        <img :src="blog.cover_photo"
             class="absolute inset-0 w-full h-full object-cover blur-2xl opacity-40 scale-110" />
        <img :src="blog.cover_photo"
             class="relative z-10 w-full h-full object-contain mx-auto" />
      </div>

      <div class="p-5 md:p-8">

        <!-- 标题 -->
        <h1 class="text-2xl font-extrabold text-slate-900 leading-tight mb-6 tracking-tight">
          {{ blog.title }}
        </h1>

        <!-- 作者 + 标签 -->
        <div class="flex items-center gap-3 mb-8 pb-4 border-b border-slate-100">
          <img :src="blog.author.photo" class="w-8 h-8 rounded-full border border-primary/20" />
          <span class="text-sm font-medium text-slate-500">{{ blog.author.username }}</span>

          <div class="flex gap-1 ml-auto flex-wrap">
            <span v-for="tag in blog.tags" :key="tag" class="badge badge-sm badge-ghost opacity-70">
              #{{ tag }}
            </span>
          </div>
        </div>

        <!-- 🔥 Vditor 原生渲染区域 -->
        <div id="preview" class="vditor-reset"></div>

      </div>
    </article>
  </div>
</template>

<style scoped>
/* vditor-reset 是 Vditor 推荐的 markdown 样式 class */
/* 你可以额外加一点适配磨砂 UI */
:deep(.vditor-reset) {
  font-size: 0.95rem;
  line-height: 1.9;
  word-break: break-word;
}
</style>