<script setup>
//defineProps 用于在 Vue 组件中定义接收的属性（props），让父组件可以向子组件传递数据
defineProps(['character'])

</script>

<template>
<div class="absolute left-2 right-22 top-6 h-10 w-fit rounded-full bg-black/50 flex items-center gap-2 px-2">
  <div class="avatar">
    <div class="w-8 rounded-full">
      <img :src="character.photo" alt="">
    </div>
  </div>
  <div class="text-white text-sm line-clamp-1 break-all">
    {{character.name}}
  </div>
</div>
</template>

<style scoped>

</style>