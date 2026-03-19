<script setup>
import NavBar from "@/components/navbar/NavBar.vue";
import { onMounted } from "vue";
import { useUserStore } from "@/stores/user.js";
import api from "@/js/http/api.js";
import { useRoute, useRouter } from "vue-router";

const user = useUserStore()
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  try {
    const res = await api.get('/api/user/account/get_user_info/')
    if (res.data.result === 'success') {
      user.setUserInfo(res.data)
    }
  } catch (err) {
    console.error("Auth failed", err)
  } finally {
    user.setHasPulledUserInfo(true)
    if (route.meta.needLogin && !user.isLogin()) {
      router.replace({ name: 'user-account-login-index' })
    }
  }
})
</script>

<template>
  <div class="relative min-h-screen">
    <div class="fixed inset-0 z-[-1] pointer-events-none">
      <div class="absolute inset-0 bg-base-200/50"></div>
      <img
        src="@/assets/static/image/background.jpg"
        class="w-full h-full object-cover opacity-60"
        style="image-rendering: high-quality;"
      />
    </div>

    <NavBar>
      <div class="min-h-[calc(100vh-64px)] overflow-x-hidden">
        <RouterView v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </div>
    </NavBar>
  </div>
</template>

<style>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>