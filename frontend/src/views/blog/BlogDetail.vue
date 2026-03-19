<script setup>
import { onMounted, ref } from "vue"
import { useRoute } from "vue-router"
import api from "@/js/http/api.js"

const route = useRoute()
const blog = ref(null)
const loading = ref(true)

async function load() {
  // 优化点：直接拉取全部是为了匹配 ID，如果后端有 get_detail 接口更好
  const res = await api.get("api/blog/list/", { params: { items_count: 0 } })
  blog.value = res.data.blogs.find(b => b.id == route.params.blog_id)
  loading.value = false
}

onMounted(load)
</script>

<template>
  <div class="page-container max-w-4xl">
    <div v-if="loading" class="flex justify-center py-20">
      <span class="loading loading-bars loading-lg text-primary"></span>
    </div>

    <article v-else-if="blog" class="glass-card overflow-hidden">
      <img v-if="blog.cover_photo" :src="blog.cover_photo" class="w-full max-h-[400px] object-cover" />

      <div class="p-8 md:p-12">
        <h1 class="text-4xl md:text-5xl font-bold mb-6 handwritten-content leading-tight">
          {{ blog.title }}
        </h1>

        <div class="flex items-center gap-4 mb-8 border-b border-black/5 pb-6">
          <img :src="blog.author.photo" class="w-10 h-10 rounded-full" />
          <div>
            <div class="font-bold">{{ blog.author.username }}</div>
            <div class="text-xs opacity-50 uppercase tracking-widest">Author</div>
          </div>
          <div class="ml-auto flex gap-2">
            <span v-for="tag in blog.tags" :key="tag" class="badge badge-primary badge-outline">#{{ tag }}</span>
          </div>
        </div>

        <div class="handwritten-content whitespace-pre-line text-xl leading-relaxed text-slate-800">
          {{ blog.content }}
        </div>
      </div>
    </article>
  </div>
</template>
<style scoped>
.handwritten-content {
  font-family: 'Dancing Script', 'Caveat', 'Segoe UI', cursive;
}
</style>