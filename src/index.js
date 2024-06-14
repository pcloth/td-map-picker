// import DHello from './DHello.vue'
import TdMapPicker from './TdMapPicker/index.vue'

export default {
    install (Vue, options) {
        Vue.component(TdMapPicker.name, TdMapPicker)
    }
}