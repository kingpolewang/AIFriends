<script setup >
import {computed, nextTick, ref, useTemplateRef} from "vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import ChatHistory from "@/components/character/chat_field/chat_history/ChatHistory.vue";

//接受来自父组件Character的参数
const props = defineProps(['friend'])
const modalRef = useTemplateRef('modal-ref')
// 引用InputFieldz子组件
const inputRef=useTemplateRef('input-ref')

const chatHistoryRef = useTemplateRef('chat-history-ref')
const history = ref([])

async function showModal(){
  modalRef.value.showModal()
  await nextTick()
  inputRef.value.focus()
}
// 将模态框背景图片设置成聊天背景：
const modalStyle = computed(() => {
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})

// 在最后添加一个消息
function handlePushBackMessage(msg){
  // 将新消息添加到历史列表
  history.value.push(msg)
  // 滚动聊天窗口到底部
  chatHistoryRef.value.scrollToBottom()
}
// 在最后一条消息上补充内容
function handleAddToLastMessage(delta){
  history.value.at(-1).content+=delta
  chatHistoryRef.value.scrollToBottom()
}


defineExpose({
  showModal,
})
</script>

<template>
<dialog ref="modal-ref" class="modal">
  <div class="modal-box w-90 h-150" :style="modalStyle">
    <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute right-1 top-1">
      ✕
    </button>

    <ChatHistory
        ref="chat-history-ref"
        v-if="friend"
        :friendId="friend.id"
        :character="friend.character"
        :history="history"
    />

    <!-- 父组件 定义两个事件pushBackMessage，addToLastMessage 进行父->子   -->
    <InputField
        v-if="friend"
        :friendId="friend.id"
        ref="input-ref"
        @pushBackMessage="handlePushBackMessage"
        @addToLastMessage="handleAddToLastMessage"
    />
    <CharacterPhotoField v-if="friend" :character="friend.character"/>
  </div>
</dialog>
</template>

<style scoped>

</style>