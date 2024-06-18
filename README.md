## 天地图坐标拾取器
支持vue组件和小程序webview两种模式获取

## vue 2.6

## 安装
```sh
npm install td-map-picker
```

## 引入并使用
> 注意：父元素必须要有尺寸，不然无法显示
```vue
<template>
  <div style="width:100vw;height:100vh;">
    <TdMapPicker v-model="value" :tk="mapkey"/>
  </div>
</template>

<script>
import {TdMapPicker} from 'td-map-picker'
// 引入地图key
import {mapkey} from '../key'

export default {
  name: 'App',
  components: {
    TdMapPicker
  },
  data(){
    return {
        mapkey,
        value:''
    }
  }
}
</script>

<style>
body {
    margin: 0;
}
</style>


```

### 参数说明

> 所有的props参数均可以通过url传入

|属性|类型|说明|默认值|
|--|--|--|--|
|value|string|v-model绑定值，是一个逗号分割的lonLat字符串|无|
|tk|string|天地图key|无|
|minZoom|number|最小缩放|3|
|maxZoom|number|最大缩放|18|
|zoom|number|默认缩放|12|
|hotTitle|string|热门标题|热门搜索：|
|hotKeywords|array|热门搜索词列表|["学校", "小区"]|
|centerOffset|array|地图中心视野偏移|[0, -0.05]|
|placeholder|string|搜索框提示|请输入关键词搜索或移动定位点|
|noData|string|无数据提示|暂无数据，请搜索关键词。|
|color|string|主颜色|#1890ff|
|mode|string|模式，可选项：webview 小程序webview模式，提交后，返回到小程序里面；picker 选择模式，提交后，返回到父组件|picker|
|startLonlat|string|开始坐标字符串，用逗号分割lon,lat，如果传入了这个，将会返回距离|无|
|drivingPolicy|number|计算距离和线路的策略:0=最少时间、1=最短距离、2=避开高速、3=步行|1|
|defaultHide|boolen|引入时是否收起信息框|false|

### 事件
|事件|参数|说明|
|--|--|--|
|submit|Object 下方详细说明|当用户选中了点位之后提交出来的数据|

#### submit 数据说明
|key|类型|说明|
|--|--|--|
|name|string|点位的名字|
|address|string|点位的地址|
|lonlat|string|点位的坐标|
|addressComponent|object|点位逆地址解析数据|
|startLonlat|string|如果传入了startLonlat，提交的时候回传回来|
|distance|number|如果有startLonlat和当前点位的距离，单位千米|
|duration|number|如果有startLonlat和当前点位的常规行车时长|
|routes|object|如果有startLonlat和当前点位的线路|
