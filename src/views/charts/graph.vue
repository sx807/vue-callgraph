<template>
  <div class="chart-container">
    <el-row :gutter="20">
      <el-col :span="4" :offset="2">
        <el-select v-model="config_graph.ver" filterable placeholder="选择内核版本" @change="ver_change">
          <el-option
            v-for="item in ver_list"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select
          v-model="path1"
          filterable
          remote
          reserve-keyword
          placeholder="请输入源路径"
          @change="path_change('sou')"
        >
          <el-option
            v-for="item in path_list"
            :key="item.value"
            :label="item.value"
            :value="item.value"
          />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select
          v-model="path2"
          filterable
          remote
          reserve-keyword
          placeholder="请输入目标路径"
          @change="path_change('tar')"
        >
          <el-option
            v-for="item in path_list"
            :key="item.value"
            :label="item.value"
            :value="item.value"
          />
        </el-select>
      </el-col>
      <el-col :span="9">
        <label class="radio-label">Layout:  </label>
        <el-select v-model="G_layout" style="width:120px;" @change="layout_change">
          <el-option
            v-for="item in G_layout_options"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <!-- <el-button type="primary" round>生成调用图</el-button> -->
      </el-col>
    </el-row>
    <grid-layout
      :layout.sync="web_layout"
      :col-num="12"
      :row-height="100"
      :is-draggable="true"
      :is-resizable="true"
      :vertical-compact="true"
      :margin="[10, 10]"
      :use-css-transforms="true"
    >
      <grid-item
        v-if="show_graph()"
        :x="web_layout[0].x"
        :y="web_layout[0].y"
        :w="web_layout[0].w"
        :min-w="6"
        :max-w="12"
        :h="web_layout[0].h"
        :min-h="5"
        :max-h="6"
        :i="web_layout[0].i"
        :is-draggable="false"
        @resized="resizedGraphEvent"
      >
<!--        <i class="el-icon-delete"></i>-->
        <Graph :layout="G_layout" :config="config_graph" :ex_data="web_data"/>
      </grid-item>
      <grid-item
        v-show="funlist_show"
        :x="web_layout[1].x"
        :y="web_layout[1].y"
        :w="web_layout[1].w"
        :min-w="3"
        :max-w="12"
        :h="web_layout[1].h"
        :min-h="5"
        :max-h="5"
        :i="web_layout[1].i"
      >
        <FunList :config="config_funlist" />
      </grid-item>
    </grid-layout>
  </div>
</template>

<script>
import Graph from '@/components/Charts/Graph'
import FunList from '@/components/Charts/FunList'
import VueGridLayout from 'vue-grid-layout'
import axios from 'axios'
// import { Loading } from 'element-ui'
// import bus from '@/utils/bus'
// import { mapGetters } from 'vuex'

