<template>
    <div class="td_map_picker">
        <div class="td_map" :id="mapid"></div>
        <div class="td_map_city_picker" v-if="options.showCity" @click.stop="openCityPicker">{{ cityName }}</div>
        <div class="td_map_city_picker_popup" :class="{ fullHeight: showCityPicker }">
            <div class="city_cover" @click.stop="showCityPicker = false"></div>
            <div class="city_hot_list" @click.stop="showCityPicker = false" v-if="options.hotCitys && options.hotCitys.length">
                <div class="city_hot_title">热门城市：</div>
                <div class="city_hot_list_box">
                    <div class="city_hot_item" v-for="city in options.hotCitys" @click.stop="findCity(city)" :key="city">
                        {{ city }}</div>
                </div>
            </div>
            <div class="city_box" ref="cityBoxRef">

                <div class="city_filter">
                    <input type="text" style="width: 100%;" class="td_search_input" placeholder="输入城市名称"
                        v-model="cityFilter" />
                </div>
                <template v-for="p in cityList">
                    <div class="city_item" v-if="p.show" :key="p.c">
                        <div class="city_item_province picker_btn" :class="{
                            filter_status: p.filterStatus,
                            current_city: cityObj.c === p.c
                        }" :id="p.c" @click.stop="setCity(p)">{{ p.n }}</div>

                        <div class="city_item_box">
                            <template v-for="c in p.d">
                                <div class="city picker_btn" :id="c.c" :class="{
                                    filter_status: c.filterStatus,
                                    current_city: cityObj.c === c.c
                                }" @click.stop="setCity(c)" :key="c.c">{{ c.n }}</div>
                            </template>
                        </div>

                    </div>
                </template>
            </div>
        </div>
        <div class="td_map_popup" @click="hidePopup = false" :class="{
            mini: hidePopup
        }">
            <div class="my_location" @click.stop="getGeoPoint">
                <img class="location_icon" src="./images/location.png" alt="">
            </div>
            <div class="route_plans" v-if="planCount && options.showRoute">
                <div class="route_plan_btn" @click.stop="showPlan(plan)" v-for="plan, planIndex in routePlans"
                    :key="`plan${planIndex}`">
                    线路{{ planIndex + 1 }}({{ plan.distance }}km)
                </div>
            </div>
            <div class="tips">
                <div class="submit_box">
                    <template v-if="currentPoint">
                        <span>{{ currentPoint.name }}</span>
                        <span>{{ currentPoint.lonlat }}</span>
                    </template>
                </div>
                <!-- currentPoint.lonlat -->
                <div class="submit_button" :class="{
                    td_disabled: submitDisabled
                }" @click.stop="submitPoint">确定</div>
            </div>
            <div class="hide_popup_button" @click.stop="hidePopup = !hidePopup">
                <img class="arrow_icon" :class="{
                    flip: hidePopup
                }" src="./images/arrow.png" alt="">
            </div>
            <div class="td_search_box">
                <input v-model="searchWord" @change="searchMap" class="td_search_input"
                    :placeholder="options.placeholder" />
            </div>
            <template v-if="!hidePopup">
                <div class="hot_keywords">
                    <label>{{ options.hotTitle }}</label>
                    <div @click="setWord(item)" class="hot_keyword" v-for="item, idx in options.hotKeywords" :key="idx">
                        {{ item }}</div>
                </div>
                <div class="td_address_list">
                    <div class="td_not_data" v-if="!pointsList.length">
                        {{ options.noData }}
                    </div>
                    <template v-else>
                        <div class="td_address" @click="selectPoint(item)" v-for="item, idx in pointsList"
                            :key="item.hotPointID">
                            <span class="index">{{ idx + 1 }}</span>
                            <div class="td_add_content">
                                <span class="name">{{ item.name }}</span>
                                <span class="address">{{ item.address }}</span>
                            </div>
                        </div>
                        <div class="pagination">
                            <div class="pagination_button" :class="{
                                td_disabled: currentPage <= 1
                            }" @click="gotoPage(-1)">上一页</div>
                            <div class="pagination_button" :class="{
                                td_disabled: allpage <= currentPage
                            }" @click="gotoPage(+1)">下一页</div>
                        </div>
                    </template>
                </div>
            </template>

        </div>
    </div>
