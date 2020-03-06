<template>
  <div class="chart-container">
    <el-row :gutter="20">
      <el-col :span="4" :offset="2">
        <el-select v-model="ver" filterable placeholder="选择内核版本" @change="ver_change">
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
    <Graph height="100%" width="100%" v-if="show_graph()" :layout="layout" :ver="ver" :sou="sou" :tar="tar"/>
  </div>
</template>

<script>
import Graph from '@/components/Charts/Graph'
import axios from 'axios'
// import bus from '@/utils/bus'
// import { mapGetters } from 'vuex'

export default {
  name: 'GraphChart',
  components: { Graph },
  data() {
    return {
      url: 'http://192.168.3.44:7001/api/v1/',
      ver: '',
      ver_list: [],
      path1: '',
      path2: '',
      sou: '',
      tar: '',
      loading: false,
      show: false,
      path_list: [],
      layout: 'random',
      layout_options: ['random', 'circular', 'concentric', 'grid']
    }
  },
  created() {
    const _t = this
    _t.$EventBus.bus.$on('graph/path/change', _t.setPath)
  },
  destroyed() {
    const _t = this
    _t.$EventBus.bus.$off('graph/path/change')
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
      switch (item) {
        case 'sou':
          this.sou = this.path1
          break
        case 'tar':
          this.tar = this.path2
          break
        case 'both':
          this.sou = this.path1
          this.tar = this.path2
          break
      }
    },
    show_graph() {
      if (this.ver !== '' && this.sou !== '' && this.tar !== '') {
        return true
      } else return false
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
      const url = _t.url + 'options/' + _t.ver
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
    height: calc(100vh - 84px);
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
