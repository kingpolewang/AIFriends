<script setup>

//接受父组件传递过来的参数
import Message from "@/components/character/chat_field/chat_history/message/Message.vue";
import {nextTick, onBeforeUnmount, onMounted, useTemplateRef} from "vue";
import api from "@/js/http/api.js";

const props = defineProps(['history','friendId','character'])
// 声明要触发的事件 接受父组件传统过来的 向上添加消息的事件
const emit = defineEmits(['pushFrontMessage'])
const scrollRef=useTemplateRef('scroll-ref')
const sentinelRef = useTemplateRef('sentinel-ref')
let isLoading=false
let hasMessages=true
let lastMessageId=0
async function loadMore(){
  if (isLoading||!hasMessages) return
  isLoading=true
  let newMessages=[]
  try{
    const res = await api.get('api/friend/message/get_history/',{
      params:{
        last_message_id:lastMessageId,
        friend_id:props.friendId
      }
    })
    const data=res.data
    if (data.result === 'success'){
      newMessages=data.messages
    }
  }catch (err){
    console.log(err)
  }finally {
    isLoading=false
    if (newMessages.length===0){
      hasMessages=false
    }else {
      //保存旧高度
      const oldHeight=scrollRef.value.scrollHeight
      //将消息添加到顶部
      for (const m of newMessages){
        // emit：是子组件通过 defineEmits() 定义的函数，用于触发父组件的事件
        emit('pushFrontMessage',{
          role:'ai',
          content:m.output,
          id:crypto.randomUUID()
        })
        emit('pushFrontMessage',{
          role:'user',
          content:m.user_message,
          id:crypto.randomUUID()
        })
        lastMessageId=m.id
      }
      await nextTick()

      const newHeight = scrollRef.value.scrollHeight
      // 新高度-旧高度=增长的高度
      scrollRef.value.scrollTop += newHeight- oldHeight
      if (checkSentinelVisible()){
        await loadMore()
      }
    }
  }
}

async function scrollToBottom(){
  // 等待渲染完
  await nextTick()
  // 改变scrollTop的值来实现滚动功能
  scrollRef.value.scrollTop = scrollRef.value.scrollHeight
}

let observer = null

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

onMounted(async () => {
  await loadMore()  // 加载新元素
  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadMore()
        }
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )
  //监听哨兵元素， 每次哨兵被看到时，都会触发一次
  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()  // 解绑监听器
})

defineExpose({
  // 在父组件实现滚动
  scrollToBottom
})
</script>

<template>
  <div ref="scroll-ref" class="absolute top-18 left-0 w-90 h-112 overflow-y-scroll no-scrollbar">
    <div ref="sentinel-ref" class="h-2"></div>
    <Message
      v-for="message in history"
      :key="message.id"
      :message="message"
      :character="character"
    />
  </div>

</template>

<style scoped>
/* 隐藏 Chrome, Safari 和 Opera 的滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

/* 隐藏 IE, Edge 和 Firefox 的滚动条 */
.no-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>