<template>
    <div class="td_map_picker">
        <div class="td_map" :id="mapid"></div>
        <div class="td_map_popup" @click="hidePopup=false" :class="{
            mini:hidePopup
        }">
            <div class="tips" v-if="currentPoint">
                <div class="submit_box">
                    <span>{{currentPoint.name}}</span>
                    <span>{{currentPoint.lonlat}}</span>
                </div>
                <div class="submit_button" :class="{
                    td_disabled:!canSubmit&& currentPoint?true:false,
                }" @click.stop="submitPoint">确定</div>
            </div>
            <div class="hide_popup_button" @click.stop="hidePopup=!hidePopup">
                <img class="arrow_icon" :class="{
                    flip:hidePopup
                }" src="./images/arrow.png" alt="">
            </div>
            <div class="td_search_box">
                <input v-model="searchWord" @change="searchMap" class="td_search_input" :placeholder="placeholder" />
            </div>
            <template v-if="!hidePopup">
                <div class="hot_keywords">
                    <label>{{options.hotTitle}}</label>
                    <div @click="setWord(item)" class="hot_keyword" v-for="item,idx in options.hotKeywords" :key="idx">{{item}}</div>
                </div>
                <div class="td_address_list">
                    <div class="td_not_data" v-if="!pointsList.length">
                        {{noData}}
                    </div>
                    <template v-else>
                        <div class="td_address" @click="selectPoint(item)" v-for="item,idx in pointsList" :key="item.hotPointID">
                            <span class="index">{{idx+1}}</span>
                            <div class="td_add_content">
                                <span class="name">{{item.name}}</span>
                                <span class="address">{{item.address}}</span>
                            </div>
                        </div>
                        <div class="pagination">
                            <div class="pagination_button" :class="{
                            td_disabled:currentPage<=1
                        }" @click="gotoPage(-1)">上一页</div>
                            <div class="pagination_button" :class="{
                            td_disabled:allpage<=currentPage
                        }" @click="gotoPage(+1)">下一页</div>
                        </div>
                    </template>
                </div>
            </template>

        </div>
    </div>
</template>

<script>
let searchObj = null;
let marker = null;

