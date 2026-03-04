<script setup>

import SendIcon from "@/components/navbar/icons/SendIcon.vue";
import MicIcon from "@/components/navbar/icons/MicIcon.vue";
import {useTemplateRef} from "vue";

const inputRef=useTemplateRef('input-ref')

// 聚焦函数,打开模态框后聚焦到输入框
function focus(){
  // 通过 ref 引用获取 DOM 元素，并调用它的 focus() 方法
  inputRef.value.focus()
}


defineExpose({
  focus
})
</script>

<template>
<div class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
  <input
      ref="input-ref"
      class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full rounded-2xl pr-20"
      type="text"
      placeholder="请输入..."
  >
  <div class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
    <SendIcon/>
  </div>
  <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
    <MicIcon/>
  </div>
</div>
</template>

<style scoped>

</style>