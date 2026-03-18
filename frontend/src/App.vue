<script setup>

import NavBar from "@/components/navbar/NavBar.vue";
import {onMounted} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import {useRoute, useRouter} from "vue-router";

const user = useUserStore()
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  try {
    const res = await api.get('/api/user/account/get_user_info/')
    const data = res.data
    if (data.result === 'success') {
      user.setUserInfo(data)
    }
  } catch (err) {
  } finally {
    user.setHasPulledUserInfo(true)

    if (route.meta.needLogin && !user.isLogin()) {
      await router.replace({
        name: 'user-account-login-index',
      })
    }
  }
})

</script>

<template>
  <div class="app-wrapper">
    <NavBar>
      <RouterView/>
    </NavBar>
  </div>
</template>

<style>
/* 建议去掉 scoped 以便背景应用到 body 或根容器 */
.app-wrapper {
  position: relative;
  min-height: 100vh;
  width: 100%;
}

.app-wrapper::before {
  content: "";
  position: fixed; /* 固定背景，不随滚动条滚动 */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;

  /* 替换成你的图片地址 */
  background-image: url("@/assets/static/image/background.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  /* 核心设置：透明度 */
  opacity: 0.7;

  /* 确保背景在内容层级之下 */
  z-index: -1;

  /* 解决你之前关心的清晰度问题：强制高质量渲染 */
  image-rendering: high-quality;
  pointer-events: none; /* 确保背景不响应鼠标事件 */
}
</style>
