<script setup lang="ts">

import {ref, watch} from "vue";
// 定义组件接收的 props，这里接收父组件的 'name'
const props = defineProps(['name'])
// 创建一个响应式变量 myName，初始值为 props.name
// 注意：这里的 ref 创建的是 props.name 的一个副本，不是双向绑定
const myName = ref(props.name)

watch(()=>props.name,newVal =>{
  myName.value=newVal
})
defineExpose({
  myName
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label text-base">
      名字
    </label>
    <input v-model="myName" type="text" class="input w-108">
  </fieldset>
</template>

<style scoped>

</style>