</template>

<script>
import coord from './coord.js';
import cityList_ from './level.min.json';
import startImg from './images/start.png';

cityList_.forEach(p => {
    p.show = true
    p.filter = p.n
    p.filterStatus = false;
    p.d.forEach(c => {
        c.show = true
        c.filter = p.n + c.n
        c.filterStatus = false;
    })
})
const cityList = cityList_

let searchObj = null;
let marker = null;
let startMarker = null

const props = {
    // 传入坐标wgs84
    value: {
        type: String,
        default: ""
    },
    /** submit提交的坐标系:
     * gcj02:国测局坐标系
     * wgs84:国际坐标系
     * bd09:百度坐标系
     */
    coordType: {
        type: String,
        default: "wgs84"
    },
    /** 坐标系输出精度 */
    decimals: {
        type: Number,
        default: 6
    },
    /** 地图key */
    tk: {
        type: String,
        default: "",
    },
    apiVer: {
        type: String,
        default: "4.0",
    },
    minZoom: {
        type: Number,
        default: 3,
    },
    maxZoom: {
        type: Number,
        default: 18,
    },
    zoom: {
        type: Number,
        default: 12,
    },
    hotTitle: {
        type: String,
        default: "热门搜索：",
    },
    hotKeywords: {
        type: Array,
        default() {
            return ["学校", "小区"];
        },
    },
    centerOffset: {
        type: Array,
        default() {
            return [0, -0.05];
        },
    },
    offsetRateMaps: {
        type: Object,
        default() {
            return {
                1: 1200,
                2: 800,
                3: 500,
                4: 280,
                5: 100,
                6: 45,
                7: 35,
                8: 25,
                9: 15,
                10: 4,
                11: 1.5,
                12: 1,
                13: 0.5555555556,
                14: 0.3333333333,
                15: 0.1666666667,
                16: 0.0833333333,
                17: 0.0416666667,
                18: 0.0208333333,
            }
        }
    },
    placeholder: {
        type: String,
        default: "请输入关键词搜索或移动定位点"
    },
    noData: {
        type: String,
        default: "暂无数据，请搜索关键词。"
    },
    color: {
        type: String,
        default: "#1890ff"
    },
    fontSize: {
        type: String,
        default: "0.98rem"
    },
    /**
     * 使用模式
     * webview 小程序webview模式，提交后，返回到小程序里面
     * picker 选择模式，提交后，返回到父组件
     * */
    mode: {
        type: String,
        default: "picker",
    },
    /** 如果传入了这个，将会返回距离 */
    startLonlat: {
        type: String,
        default: "",
    },
    /** 是否显示线路 */
    showRoute: {
        type: Boolean,
        default: false
    },
    /** policy：策略常量。常量如下：
        TMAP_DRIVING_POLICY_LEAST_TIME = 0 最少时间
        TMAP_DRIVING_POLICY_LEAST_DISTANCE = 1 最短距离
        TMAP_DRIVING_POLICY_AVOID_HIGHWAYS = 2 避开高速
        TMAP_DRIVING_POLICY_WALK = 3 步行 */
    drivingPolicy: {
        type: Number,
        default: 1,
    },
    defaultHide: {
        type: Boolean,
        default: false
    },
    debug: {
        type: Boolean,
        default: false
    },
    /** 提交地址的时候，名称优先使用兴趣点名称 */
    usePoi: {
        type: Boolean,
        default: false
    },
    /** 优先使用兴趣点时候，这个范围内的兴趣点才能被使用 */
    poiDistance: {
        type: Number,
        default: 30
    },
    /** 显示城市选择器 */
    showCity: {
        type: Boolean,
        default: true
    },
    /** 热门城市 */
    hotCitys: {
        type: Array,
        default() {
            return ['上海市', '北京市']
        }
    }
};
export default {
    name: "td-map-picker",
    props,
    data() {
        return {
            mapid: "map" + new Date().getTime(),
            initFlag: false,
            currentZoom: this.zoom,
            lnglat: null,
            currentPoint: null, // 当前选中点
            options: {
                ...this.$props,
            },
            searchWord: "",
            pointsList: [],
            currentPage: 1,
            allpage: 1,
            total: 0,
            hidePopup: this.defaultHide,
            routeLoadFlag: true,
            loadWxSdkFlag: false,
            routePlans: [],
            planCount: 0,
            cityName: '选择城市',
            cityObj: {},
            cityList,
            showCityPicker: false,
            cityFilter: ''
        };
    },
    watch: {
        value() {
            this.changeValue(this.value)
        },
        cityFilter() {
            const word = this.cityFilter.trim()
            this.cityList.forEach(p => {
                let showP = false;
                p.d.forEach(c => {
                    c.filterStatus = word && c.n.indexOf(word) >= 0
                    c.show = !word || c.filter.indexOf(word) >= 0
                    if (c.show) {
                        showP = true
                    }
                })
                p.show = !word || showP || p.filter.indexOf(word) >= 0
                p.filterStatus = word && p.n.indexOf(word) >= 0
            })
        }
    },
    computed: {
        submitDisabled() {
            // 线路加载
            if (!this.routeLoadFlag) return true;
            // 点位获取
            if (!this.currentPoint) return true;
            // 如果是webview小程序sdk加载状态
            if (this.options.mode === 'webview' && !this.loadWxSdkFlag) return true;
            return false;
        }
    },
    mounted() {
        this.initUrlParams();
        this.initMap();
    },
    methods: {
        initMap() {
            if (window.T) {
                // 已经存在了
                this.initOnload();
                return;
            }
            const script = document.createElement("script");
            const { apiVer, tk } = this.options;
            if (!tk) {
                throw "请配置tk参数";
            }
            this.log('加载地图sdk')
            script.type = "text/javascript";
            script.src = `//api.tianditu.gov.cn/api?v=${apiVer}&tk=${tk}`;
            script.onerror = (e) => {
                this.log("地图加载失败", e);
            };
            document.head.appendChild(script);
            script.onload = () => {
                this.initOnload();
            };
        },
        loadWxsdk() {
            // document.write('<script type="text/javascript" src="https://res.wx.qq.com/open/js/jweixin-1.4.0.js"><\/script>');
            if (window.wx) {
                return
            }
            this.log('加载微信sdk')
            const script = document.createElement("script");
            script.type = "text/javascript";
            script.src = "//res.wx.qq.com/open/js/jweixin-1.4.0.js";
            script.onerror = (e) => {
                alert('微信sdk加载失败' + JSON.stringify(e))
            };
            document.head.appendChild(script);
            script.onload = () => {
                // this.initOnload();
                this.loadWxSdkFlag = true;
            };
        },
        round(number) {
            const decimals = this.options.decimals
            const rate = Math.pow(10, decimals)
            return Math.round(number * rate) / rate
        },
        lonlatToCoordType(lonlat) {
            const g = lonlat.split(",");
            const coordType = this.options.coordType
            let value = [g[0], g[1]]
            if (coordType === 'gcj02') {
                value = coord.wgs84togcj02(g[0], g[1])
            } else if (coordType === 'bd09') {
                value = coord.wgs84togcj02(g[0], g[1])
                value = coord.gcj02tobd09(value[0], value[1])
            } else if (coordType === 'wgs84') {
                // 天地图和wgs84非常接近
            } else {
                console.error('未知的坐标系')
            }
            return value.map(v => this.round(v))
        },
        coordTypeToLonlat(lonlat) {
            const coordType = this.options.coordType
            const g = lonlat.split(",");
            let value = [g[0], g[1]]
            if (coordType === 'gcj02') {
                value = coord.gcj02towgs84(g[0], g[1])
            } else if (coordType === 'bd09') {
                value = coord.bd09togcj02(g[0], g[1])
                value = coord.gcj02towgs84(value[0], value[1])
            } else if (coordType === 'wgs84') {
                // 天地图和wgs84非常接近
            } else {
                console.error('未知的坐标系')
            }
            return value.map(v => this.round(v))
        },
        changeValue(value) {
            if (!window.T || !this.initFlag) {
                setTimeout(() => {
                    this.changeValue(value)
                }, 500)
                return
            }
            const g = this.coordTypeToLonlat(value);
            this.lnglat = new window.T.LngLat(g[0], g[1]);
            this.setPoint(this.lnglat);
            this.getLocation();
        },
        initOnload() {
            this.initMapInstance();
            if (this.value) {
                this.changeValue(this.value)
            } else {
                this.getGeoPoint();
            }
        },
        initMapInstance(lnglat) {
            const T = window.T;
            if (!lnglat) {
                lnglat = new T.LngLat(116.404, 39.915);
            }
            this.map = new T.Map(this.mapid, {
                minZoom: this.options.minZoom,
                maxZoom: this.options.maxZoom,
            });
            this.setPoint(lnglat, true);
            this.initFlag = true;
            this.map.addEventListener('click', (e) => {
                if (e.lnglat) {
                    this.setPoint(e.lnglat, true)
                    this.getLocation()
                }
            })
        },
        /** 从url上获取参数取代props参数 */
        initUrlParams() {
            marker = null;
            searchObj = null;
            startMarker = null;
            this.routePlans = [];
            this.planCount = 0;
            // 解析url参数
            window.location.href.split('?').pop().split('&').forEach(item => {
                let [key, value] = item.split('=')
                const propsConf = props[key];
                // base64解码
                value = decodeURIComponent(value)
                if (propsConf) {
                    if ([Array, Object, Boolean].includes(propsConf.type)) {
                        value = JSON.parse(value);
                    } else if (propsConf.type === Number) {
                        value = Number(value);
                    }
                }
                this.options[key] = value
            })
            this.currentZoom = this.options.zoom;
            this.hidePopup = this.options.defaultHide;
            this.log('url参数', this.options)
            if (this.options.value) {
                this.changeValue(this.options.value)
            }
            // 将color参数写入css变量
            document.documentElement.style.setProperty(
                "--td_map_picker_color",
                this.options.color
            );
            // 将fontSize写入css变量
            document.documentElement.style.setProperty(
                "--font-size",
                this.options.fontSize
            );
            if (this.options.mode === 'webview') {
                this.loadWxsdk()
            }
        },
        /** 接管console.log */
        log(...args) {
            if (this.options.debug) {
                console.log(...args)
            }
        },
        getGeoPoint() {
            // 获取当前浏览器定位
            let that = this;
            const T = window.T;
            return new Promise((resolve, reject) => {
                const geolocation = new T.Geolocation();
                geolocation.getCurrentPosition(function (result) {
                    that.log(result, '获取定位')
                    if (!result || !result.lnglat) {
                        const msg = '获取定位失败'
                        that.showMessage(msg)
                        reject(msg)
                        return
                    }
                    that.setPoint(result.lnglat, true);
                    that.getLocation();
                    resolve(result);
                });
                setTimeout(() => {
                    if (!this.lnglat) {
                        const msg = '获取定位超时'
                        that.showMessage(msg)
                        reject(msg);
                    }
                }, 8000);
            });
        },
        /** 模仿element弹窗信息 */
        showMessage(msg) {
            alert(msg);
        },
        moveCenter(lnglat) {
            let offLng = this.options.centerOffset[0] || 0;
            let offLat = this.options.centerOffset[1] || 0;
            const zoom = this.map?.getZoom() || this.currentZoom
            const offsetRateMaps = this.options.offsetRateMaps
            const rate = offsetRateMaps[zoom] || 1
            offLng = offLng * rate
            offLat = offLat * rate
            const offsetCenter = new T.LngLat(
                lnglat.lng + Number(offLng.toFixed(6)),
                lnglat.lat + Number(offLat.toFixed(6))
            );
            this.map.centerAndZoom(offsetCenter, zoom);
        },
        setPoint(lnglat, moveCenter = true) {
            const T = window.T;
            this.lnglat = lnglat;
            if (moveCenter) {
                this.moveCenter(lnglat)
            }
            if (!marker) {
                marker = new T.Marker(lnglat, {
                    zIndexOffset: 2
                });
                this.map.addOverLay(marker);
                marker.enableDragging();
                marker.addEventListener("dragend", (e) => {
                    this.lnglat = e.lnglat;
                    this.currentPoint = null;
                    this.getLocation();
                });
            } else {
                marker.setLngLat(lnglat);
            }
        },
        setStartPoint() {
            const { startLonlat } = this.options;
            if (startLonlat) {
                const g = this.coordTypeToLonlat(startLonlat)
                const lnglat = new window.T.LngLat(g[0], g[1]);
                if (startMarker) {
                    startMarker.setLngLat(lnglat)
                } else {
                    const icon = new T.Icon({
                        iconUrl: startImg,
                        iconSize: new T.Point(25, 41),
                        iconAnchor: new T.Point(12.5, 41),
                    });
                    startMarker = new T.Marker(lnglat, {
                        opacity: 0.8,
                        zIndexOffset: 1,
                        icon
                    });
                    this.map.addOverLay(startMarker);
                }
            }
        },
        setWord(item) {
            this.searchWord = item;
            this.searchMap();
        },
        searchMap() {
            const T = window.T;
            this.createSearchObj()
            this.currentPage = 1;
            this.total = 0;
            this.allpage = 1;
            this.pointsList = [];
            searchObj.search(this.searchWord);
        },
        createSearchObj() {
            if (!searchObj) {
                searchObj = new T.LocalSearch(this.map, {
                    pageCapacity: 5,
                    onSearchComplete: (result) => {
                        this.searchOnResult(result);
                    },
                });
            }
        },
        openCityPicker() {
            this.showCityPicker = true
            this.$nextTick(() => {
                // 滚动到当前城市
                let cityBox = this.$refs.cityBoxRef
                let currentCity = cityBox.querySelector('.current_city')
                if (currentCity) {
                    // 如果选中的是城市，滚动到父级
                    let offsetTop = currentCity.offsetTop
                    if (currentCity.className.startsWith('city ')) {
                        currentCity = currentCity.parentNode.parentNode
                        offsetTop = currentCity.offsetTop
                    }
                    cityBox.scrollTop = offsetTop - 40
                }
            })
        },
        setCity(city) {
            this.createSearchObj()
            this.log(city, 'city')
            if (city.c) {
                this.cityObj = city
                this.cityName = city.n
                searchObj.setSpecifyAdminCode(city.c)
                const { t } = city // {lat,lng}
                if (t) {
                    this.moveCenter(new T.LngLat(t.lng, t.lat))
                }
            }
            this.showCityPicker = false

        },
        findCity(cityName){
            let city = null;
            let findStatus = false;
            for(let p of this.cityList){
                if(p.n === cityName){
                    city = p
                    findStatus = true
                    break
                }
                
                for(let c of p.d){
                    if(c.n === cityName){
                        city = c
                        findStatus = true
                        break
                    }
                }
                if(findStatus){
                    break
                }
            }
            if(city){
                this.setCity(city)
            }
        },
        searchOnResult(result) {
            this.total = result.getCount();
            this.allpage = searchObj.getCountPage();
            const arr = result.getPois();
            this.pointsList = arr;
        },
        gotoPage(step) {
            this.currentPage = this.currentPage + step;
            if (step > 0) {
                if (this.allpage < this.currentPage) {
                    this.currentPage = this.allpage;
                    return;
                }
                searchObj.nextPage();
            } else {
                if (this.currentPage <= 1) {
                    this.currentPage = 1;
                }
                searchObj.previousPage();
            }
        },
        selectPoint(item) {
            const T = window.T;
            const g = item.lonlat.split(",");
            /** address: "重庆市渝北区"
                hotPointID: "90344007C6D4C326"
                lonlat: "106.889672,29.939002"
                name: "明月学校"
                phone: ""
                poiType: "101"
                source: "0" 
            */
            this.log(item, '选中')
            this.setCurrentPoint({
                name: item.name,
                address: item.address,
                lonlat: item.lonlat,
                addressComponent: null,
            });
            this.setPoint(new T.LngLat(g[0], g[1]));
            this.getLocation(true);
        },
        // 逆地理编码
        getLocation(coverAddressComponent) {
            const T = window.T;
            const geocode = new T.Geocoder();
            const that = this;
            geocode.getLocation(that.lnglat, function (result) {
                const name = that.getPointName(result);
                that.log(result, '逆地理编码')
                const addressComponent = result.addressComponent
                const {
                    county,
                    county_code,
                    city,
                    city_code,
                    province,
                    province_code,
                } = addressComponent
                const c = city_code ? city_code : province_code
                const cityObj = {
                    n: city ? city : province,
                    c: c,
                    d: [{
                        n: county,
                        c: county_code
                    }]
                }
                that.setCity(cityObj)
                if (coverAddressComponent) {
                    that.setCurrentPoint({
                        name: name,
                        address: result.formatted_address,
                        lonlat: that.lnglat.lng + "," + that.lnglat.lat,
                        ...that.currentPoint,
                        addressComponent: result.addressComponent,
                    });
                } else {
                    that.setCurrentPoint({
                        name: name,
                        address: result.formatted_address,
                        lonlat: that.lnglat.lng + "," + that.lnglat.lat,
                        addressComponent: result.addressComponent,
                    });
                }
            });
        },
        async setCurrentPoint(data) {
            this.routeLoadFlag = false;
            const { startLonlat, drivingPolicy } = this.options;
            let drives = {};
            if (this.options.showRoute && startLonlat) {
                drives = await this.getDrivingRoute(
                    this.coordTypeToLonlat(startLonlat).join(','),
                    data.lonlat,
                    drivingPolicy
                );
                this.setStartPoint()
            }
            this.currentPoint = {
                distance: null,
                duration: null,
                routes: null,
                ...data,
                ...drives,
                startLonlat,
            };
            this.routeLoadFlag = true;
        },
        getDrivingRoute(startLonlat, endLonlat, policy) {
            const T = window.T;
            const that = this;
            return new Promise((resolve) => {
                const driving = new T.DrivingRoute(this.map, {
                    policy: policy,
                    onSearchComplete: function (result) {
                        const plans = result.getNumPlans();
                        that.planObj = result;
                        that.options.showRoute && that.showPlans(result);
                        that.log('规划线路数量：', plans)
                        if (plans) {
                            const plan = result.getPlan(0);
                            resolve({
                                distance: plan.getDistance(),
                                duration: plan.getDuration(),
                                routes: plan.routes,
                            });
                        } else {
                            resolve({
                                distance: 0,
                                duration: 0,
                                routes: [],
                            });
                        }
                    },
                });
                const startG = startLonlat.split(",");
                const endG = endLonlat.split(",");
                driving.search(
                    new T.LngLat(startG[0], startG[1]),
                    new T.LngLat(endG[0], endG[1])
                );
            });
        },
        /** 显示线路 */
        showPlans(plans) {
            this.planCount = plans.getNumPlans();
            if (!this.planCount) { return }
            const routePlans = []
            for (let i = 0; i < this.planCount; i++) {
                routePlans.push(plans.getPlan(i))
                if (i === 0) {
                    this.showPlan(plans.getPlan(i))
                }
            }
            this.routePlans = routePlans;
        },
        /** 在地图上绘制线路 */
        showPlan(plan) {
            const T = window.T;
            // const pointGroup = plan.routes.item.map(row=>{
            //     const [lng,lat] = row.turnlatlon.split(',')
            //     return new T.LngLat(lng,lat)
            // });
            const pointGroup = plan.result.routelatlon.split(';').filter(item => item).map(row => {
                const [lng, lat] = row.split(',')
                return new T.LngLat(lng, lat)
            });
            if (this.polyline) {
                this.map.removeOverLay(this.polyline)
            }
            this.log('pointGroup', pointGroup)
            this.polyline = new T.Polyline(pointGroup, {
                color: "#ff0000",
                weight: 2,
                opacity: 0.7,
            });
            this.map.addOverLay(this.polyline);
        },
        /** 检查是否处于小程序环境，调用api返回小程序并提交参数 */
        submitMPWebview() {
            const wx = window.wx;
            if (wx && wx.miniProgram) {
                wx.miniProgram.postMessage({ data: this.currentPoint });
                wx.miniProgram.navigateBack();
            } else {
                alert('请在小程序环境中使用webview')
            }
        },
        getPointName(fullPoint) {
            if (this.options.usePoi) {
                // 使用兴趣点作为定位名称，而不是地址
                const addressComponent = fullPoint.addressComponent
                if (addressComponent.poi && addressComponent.poi_distance <= this.options.poiDistance) {
                    return addressComponent.poi
                }
            }
            return fullPoint.name || fullPoint.address
        },
        submitPoint() {
            const value = this.lonlatToCoordType(this.currentPoint.lonlat).join(',')
            this.currentPoint.lonlat = value
            this.currentPoint.coordType = this.options.coordType
            this.currentPoint.name = this.getPointName(this.currentPoint)
            this.log('提交', this.currentPoint, this.options)
            this.$emit("submit", this.currentPoint);
            if (this.options.mode === "webview") {
                this.submitMPWebview();
            } else {
                this.$emit("input", value);
            }
        }
    },
};
</script>

