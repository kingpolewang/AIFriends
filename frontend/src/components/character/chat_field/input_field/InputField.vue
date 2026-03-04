<script setup>

import SendIcon from "@/components/navbar/icons/SendIcon.vue";
import MicIcon from "@/components/navbar/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import streamApi from "@/js/http/streamApi.js";

// 父组件传递给子组件
const props=defineProps(['friendId'])

const inputRef=useTemplateRef('input-ref')
// 获取输入框的内容
const message=ref('')
let isProcessing = false


// 聚焦函数,打开模态框后聚焦到输入框
function focus(){
  // 通过 ref 引用获取 DOM 元素，并调用它的 focus() 方法
  inputRef.value.focus()
}
// 处理发送事件
async function handleSend(){
  // 检查是否正在处理中
  // 如果正在处理，直接返回，避免重复执行
  if (isProcessing) return
  isProcessing=true
  const content = message.value.trim()
  if (!content) return
  //发送后清空聊天框
  message.value=''

  try {
    await streamApi('/api/friend/message/chat/',{
      body:{
        friend_id : props.friendId,
        message:content,
      },
       // 收到消息时的回调函数
      onmessage(data,isDone){
        //如果流式响应结束
        if (isDone){
          isProcessing=false
        }else if (data.content){
          console.log(data.content)
        }
      },
      // 发生错误时的回调函数
      onerror(err){
        isProcessing=false
      },
    })
  }catch (err){
    console.log(err)
    isProcessing=false
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