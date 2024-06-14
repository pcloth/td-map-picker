<template>
  <div style="width:100vw;height:100vh;">
    <TdMapPicker/>
  </div>
</template>

<script>
import TdMapPicker from './TdMapPicker'
import "@/assets/components.scss"

export default {
  name: 'App',
  components: {
    TdMapPicker
  },
  data(){
    return {
    }
  }
}
</script>

<style>
body {
    margin: 0;
}
</style>