<style>
.td_map_picker {
    width: 100%;
    height: 100%;
    position: relative;
    --pop-mini-height: 4.4rem;
    --pop-full-height: 23.2rem;

}

.td_map {
    width: 100%;
    height: 100%;
}

.td_map_popup {
    position: absolute;
    bottom: 0.4rem;
    width: calc(100% - 1.6rem);
    left: 0.4rem;
    background: #fff;
    padding: 0.4rem;
    padding-top: 0;
    border-radius: 0.5rem;
    box-shadow: 0 0 0.4rem rgba(0, 0, 0, 0.1);
    z-index: 9999;
    height: var(--pop-full-height);
    display: flex;
    flex-direction: column;
    animation: changeToFull 0.6s;
}

.hide_popup_button {
    text-align: center;
    width: 100%;
    color: var(--td_map_picker_color);
    margin-bottom: 0.2rem;
    margin-top: 0.2rem;
}



.td_map_popup.mini {
    height: var(--pop-mini-height);
    animation: changeToMini 0.6s;
}

@keyframes changeToMini {
    0% {
        height: var(--pop-full-height);
    }

    100% {
        height: var(--pop-mini-height);
    }
}

@keyframes changeToFull {
    0% {
        height: var(--pop-mini-height);
    }

    100% {
        height: var(--pop-full-height);
    }
}

