<script setup>
import { ref, onMounted, onBeforeUnmount, useTemplateRef } from "vue"
import api from "@/js/http/api.js"

const blogs = ref([])
const itemsCount = ref(0)
const sentinelRef = useTemplateRef("sentinel-ref")
const editingId = ref(null)
const submitting = ref(false)

const editTitle = ref("")
const editContent = ref("")
const editTags = ref("")
const editCover = ref(null)
const editCoverUrl = ref("")
let tempUrl = null

async function loadMore() {
  const res = await api.get("api/blog/my_list/", { params: { items_count: itemsCount.value } })
  if (res.data.result === 'success') {
    blogs.value.push(...res.data.blogs)
    itemsCount.value += res.data.blogs.length
  }
}

function startEdit(blog) {
  editingId.value = blog.id
  editTitle.value = blog.title
  editContent.value = blog.content
  editTags.value = blog.tags.join(',')
  editCoverUrl.value = blog.cover_photo
}

function handleSelectFile(e) {
  const file = e.target.files[0]
  if (!file) return
  editCover.value = file
  if (tempUrl) URL.revokeObjectURL(tempUrl)
  tempUrl = URL.createObjectURL(file)
  editCoverUrl.value = tempUrl
}

async function submitEdit(id) {
  submitting.value = true
  const formData = new FormData()
  formData.append("blog_id", id)
  formData.append("title", editTitle.value)
  formData.append("content", editContent.value)
  editTags.value.split(',').forEach(t => {
    if (t.trim()) formData.append("tags", t.trim())
  })
  if (editCover.value) formData.append("cover_photo", editCover.value)

  const res = await api.post("api/blog/update/", formData)
  if (res.data.result === 'success') {
    const index = blogs.value.findIndex(b => b.id === id)
    blogs.value[index] = { ...blogs.value[index], title: editTitle.value, content: editContent.value, tags: editTags.value.split(','), cover_photo: editCoverUrl.value }
    editingId.value = null
  }
  submitting.value = false
}

async function remove(id) {
  if (!confirm("确定删除这篇故事吗？")) return
  const res = await api.post("api/blog/remove/", { blog_id: id })
  if (res.data.result === 'success') blogs.value = blogs.value.filter(b => b.id !== id)
}

let observer = null
onMounted(async () => {
  await loadMore()
  observer = new IntersectionObserver(entries => { if (entries[0].isIntersecting) loadMore() })
  observer.observe(sentinelRef.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div class="page-container">
    <h1 class="text-3xl font-bold mb-10 handwritten-content">管理我的博客</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div v-for="blog in blogs" :key="blog.id" class="glass-card flex flex-col overflow-hidden">

        <div v-if="editingId === blog.id" class="p-6 space-y-4">
          <label class="relative block h-48 group cursor-pointer">
            <img :src="editCoverUrl || '/placeholder.jpg'" class="w-full h-full object-cover rounded-xl border-2 border-dashed border-primary/20" />
            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition rounded-xl">
              <span class="text-white">点击更换预览</span>
            </div>
            <input type="file" class="hidden" accept="image/*" @change="handleSelectFile" />
          </label>
          <input v-model="editTitle" class="input input-bordered w-full handwritten-content font-bold" />
          <textarea v-model="editContent" class="textarea textarea-bordered w-full h-40 handwritten-content"></textarea>
          <div class="flex justify-end gap-2">
            <button class="btn btn-ghost btn-sm" @click="editingId = null">取消</button>
            <button class="btn btn-primary btn-sm" @click="submitEdit(blog.id)" :disabled="submitting">保存</button>
          </div>
        </div>

        <div v-else class="flex flex-col h-full">
          <img v-if="blog.cover_photo" :src="blog.cover_photo" class="h-48 w-full object-cover" />
          <div class="p-6 flex-1 flex flex-col">
            <h2 class="text-xl font-bold mb-2 handwritten-content">{{ blog.title }}</h2>
            <p class="line-clamp-3 text-sm opacity-80 mb-4 flex-1 handwritten-content">{{ blog.content }}</p>
            <div class="flex gap-2 justify-end mt-4">
              <button class="btn btn-outline btn-primary btn-sm" @click="startEdit(blog)">编辑</button>
              <button class="btn btn-outline btn-error btn-sm" @click="remove(blog.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div ref="sentinel-ref" class="h-10"></div>
  </div>
</template>