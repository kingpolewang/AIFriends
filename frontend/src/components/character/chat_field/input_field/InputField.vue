<script setup>

import SendIcon from "@/components/navbar/icons/SendIcon.vue";
import MicIcon from "@/components/navbar/icons/MicIcon.vue";
import {onUnmounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import streamApi from "@/js/http/streamApi.js";
import Microphone from "@/components/character/chat_field/input_field/Microphone.vue";

// 父组件（ChatField）传递给子组件 的变量
const props=defineProps(['friendId'])
// 接受父组件（ChatField）传来的事件
const emit =defineEmits(['pushBackMessage','addToLastMessage'])

const inputRef=useTemplateRef('input-ref')
// 获取输入框的内容
const message=ref('')

let processId=0
//是否显示麦克风
const showMic =ref(false)



//语音播放
let mediaSource = null;
let sourceBuffer = null;
let audioPlayer = new Audio(); // 全局播放器实例
let audioQueue = [];           // 待写入 Buffer 的二进制队列
let isUpdating = false;        // Buffer 是否正在写入

const initAudioStream = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    mediaSource = new MediaSource();
    audioPlayer.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener('sourceopen', () => {
        try {
            sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
            sourceBuffer.addEventListener('updateend', () => {
                isUpdating = false;
                processQueue();
            });
        } catch (e) {
            console.error("MSE AddSourceBuffer Error:", e);
        }
    });

    audioPlayer.play().catch(e => console.error("等待用户交互以播放音频"));
};

const processQueue = () => {
    if (isUpdating || audioQueue.length === 0 || !sourceBuffer || sourceBuffer.updating) {
        return;
    }

    isUpdating = true;
    const chunk = audioQueue.shift();
    try {
        sourceBuffer.appendBuffer(chunk);
    } catch (e) {
        console.error("SourceBuffer Append Error:", e);
        isUpdating = false;
    }
};

const stopAudio = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    if (mediaSource) {
        if (mediaSource.readyState === 'open') {
            try {
                mediaSource.endOfStream();
            } catch (e) {
            }
        }
        mediaSource = null;
    }

    if (audioPlayer.src) {
        URL.revokeObjectURL(audioPlayer.src);
        audioPlayer.src = '';
    }
};

const handleAudioChunk = (base64Data) => {  // 将语音片段添加到播放器队列中
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        audioQueue.push(bytes);
        processQueue();
    } catch (e) {
        console.error("Base64 Decode Error:", e);
    }
};

onUnmounted(() => {
    audioPlayer.pause();
    audioPlayer.src = '';
});






// 聚焦函数,打开模态框后聚焦到输入框
function focus(){
  // 通过 ref 引用获取 DOM 元素，并调用它的 focus() 方法
  inputRef.value.focus()
}
// 处理发送事件
async function handleSend(event,audio_msg){
  let content
  if (audio_msg){
    content=audio_msg.trim()
  }else
  {
    content = message.value.trim()
  }
  if (!content) return

  initAudioStream()

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
        if (data.audio){
          handleAudioChunk(data.audio)
        }
      },
    })
  }catch (err){
    console.log(err)

  }
}
function close(){
  ++processId
  showMic.value=false
  stopAudio()
}
function handleStop(){
  ++processId
  stop()
}
defineExpose({
  focus,
  close,
})
</script>

<template>
  <!-- 回车也能触发  将div变成form -->
  <form v-if="!showMic" @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
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
    <div @click="showMic=true" class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon/>
    </div>
  </form>
  <Microphone
      v-else-if="showMic"
      @close="showMic=false"
      @send="handleSend"
      @stop="handleStop"
  />
</template>

<style scoped>

</style>