.td_search_box {
    /* padding: 0.4rem; */
    border-bottom: 1px solid #f0f0f0;
    display: flex;
}

.td_search_input {
    display: flex;
    flex: 1;
    height: 2.0rem;
    border: 1px solid #f0f0f0;
    border-radius: 0.4rem;
    padding: 0 0.4rem;
    /* 激活时边框蓝色 */
    outline: none;
    font-size: var(--font-size);
}

/* 激活时边框蓝色 */
.td_search_input:focus {
    border-color: var(--td_map_picker_color);
}

.td_address_list {
    margin-top: 0.4rem;
    display: flex;
    flex-direction: column;
    overflow: scroll;
    flex: 1;
}

.td_address {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    width: 100%;
    line-height: 140%;
}

.td_add_content {
    display: flex;
    flex-direction: column;
    width: calc(100% - 1.2rem - 10px);
}

.td_address .index {
    width: 1.2rem;
    text-align: center;
    font-size: var(--font-size);
    color: #999;
    margin-right: 0.4rem;
}

.td_add_content .name {
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: var(--font-size);
    font-weight: bold;
}

.td_add_content .address {
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: var(--font-size);
    color: #999;
}

.pagination {
    display: flex;
    justify-content: center;
    margin-top: 0.4rem;
}

.pagination_button {
    margin: 0 0.2rem;
    color: var(--td_map_picker_color);
    cursor: pointer;
    border: 1px solid var(--td_map_picker_color);
    padding: 0.2rem 0.4rem;
}