export default {
  name: 'GraphChart',
  components: {
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem,
    Graph,
    FunList
  },
  data() {
    return {
      url: 'http://192.168.3.44:7001/api/v1/',
      // ver: '',
      ver_list: [],
      path1: '',
      path2: '',
      web_data: {},
      config_graph: {
        ver: '',
        sou: '',
        tar: '',
        ex: false,
        w: 1000,
        h: 500
      },
      config_funlist: {
        ver: '',
        sou: '',
        tar: ''
      },
      funlist_show: false,
      show: false,
      path_list: [],
      web_layout: [
        { 'x': 0, 'y': 0, 'w': 12, 'h': 5, 'i': '0' },
        { 'x': 0, 'y': 1, 'w': 12, 'h': 5, 'i': '1' }
      ],
      // resizeEvent: function(i, newH, newW, newHPx, newWPx) {
      //   console.log('RESIZE i=' + i + ', H=' + newH + ', W=' + newW + ', H(px)=' + newHPx + ', W(px)=' + newWPx)
      // },
      G_layout: 'random',
      G_layout_options: ['random', 'fruchterman', 'force', 'circular', 'concentric', 'grid']
    }
  },
  created() {
    const _t = this
    _t.$EventBus.bus.$on('graph/path/change', _t.setPath)
    _t.$EventBus.bus.$on('funlist/show', _t.show_funlist)
    _t.$EventBus.bus.$on('code/show', _t.show_code)
    console.log(this.$route.params)
    _t.get_ver_list()
    if (_t.$route.params.hasOwnProperty('pathMatch')) {
      _t.get_data(this.$route.params.pathMatch)
    }
    if (_t.$route.query.hasOwnProperty('ver')) {
      _t.config_graph.ver = _t.$route.query.ver
      this.get_path_list()
    }
    if (_t.$route.query.hasOwnProperty('sou')) {
      _t.config_graph.sou = _t.$route.query.sou
      _t.path1 = _t.$route.query.sou
    }
    if (_t.$route.query.hasOwnProperty('tar')) {
      _t.config_graph.tar = _t.$route.query.tar
      _t.path2 = _t.$route.query.tar
    }
    // if (_t.$route.query.hasOwnProperty('ver'))
  },
  destroyed() {
    const _t = this
    _t.$EventBus.bus.$off('graph/path/change')
    _t.$EventBus.bus.$off('funlist/show')
    _t.$EventBus.bus.$off('code/show')
  },
  mounted() {
    // console.log(this.$route.fullPath)
    // console.log(this.$route.path)
    // const _t = this
  },
  methods: {
    ver_change(item) {
      this.get_path_list()
    },
    layout_change() {
      const _t = this
      console.log(_t.G_layout)
      // this.$EventBus.bus.$emit('graph/layout', _t.layout)
    },
    setPath(val) {
      const _t = this
      // console.log(val)
      if (val.disable) {
        return
      }
      if (val.sou) {
        // console.log('sou')
        this.path1 = val.sou
      }
      if (val.tar) {
        // console.log('tar')
        this.path2 = val.tar
      }
      _t.path_change('both')
    },
    path_change(item) {
      // console.log(item)
      const tmp = this.config_graph
      switch (item) {
        case 'sou':
          tmp.sou = this.path1
          break
        case 'tar':
          tmp.tar = this.path2
          break
        case 'both':
          tmp.sou = this.path1
          tmp.tar = this.path2
          break
      }
      this.config_graph = tmp
      // console.log('pathchange', this.sou, this.tar)
      // this.$EventBus.bus.$emit('graph/path')
    },
    show_graph() {
      if (this.config_graph.ver !== '' && this.config_graph.sou !== '' && this.config_graph.tar !== '') {
        return true
      } else return false
    },

    show_funlist(item) {
      const _t = this
      console.log('showlist', item)
      _t.funlist_show = true
      const tmp = {
        ver: _t.config_graph.ver,
        sou: item.source,
        tar: item.target
      }
      _t.config_funlist = tmp
    },

    show_code(path, line) {
      const _t = this
      console.log('showcode', path, line)
      const ver = _t.ver_list[_t.ver_list.findIndex((item) => item.value === _t.config_graph.ver)]
      // https://elixir.bootlin.com/linux/v4.18.15/source/include/linux/list.h#L627
      let url = 'https://elixir.bootlin.com/linux/v' + ver.label
      const point = path.indexOf('.')
      if (point > 0 && point < path.length - 3) {
        url += '/ident' + path.slice(path.lastIndexOf('/'))
      } else if (line > 0) {
        url += '/source' + path + '#L' + line.toString()
      } else {
        url += '/source' + path
      }
      // console.log(url)
      window.open(url)
    },

    get_ver_list() {
      const _t = this
      const url = _t.url + 'options'
      axios.get(url, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        console.log(res.data)
        if (res.data.length > 0) {
          _t.ver_list = res.data
        }
      }).catch(function(error) {
        console.log(error)
      })
    },

    get_path_list() {
      const _t = this
      const url = _t.url + 'options/' + _t.config_graph.ver
      axios.get(url, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        console.log(res.data)
        if (res.data.length > 0) {
          _t.path_list = res.data.map(item => {
            return { value: item }
          })
        }
        _t.path_list.unshift({ value: '/' })
      }).catch(function(error) {
        console.log(error)
      })
    },

    // resizedTableEvent(i, newH, newW, newHPx, newWPx) {
    //   // console.log('RESIZE i=' + i + ', H=' + newH + ', W=' + newW + ', H(px)=' + newHPx + ', W(px)=' + newWPx)
    //   this.config_funlist.h = Math.floor(newHPx)
    // },
    resizedGraphEvent(i, newH, newW, newHPx, newWPx) {
      // console.log('RESIZE i=' + i + ', H=' + newH + ', W=' + newW + ', H(px)=' + newHPx + ', W(px)=' + newWPx)
      this.config_graph.h = Math.floor(newHPx - 40)
      this.config_graph.w = Math.floor(newWPx)
    },

    get_data(key) {
      const _t = this
      // axios.defaults.withCredentials = true
      const url = 'http://192.168.3.44:7001/api/v1/graphs/' + key
      axios.get(url, { // 还可以直接把参数拼接在url后边
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        console.log(res.data)
        if (Object.keys(res.data).length > 0) {
          // _t.web_data = res.data
          // console.log('get', res.data)
          _t.set_web_data(res.data)
        }
      }).catch(function(error) {
        console.log(error)
      })
    },
    set_web_data(row) {
      const _t = this
      _t.web_data = row.data
      console.log('set', row.data)
      // set config
      const tmp = {}
      tmp.ver = row.config.version
      tmp.sou = row.config.source
      tmp.tar = row.config.target
      tmp.ex = true
      tmp.w = _t.config_graph.w
      tmp.h = _t.config_graph.h
      _t.config_graph = tmp
      _t.path1 = tmp.sou
      _t.path2 = tmp.tar
    }
  }
}
</script>

<style scoped>
  .chart-container{
    position: relative;
    width: 100%;
  }
  .radio-label {
    font-size: 14px;
    color: #606266;
    line-height: 40px;
    padding: 0 12px 0 30px;
  }
  .el-row {
    margin-top: 20px;
    margin-bottom: 20px;
  }
  .el-col {
    border-radius: 4px;
  }
  .bg-purple-dark {
    background: #99a9bf;
  }
  .bg-purple {
    background: #d3dce6;
  }
  .bg-purple-light {
    background: #e5e9f2;
  }
  .grid-content {
    border-radius: 4px;
    min-height: 36px;
  }
  .row-bg {
    padding: 10px 0;
    background-color: #f9fafc;
  }
</style>
