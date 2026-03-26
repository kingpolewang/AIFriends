<script setup>
import { onMounted, ref, computed } from "vue"
import { useRoute } from "vue-router"
import api from "@/js/http/api.js"

// 1. 引入解析与高亮核心
import { marked } from "marked"
import hljs from "highlight.js"
import "highlight.js/styles/github-dark.css" // 使用高对比度深色主题

const route = useRoute()
const blog = ref(null)
const loading = ref(true)

// 配置 Marked 解析器
marked.setOptions({
  breaks: true,
  gfm: true,
  highlight: (code, lang) => {
    const language = hljs.getLanguage(lang) ? lang : "plaintext"
    return hljs.highlight(code, { language }).value
  },
})

// 计算属性：渲染 Markdown
const renderedContent = computed(() => {
  if (!blog.value?.content) return ""
  // 预处理：确保中文和代码之间有换行空间，解决挤占
  const content = blog.value.content.replace(/([。！？；：])\s*/g, "$1\n\n")
  return marked.parse(content)
})

async function load() {
  const res = await api.get("api/blog/list/", { params: { items_count: 0 } })
  blog.value = res.data.blogs.find(b => b.id == route.params.blog_id)
  loading.value = false
}

onMounted(load)
</script>

<template>
  <div class="page-container max-w-2xl mx-auto px-4 py-8">
    <div v-if="loading" class="flex justify-center py-20">
      <span class="loading loading-spinner loading-lg text-primary/30"></span>
    </div>

    <article v-else-if="blog" class="glass-card shadow-2xl rounded-3xl overflow-hidden border border-white/20">

      <div v-if="blog.cover_photo" class="relative w-full h-[180px] bg-slate-900 overflow-hidden">
        <img :src="blog.cover_photo" class="absolute inset-0 w-full h-full object-cover blur-2xl opacity-40 scale-110" />
        <img :src="blog.cover_photo" class="relative z-10 w-full h-full object-contain mx-auto" />
      </div>

      <div class="p-5 md:p-8">
        <h1 class="text-2xl font-extrabold text-slate-900 leading-tight mb-6 tracking-tight">
          {{ blog.title }}
        </h1>

        <div class="flex items-center gap-3 mb-8 pb-4 border-b border-slate-100">
          <img :src="blog.author.photo" class="w-8 h-8 rounded-full border border-primary/20" />
          <span class="text-sm font-medium text-slate-500">{{ blog.author.username }}</span>
          <div class="flex gap-1 ml-auto">
            <span v-for="tag in blog.tags" :key="tag" class="badge badge-sm badge-ghost opacity-70">#{{ tag }}</span>
          </div>
        </div>

        <div class="markdown-body" v-html="renderedContent"></div>
      </div>
    </article>
  </div>
</template>

<style scoped>
@reference "@/assets/main.css";

.markdown-body {
  /* 解决文字挤占的核心：强制换行与合理的行高 */
  @apply text-slate-700 antialiased;
  font-size: 0.95rem;
  line-height: 1.8;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-all; /* 强制在过长的字符间断行 */
}

/* 解决高亮不清晰：强制深色背景 */
:deep(pre) {
  @apply my-6 p-4 rounded-xl shadow-lg !bg-[#0d1117] !text-slate-200 overflow-x-auto;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(code) {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  @apply font-medium;
}

/* 行内代码（针对你提到的 v-model 等文字） */
:deep(:not(pre) > code) {
  @apply px-1.5 py-0.5 rounded bg-slate-200/80 text-rose-700 font-bold mx-0.5 border border-slate-300/50;
  font-size: 0.85em;
  word-break: break-word;
}

/* 列表与间距 */
:deep(p) { @apply mb-5; }
:deep(h2) { @apply text-xl font-bold text-slate-900 mt-8 mb-4; }

/* 强制高亮颜色对比度 */
:deep(.hljs-keyword) { color: #ff7b72 !important; }
:deep(.hljs-attr) { color: #79c0ff !important; }
:deep(.hljs-string) { color: #a5d6ff !important; }
:deep(.hljs-variable) { color: #ffa657 !important; }
</style>