.td_disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}

.td_not_data {
    display: flex;
    justify-content: center;
    align-items: center;
    color: #999;
    flex: 1;
}

.hot_keywords {
    display: flex;
    align-items: center;
    margin-top: 0.4rem;
    padding-left: 0.4rem;
}

.hot_keyword {
    padding: 0.2rem 0.4rem;
    border: 1px solid #f0f0f0;
    border-radius: 4px;
    margin-right: 0.4rem;
    cursor: pointer;
    color: var(--td_map_picker_color);
    border: 1px solid var(--td_map_picker_color);
}

.tips {
    position: absolute;
    top: -50px;
    left: 0;
    width: calc(100% - 0.8rem);
    padding: 0 0.4rem;
    background: rgba(255, 255, 255, 0.4);
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 0.2rem;
}

.my_location {
    position: absolute;
    top: -90px;
    background: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 34px;
    height: 34px;
    border-radius: 0.2rem;
    color: var(--td_map_picker_color);
    /* 阴影 */
    box-shadow: 0 0 0.4rem rgba(0, 0, 0, 0.1);
}

.route_plans {
    position: absolute;
    left: 54px;
    top: -90px;
    /* background: #fff; */
    display: flex;
    justify-content: flex-start;
    align-items: center;
    width: calc(100% - 54px - 0.4rem);
    height: 34px;
    border-radius: 0.2rem;
    color: var(--td_map_picker_color);
    /* 阴影 */
    /* box-shadow: 0 0 0.4rem rgba(0, 0, 0, 0.1); */

}

