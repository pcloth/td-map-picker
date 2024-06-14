import TdMapPicker_ from './TdMapPicker/index.vue'

export const TdMapPicker = TdMapPicker_

export default {
    install (Vue) {
        Vue.component(TdMapPicker_.name, TdMapPicker_)
    },
    TdMapPicker:TdMapPicker_
}