const props = {
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
            return ["学校", "医院", "超市"];
        },
    },
    centerOffset: {
        type: Array,
        default() {
            return [0, -0.08];
        },
    },
    placeholder:{
        type:String,
        default:"请输入关键词搜索或移动定位点"
    },
    noData:{
        type:String,
        default:"暂无数据，请搜索关键词。"
    },
    color:{
        type:String,
        default:"#1890ff"
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
    /** policy：策略常量。常量如下：
        TMAP_DRIVING_POLICY_LEAST_TIME = 0 最少时间
        TMAP_DRIVING_POLICY_LEAST_DISTANCE = 1 最短距离
        TMAP_DRIVING_POLICY_AVOID_HIGHWAYS = 2 避开高速
        TMAP_DRIVING_POLICY_WALK = 3 步行 */
    drivingPolicy: {
        type: Number,
        default: 1,
    },
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
            hidePopup: true,
            canSubmit: true,
        };
    },
    mounted() {
        this.initUrlParams();
        this.initMap();
        window.tt = this;
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
            script.type = "text/javascript";
            script.src = `http://api.tianditu.gov.cn/api?v=${apiVer}&tk=${tk}`;
            script.onerror = (e) => {
                console.error("地图加载失败", e);
            };
            document.head.appendChild(script);
            script.onload = () => {
                this.initOnload();
            };
        },
        initOnload() {
            this.initMapInstance();
            this.getGeoPoint();
        },
        initMapInstance(lnglat) {
            const T = window.T;
            if (!lnglat) {
                lnglat = new T.LngLat(116.404, 39.915);
            }
            this.map = new T.Map(this.mapid);
            this.setPoint(lnglat, true);
            this.initFlag = true;
        },
        /** 从url上获取参数取代props参数 */
        initUrlParams() {
            let url = new URL(window.location.href);
            // 获取所有的参数覆盖到options上
            url.searchParams.forEach((value, key) => {
                const propsConf = props[key];
                if (propsConf) {
                    if ([Array, Object, Boolean].includes(propsConf.type)) {
                        value = JSON.parse(value);
                    } else if (propsConf.type === Number) {
                        value = Number(value);
                    }
                }
                this.options[key] = value;
            });
            this.currentZoom = this.options.zoom;
            console.log(this.options, "options>>");
            // 将color参数写入css变量
            document.documentElement.style.setProperty(
                "--td_map_picker_color",
                this.options.color
            );
        },
        getGeoPoint() {
            // 获取当前浏览器定位
            let that = this;
            const T = window.T;
            return new Promise((resolve, reject) => {
                const geolocation = new T.Geolocation();
                geolocation.getCurrentPosition(function (result) {
                    console.log(result, "定位信息");
                    this.lnglat = result.lnglat;
                    that.setPoint(result.lnglat, true);
                    that.getLocation();
                    resolve(result);
                });
                setTimeout(() => {
                    if (!this.lnglat) {
                        reject("获取定位超时");
                    }
                }, 8000);
            });
        },
        setPoint(lnglat, moveCenter = true) {
            const T = window.T;
            this.lnglat = lnglat;
            if (moveCenter) {
                const offsetCenter = new T.LngLat(
                    lnglat.lng + this.options.centerOffset[0],
                    lnglat.lat + this.options.centerOffset[1]
                );
                this.map.centerAndZoom(offsetCenter, this.currentZoom);
            }
            if (!marker) {
                marker = new T.Marker(lnglat);
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
        setWord(item) {
            this.searchWord = item;
            this.searchMap();
        },
        searchMap() {
            const T = window.T;
            if (!searchObj) {
                searchObj = new T.LocalSearch(this.map, {
                    pageCapacity:5,
                    onSearchComplete: (result) => {
                        this.searchOnResult(result);
                    },
                });
            }
            this.currentPage = 1;
            this.total = 0;
            this.allpage = 1;
            this.pointsList = [];
            searchObj.search(this.searchWord);
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
            // this.currentPoint = item;
            this.setCurrentPoint({
                name: item.name,
                address: item.address,
                lonlat: item.lonlat,
                addressComponent: null,
            });
            this.setPoint(new T.LngLat(g[0], g[1]));
            // this.setPoint(new T.LngLat(item.point.lng, item.point.lat))
        },
        // 逆地理编码
        getLocation() {
            const T = window.T;
            const geocode = new T.Geocoder();
            const that = this;
            geocode.getLocation(that.lnglat, function (result) {
                that.setCurrentPoint({
                    name: result.formatted_address,
                    address: result.formatted_address,
                    lonlat: that.lnglat.lng + "," + that.lnglat.lat,
                    addressComponent: result.addressComponent,
                });
            });
        },
        async setCurrentPoint(data) {
            this.canSubmit = false;
            const { startLonlat, drivingPolicy } = this.options;
            let drives = {};
            if (startLonlat) {
                drives = await this.getDrivingRoute(
                    startLonlat,
                    data.lonlat,
                    drivingPolicy
                );
            }
            this.currentPoint = {
                distance: null,
                duration: null,
                routes: null,
                ...data,
                ...drives,
                startLonlat,
            };
            this.canSubmit = true;
        },
        getDrivingRoute(startLonlat, endLonlat, policy) {
            const T = window.T;
            // const that = this;
            return new Promise((resolve) => {
                const driving = new T.DrivingRoute(this.map, {
                    policy: policy,
                    onSearchComplete: function (result) {
                        const plans = result.getNumPlans();
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
        /** 检查是否处于小程序环境，调用api返回小程序并提交参数 */
        submitMPWebview() {
            const wx = window.wx;
            if (wx && wx.miniProgram) {
                console.log("小程序环境");
                wx.miniProgram.postMessage({ data: this.currentPoint });
                wx.miniProgram.navigateBack;
            }
        },
        submitPoint() {
            console.log(this.currentPoint, "this.currentPoint");
            if (this.mode === "picker") {
                this.$emit("submit", this.currentPoint);
            } else if (this.mode === "webview") {
                this.submitMPWebview();
            }
        },
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
    --font-size: 0.9rem;
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
    height: 1.7rem;
    border: 1px solid #f0f0f0;
    border-radius: 0.2rem;
    padding: 0 0.4rem;
    /* 激活时边框蓝色 */
    outline: none;
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
    font-size: 0.5rem;
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
    color: #999;
    border-color: #999;
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
    border-radius: 0.2rem;
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
</style>