.route_plan_btn {
    display: flex;
    justify-content: center;
    align-items: center;
    border: 1px solid #f0f0f0;
    border-radius: 4px;
    margin-right: 0.4rem;
    cursor: pointer;
    height: 34px;
    padding: 0 5px;
    color: var(--td_map_picker_color);
    /* border: 1px solid var(--td_map_picker_color); */
    background: #fff;
    box-shadow: 0 0 0.4rem rgba(0, 0, 0, 0.1);
}

.my_location:active {
    background: #f0f0f0;
}

.location_icon {
    width: 20px;
}

.submit_box {
    display: flex;
    flex-direction: column;
    width: calc(100% - 80px);
}

.submit_box span {
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.submit_button {
    background: var(--td_map_picker_color);
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 0.4rem;
    width: 60px;
    height: 34px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.arrow_icon {
    width: 20px;
    animation: transform 0.3s;
}

.arrow_icon.flip {
    transform: rotate(180deg);
    animation: transform 0.3s;
}

@keyframes transform {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(180deg);
    }
}

.td_map_city_picker {
    position: absolute;
    top: 0.4rem;
    left: 0.4rem;
    background: #fff;
    padding: 0.2rem 0.4rem;
    border-radius: 0.2rem;
    color: var(--td_map_picker_color);
    box-shadow: 0 0 0.4rem rgba(0, 0, 0, 0.1);
    z-index: 9999;
    cursor: pointer;
}

.td_map_city_picker_popup {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 19999;
    width: 100%;
    padding: 0.2rem 0.4rem;
    height: 0;
    opacity: 0;
    transition: all 0.3s;
    overflow: hidden;

}

.td_map_city_picker_popup.fullHeight {
    height: 100%;
    opacity: 1;
}

.city_cover {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 9998;
}

.city_box {
    position: absolute;
    background: #f7f7f7;
    padding: 0.2rem 0.4rem;
    border-radius: 0.2rem;
    color: #333;
    box-shadow: 0 0 0.4rem rgba(0, 0, 0, 0.1);
    top: 2.8rem;
    height: calc(100% - 4.8rem);
    width: calc(100% - 2.4rem);
    z-index: 9999;
    overflow: auto;
    /* css变动过渡 */
    transition: all 0.3s;
}

.city_filter {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
    position: -webkit-sticky;
    position: sticky;
    top: 0;
    background: #fff;
    box-shadow: 0 0 0.4rem rgba(0, 0, 0, 0.1);

}

.filter_status {
    color: #f10022 !important;
}

.city_item {
    display: flex;
    flex-direction: column;
}

.city_item:not(:first-child) {
    border-top: 1px solid #ccc;
}

.city_item:not(:last-child) {
    margin-bottom: 1rem;
}

.city_item_province {
    font-weight: bold;
    margin-top: 0.5rem;
    margin-bottom: 0.2rem;
    width: fit-content;
}

.current_city {
    color: var(--td_map_picker_color);
}

.picker_btn {
    cursor: pointer;
}

.city_item_box {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin-top: 0.5rem;
}

.city_item_box.city {
    color: #333;
}

.city_hot_list {
    display: flex;
    align-items: center;
    position: absolute;
    top: 0.8rem;
    justify-content: flex-end;
    width: calc(100% - 1.6rem);
    color: #fff;
    z-index: 99999;
}
.city_hot_list_box {
    display: flex;
    align-items: center;
}
.city_hot_item {
    padding: 0.2rem 0.4rem;
    border: 1px solid #f0f0f0;
    border-radius: 4px;
    margin-left: 0.4rem;
    cursor: pointer;
    color: var(--td_map_picker_color);
    border: 1px solid var(--td_map_picker_color);
    background: #fff;
}
</style>