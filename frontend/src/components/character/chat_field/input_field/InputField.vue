<script setup>

import SendIcon from "@/components/navbar/icons/SendIcon.vue";
import MicIcon from "@/components/navbar/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";

// 父组件传递给子组件
const props=defineProps(['friendId'])

const inputRef=useTemplateRef('input-ref')
// 获取输入框的内容
const message=ref('')


// 聚焦函数,打开模态框后聚焦到输入框
function focus(){
  // 通过 ref 引用获取 DOM 元素，并调用它的 focus() 方法
  inputRef.value.focus()
}
// 处理发送事件
async function handleSend(){
  const content = message.value.trim()
  if (!content) return
  //发送后清空聊天框
  message.value=''
  try {
    const res=await api.post('/api/friend/message/chat/',{
      friend_id:props.friendId,
      message:content
    })
    console.log(res.data)
  }catch (err){
    console.log(err)
  }
}

defineExpose({
  focus
})
</script>

<template>
<!-- 回车也能触发  将div变成form -->
<form @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
  <input
      v-model="message"
      ref="input-ref"
      class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full rounded-2xl pr-20"
      type="text"
      placeholder="请输入..."
  >
  <div @click="handleSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
    <SendIcon/>
  </div>
  <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
    <MicIcon/>
  </div>
</form>
</template>

<style scoped>

</style>