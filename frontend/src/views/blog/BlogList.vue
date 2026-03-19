<script setup>
import { ref, onMounted, onBeforeUnmount, useTemplateRef } from "vue"
import api from "@/js/http/api.js"
import { useRouter } from "vue-router"

const router = useRouter()
const blogs = ref([])
const itemsCount = ref(0)
const loading = ref(false)

const sentinelRef = useTemplateRef('sentinel-ref')
let observer = null

async function loadMore() {
  if (loading.value) return
  loading.value = true
  const res = await api.get('api/blog/list/', {
    params: { items_count: itemsCount.value }
  })
  if (res.data.result === 'success') {
    blogs.value.push(...res.data.blogs)
    itemsCount.value += res.data.blogs.length
  }
  loading.value = false
}

const openDetail = (id) => router.push({ name: 'blog-detail', params: { blog_id: id } })

onMounted(async () => {
  await loadMore()
  observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) loadMore()
  })
  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div class="page-container">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="blog in blogs" :key="blog.id"
        @click="openDetail(blog.id)"
        class="glass-card group overflow-hidden cursor-pointer flex flex-col">

        <div v-if="blog.cover_photo" class="h-48 overflow-hidden">
          <img :src="blog.cover_photo" class="w-full h-full object-cover group-hover:scale-110 transition duration-500" />
        </div>

        <div class="p-6 flex-1 flex flex-col">
          <h2 class="text-2xl font-bold mb-2 group-hover:text-primary transition-colors handwritten-content">
            {{ blog.title }}
          </h2>
          <p class="line-clamp-3 text-slate-600 mb-4 flex-1 handwritten-content opacity-90">
            {{ blog.content }}
          </p>

          <div class="flex flex-wrap gap-2 mb-4">
            <span v-for="tag in blog.tags" class="badge badge-outline badge-primary badge-sm">#{{ tag }}</span>
          </div>

          <div class="flex items-center gap-2 border-t pt-4 border-black/5">
            <img :src="blog.author.photo" class="w-8 h-8 rounded-full shadow-sm" />
            <span class="text-sm font-medium opacity-70">{{ blog.author.username }}</span>
          </div>
        </div>
      </div>
    </div>

    <div ref="sentinel-ref" class="h-20 flex items-center justify-center">
      <span v-if="loading" class="loading loading-dots loading-lg text-primary"></span>
    </div>
  </div>
</template>