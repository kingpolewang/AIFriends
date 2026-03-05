<script setup>
defineProps(['message','character'])
</script>

<template>
  <div v-if="message.content">
    <div v-if="message.role==='ai' " >

    </div>
    <div v-else>

    </div>
  </div>

</template>

<style scoped>

</style>