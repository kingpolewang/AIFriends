<script setup>
import { ref } from "vue"
import api from "@/js/http/api.js"
import { useRouter } from "vue-router"

const router = useRouter()
const title = ref("")
const content = ref("")
const tags = ref("")
const cover = ref(null)
const submitting = ref(false)

async function submit() {
  if (!title.value || !content.value) return alert("请填写必要内容")
  submitting.value = true
  const formData = new FormData()
  formData.append("title", title.value)
  formData.append("content", content.value)
  tags.value.split(',').forEach(t => {
    if (t.trim()) formData.append("tags", t.trim())
  })
  if (cover.value) formData.append("cover_photo", cover.value)

  try {
    const res = await api.post("api/blog/create/", formData)
    if (res.data.result === 'success') router.push({ name: 'blog-index' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
 <div class="page-container flex justify-center px-4">
  <div class="glass-card w-full max-w-md p-6 rounded-2xl shadow-xl">
    <h1 class="text-lg font-semibold mb-6 text-center handwritten-content text-primary">写下你的博客</h1>

    <div class="space-y-5">
      <input v-model="title" class="input w-full text-base border-0 border-b border-gray-200 focus:border-gray-400 focus:ring-0 rounded-none px-0 py-1 handwritten-content" placeholder="输入标题...">

      <textarea v-model="content" class="textarea w-full h-56 handwritten-content text-base leading-relaxed focus:ring-2 focus:ring-primary/20 rounded-xl" placeholder="开始创作你的博客内容..."></textarea>

      <div class="form-control">
        <label class="label">
          <span class="label-text text-sm text-gray-600">标签</span>
        </label>
        <input v-model="tags" class="input input-bordered w-full text-sm" placeholder="生活, 科技, 旅行" />
      </div>

      <div class="form-control">
        <label class="label">
          <span class="label-text text-sm text-gray-600">封面照片</span>
        </label>
        <input type="file" @change="e => cover = e.target.files[0]" class="file-input file-input-bordered file-input-primary w-full text-sm" />
      </div>

      <button class="btn btn-primary w-full text-base shadow-md shadow-primary/20" @click="submit">
        <span v-if="submitting" class="loading loading-spinner"></span>
        发布博客
      </button>
    </div>
  </div>
</div>
</template>