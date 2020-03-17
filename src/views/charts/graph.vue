<template>
  <div class="chart-container">
    <el-row :gutter="20">
      <el-col :span="4" :offset="2">
        <el-select v-model="config.ver" filterable placeholder="选择内核版本" @change="ver_change">
          <el-option
            v-for="item in ver_list"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select
          v-model="path1"
          filterable
          remote
          reserve-keyword
          placeholder="请输入源路径"
          @change="path_change('sou')">
          <el-option
            v-for="item in path_list"
            :key="item.value"
            :label="item.value"
            :value="item.value">
          </el-option>
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select
          v-model="path2"
          filterable
          remote
          reserve-keyword
          placeholder="请输入目标路径"
          @change="path_change('tar')">
          <el-option
            v-for="item in path_list"
            :key="item.value"
            :label="item.value"
            :value="item.value">
          </el-option>
        </el-select>
      </el-col>
      <el-col :span="9">
        <label class="radio-label">Layout:  </label>
        <el-select v-model="layout" style="width:120px;" @change="layout_change">
          <el-option
            v-for="item in layout_options"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <!-- <el-button type="primary" round>生成调用图</el-button> -->
      </el-col>
    </el-row>
    <Graph v-if="show_graph()" :layout="layout" :config="config"/>
    <FunList :config="config_funlist" v-show="funlist_show"/>
  </div>
</template>

<script>
import Graph from '@/components/Charts/Graph'
import FunList from '@/components/Charts/FunList'
import axios from 'axios'
// import bus from '@/utils/bus'
// import { mapGetters } from 'vuex'

export default {
  name: 'GraphChart',
  components: {
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
      config: {
        ver: '',
        sou: '',
        tar: ''
      },
      config_funlist: {
        ver: '',
        sou: '',
        tar: ''
      },
      funlist_show: false,
      sou: '',
      tar: '',
      show: false,
      path_list: [],
      layout: 'random',
      layout_options: ['random', 'circular', 'concentric', 'grid']
    }
  },
  created() {
    const _t = this
    _t.$EventBus.bus.$on('graph/path/change', _t.setPath)
    _t.$EventBus.bus.$on('funlist/show', _t.show_funlist)
  },
  destroyed() {
    const _t = this
    _t.$EventBus.bus.$off('graph/path/change')
    _t.$EventBus.bus.$off('funlist/show')
  },
  mounted() {
    this.get_ver_list()
  },
  methods: {
    ver_change(item) {
      this.get_path_list()
    },

    // remoteMethod(query) {
    //   if (query !== '') {
    //     this.loading = true
    //     for (const item in this.path_all_list) {
    //       item.value.index
    //     }
    //     this.loading = false
    //   } else {
    //     this.path_list = []
    //   }
    // },
    layout_change() {
      const _t = this
      console.log(_t.layout)
      this.$EventBus.bus.$emit('graph/layout', _t.layout)
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
      const tmp = this.config
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
      this.config = tmp
      // console.log('pathchange', this.sou, this.tar)
      // this.$EventBus.bus.$emit('graph/path')
    },
    show_graph() {
      if (this.config.ver !== '' && this.config.sou !== '' && this.config.tar !== '') {
        return true
      } else return false
    },

    show_funlist(item) {
      const _t = this
      console.log('showlist', item)
      _t.funlist_show = true
      const tmp = {
        ver: _t.config.ver,
        sou: item.source,
        tar: item.target
      }
      _t.config_funlist = tmp
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
      const url = _t.url + 'options/' + _t.config.ver
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
