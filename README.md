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
|value|string|v-model绑定，只有在确定按钮点击后才提交input事件。值是一个逗号分割的lonLat字符串|无|
|coordType|string|指定value的坐标系，支持gcj02、wgs84、bd09三种格式，请注意，当使用非wgs84的时候，反复提交会造成坐标误差累积偏离地点|wgs84|
|decimals|number|坐标保持的精度|6|
|tk|string|天地图key|无|
|minZoom|number|最小缩放|3|
|maxZoom|number|最大缩放|18|
|zoom|number|默认缩放|12|
|hotTitle|string|热门标题|热门搜索：|
|hotKeywords|array|热门搜索词列表|["学校", "小区"]|
|centerOffset|array|地图中心视野偏移|[0, -0.05]|
|offsetRateMaps|object|根据zoom和偏移值系数计算视野中心|默认在常见手机尺寸下不需要修改|
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
|coordType|string|当前lonlat的坐标系|
|lonlat|string|点位的坐标|
|addressComponent|object|点位逆地址解析数据|
|startLonlat|string|如果传入了startLonlat，提交的时候回传回来|
|distance|number|如果有startLonlat和当前点位的距离，单位千米|
|duration|number|如果有startLonlat和当前点位的常规行车时长|
|routes|object|如果有startLonlat和当前点位的线路|


### 小程序webview模式
```html
<template>
	<view>
		<web-view :src="currentUrl" @message="onMessage"></web-view>
	</view>
</template>

<script>
const host = 'http://192.168.0.55:8080/?mode=webview'
export default {
	data() {
		return {
			currentUrl: '',
			startLonlat: '',
			locationType: ''
		};
	},
	onLoad(options) {
		let url = host;
		this.locationType = options.locationType || 'start'
		if (options.startLonlat) {
			url = url + `&startLonlat=${options.startLonlat}`
		}
		if (options.value) {
			url = url + `&value=${options.value}`
		}
		this.currentUrl = url;
	},
	methods: {
		onMessage({ detail }) {
      // 在这个事件里接收提交数据
			console.log(detail, 'onMessage')
			if (detail.data) {
				const data = detail.data[0]
				this.$store.dispatch('order/SET_ORDER_POINT', { data, type: this.locationType })
			}

		}
	}
}
</script>
```
