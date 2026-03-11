<script setup>

import SendIcon from "@/components/navbar/icons/SendIcon.vue";
import MicIcon from "@/components/navbar/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import streamApi from "@/js/http/streamApi.js";

// 父组件（ChatField）传递给子组件 的变量
const props=defineProps(['friendId'])
// 接受父组件（ChatField）传来的事件
const emit =defineEmits(['pushBackMessage','addToLastMessage'])

const inputRef=useTemplateRef('input-ref')
// 获取输入框的内容
const message=ref('')

let processId=0

// 聚焦函数,打开模态框后聚焦到输入框
function focus(){
  // 通过 ref 引用获取 DOM 元素，并调用它的 focus() 方法
  inputRef.value.focus()
}
// 处理发送事件
async function handleSend(){

  const content = message.value.trim()
  if (!content) return

  //将当前版本号存下来
  const curId = ++ processId
  //发送后清空聊天框
  message.value=''

  //  发送用户消息
  // 触发'pushBackMessage'事件，将用户输入的消息推送到消息列表
  emit('pushBackMessage',
      {
        role: 'user',                    // 消息角色：用户
        content: content,                 // 消息内容：用户输入的内容
        id: crypto.randomUUID()          // 生成唯一ID：使用Web Crypto API生成随机UUID作为消息标识符
      })
  // 发送AI响应消息（初始为空）
  // 触发'pushBackMessage'事件，创建一个空的AI消息占位符，用于后续流式填充
  emit('pushBackMessage',
      {
          role: 'ai',                       // 消息角色：AI助手
          content: '',                      // 消息内容：初始为空字符串，等待AI响应逐步填充
          id: crypto.randomUUID()           // 生成唯一ID：使用Web Crypto API生成随机UUID作为消息标识符
      })
  try {
    await streamApi('/api/friend/message/chat/',{
      body:{
        friend_id : props.friendId,
        message:content,
      },
       // 收到消息时的回调函数
      onmessage(data){
        if (curId!==processId) return
        if (data.content){
          // 触发'addToLastMessage'事件，将新内容添加到当前会话中最后一条消息的末尾
          emit('addToLastMessage',data.content) // 要追加的内容：从data对象中获取的content字段
        }
      },
    })
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