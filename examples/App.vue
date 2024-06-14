<template>
  <div style="width:100vw;height:100vh;">
    <TdMapPicker :tk="mapkey"/>
  </div>
</template>

<script>
import TdMapPicker from '../src/TdMapPicker/index.vue'
// 引入地图key
import {mapkey} from '../key'

export default {
  name: 'App',
  components: {
    TdMapPicker
  },
  data(){
    return {
        mapkey
    }
  }
}
</script>

<style>
body {
    margin: 0;
}
</style>

