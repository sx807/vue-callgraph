<template>
  <div class="chart-container">
    <el-row :gutter="20">
      <el-col :span="3" :offset="1">
        <el-select v-model="config_graph.ver" filterable placeholder="选择内核版本" @change="ver_change">
          <el-option
            v-for="item in ver_list"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-col>
      <el-col :span="3">
        <el-select v-model="config_graph.plat" placeholder="编译环境" @change="plat_change">
          <el-option
            v-for="item in plat_list"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-col>
      <el-col :span="12">
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

    </el-row>
    <el-row :gutter="20">
      <el-col :offset="1">
        <span>{{ web_url() }}</span>
      </el-col>
    </el-row>

    <FunList v-show="show_graph()" :config="config_graph" />

  </div>
</template>

<script>

import FunList from '@/components/Charts/FunList'

import axios from 'axios'
// import { Loading } from 'element-ui'
// import bus from '@/utils/bus'
// import { mapGetters } from 'vuex'

export default {
  name: 'FunctionTable',
  components: {
    FunList
  },
  data() {
    return {
      url: process.env.VUE_APP_BASE_API,
      // url: 'http://192.168.3.100:7001/api/v1',
      // ver: '',
      ver_list: [],
      plat_list: [],
      path1: '',
      path2: '',
      web_data: {},
      config_graph: {
        ver: '',
        per: '',
        plat: '',
        sou: '',
        tar: ''
      },
      // size_graph: {
      //   w: 1000,
      //   h: 500
      // },
      // g_sel_f: '',
      config_funlist: {
        ver: '',
        plat: '',
        sou: '',
        tar: ''
      },
      path_list: []
      // web_layout: [
      //   { 'x': 0, 'y': 0, 'w': 12, 'h': 5, 'i': '0' },
      //   { 'x': 0, 'y': 1, 'w': 12, 'h': 5, 'i': '1' }
      // ],
      // resizeEvent: function(i, newH, newW, newHPx, newWPx) {
      //   console.log('RESIZE i=' + i + ', H=' + newH + ', W=' + newW + ', H(px)=' + newHPx + ', W(px)=' + newWPx)
      // },
      // G_layout: 'random',
      // G_layout_options: ['random', 'dagre', 'force', 'circular', 'concentric', 'grid']
    }
  },
  created() {
    const _t = this
    // _t.$EventBus.bus.$on('graph/sel/to_url', _t.set_g_sel)
    // _t.$EventBus.bus.$on('graph/path/change', _t.setPath)
    // _t.$EventBus.bus.$on('graph/options', _t.set_per)
    // _t.$EventBus.bus.$on('funlist/show', _t.funlist_conf)
    _t.$EventBus.bus.$on('code/show', _t.show_code)
    // console.log(process.env)
    _t.get_ver_list()
    if (Object.keys(_t.$route.query).length > 0) {
      _t.set_by_url(_t.$route.query)
    }
  },
  destroyed() {
    const _t = this
    _t.$EventBus.bus.$off('code/show')
  },
  mounted() {
    // console.log(this.$route.fullPath)
    // console.log(this.$route.path)
    // const _t = this
  },
  methods: {
    ver_change(val) {
      const _t = this
      console.log('ver ', val, _t.ver_list.findIndex((item) => item.value === val))
      _t.plat_list = _t.ver_list[_t.ver_list.findIndex((item) => item.value === val)].platform
      if (_t.config_graph.plat === '') _t.config_graph.plat = _t.plat_list[0].value
      _t.get_path_list()
      // _t.config_graph.data_source = 'server'
    },
    plat_change() {
      const _t = this
      // _t.setPath({ sou: '', tar: '' })
      _t.get_path_list()
      // _t.config_graph.data_source = 'server'
    },
    // per_change() {
    //   const _t = this
    //   // if (_t.per_select) _t.config_graph.per = 0
    //   // else _t.config_graph.per = 1
    //   // _t.config_graph.data_source = 'server'
    //   // console.log(_t.config_graph.per)
    // },
    // set_per(val) {
    //   const _t = this
    //   _t.config_graph.data_source = 'null'
    //   _t.config_graph.per = val.per
    // },
    // layout_change() {
    //   // const _t = this
    //   // console.log(_t.G_layout)
    //   // this.$EventBus.bus.$emit('graph/layout', _t.layout)
    // },
    setPath(val) {
      const _t = this
      // console.log(val)
      if (val.disable) {
        return
      }
      if (val.data_source) {
        // console.log('val', val)
        // _t.config_graph.data_source = val.data_source
        _t.config_graph.ver = val.ver
        _t.config_graph.plat = val.plat
        // _t.config_graph.per = val.per
        _t.path1 = val.sou
        _t.path2 = val.tar
        _t.config_graph.sou = val.sou
        _t.config_graph.tar = val.tar
        _t.get_path_list()
        return
      }
      if (val.sou) {
        // console.log('sou')
        _t.path1 = val.sou
      }
      if (val.tar) {
        // console.log('tar')
        _t.path2 = val.tar
      }
      _t.path_change('both')
    },
    path_change(item) {
      // console.log(item)
      const _t = this
      const tmp = {
        ver: _t.config_graph.ver,
        plat: _t.config_graph.plat,
        sou: _t.config_graph.sou,
        tar: _t.config_graph.tar,
        per: _t.config_graph.per,
        data_source: 'server'
      }
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
      return this.config_graph.ver !== '' && this.config_graph.plat !== '' && this.config_graph.sou !== '' && this.config_graph.tar !== ''
    },

    show_funlist() {
      return this.config_funlist.ver !== '' && this.config_funlist.sou !== '' && this.config_funlist.tar !== ''
    },
    funlist_conf(item) {
      const _t = this
      // console.log('showlist', item)
      _t.config_funlist = {
        ver: _t.config_graph.ver,
        plat: _t.config_graph.plat,
        sou: item.source,
        tar: item.target
      }
    },

    show_code(path, line) {
      const _t = this
      // console.log('showcode', path, line)
      const ver = _t.ver_list[_t.ver_list.findIndex((item) => item.value === _t.config_graph.ver)]
      // https://elixir.bootlin.com/linux/v4.18.15/source/include/linux/list.h#L627
      let url = 'https://elixir.bootlin.com/linux/v' + ver.label
      const point = path.indexOf('.')
      if (point > 0 && point < path.length - 3) {
        // console.log(path.slice(0, path.lastIndexOf('/')), path.slice(path.lastIndexOf('/')))
        url += '/source'
        _t.show_fun_code(url, path)
        return
      } else if (line > 0) {
        url += '/source' + path + '#L' + line.toString()
      } else {
        url += '/source' + path
      }
      // console.log(url)
      window.open(url)
    },

    show_fun_code(code_url, path) {
      const _t = this
      // axios.defaults.withCredentials = true
      const url = _t.url + '/functions' + path.slice(path.lastIndexOf('/'))
      axios.get(url, { // 还可以直接把参数拼接在url后边
        params: {
          version: _t.config_graph.ver,
          platform: _t.config_graph.plat,
          file: path.slice(1, path.lastIndexOf('/'))
        },
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        // console.log(res.data)
        if (Object.keys(res.data).length > 0) {
          // _t.web_data = res.data
          // console.log('function', res.data)
          // _t.set_web_data(res.data)
          code_url += path.slice(0, path.lastIndexOf('/')) + '#L' + res.data.f_dline.toString()
          window.open(code_url)
        }
      }).catch(function(error) {
        console.log(error)
      })
    },

    get_ver_list() {
      const _t = this
      const url = _t.url + '/options'
      axios.get(url, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        // console.log(res.data)
        if (res.data.length > 0) {
          _t.ver_list = res.data
          if (_t.config_graph.ver !== '') {
            _t.plat_list = _t.ver_list[_t.ver_list.findIndex((item) => item.value === _t.config_graph.ver)].platform
          }
        }
      }).catch(function(error) {
        console.log(error)
      })
    },

    get_path_list() {
      const _t = this
      const url = _t.url + '/options/' + _t.config_graph.ver
      axios.get(url, {
        params: {
          platform: _t.config_graph.plat
        },
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        // console.log(res.data)
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
      const tmp = {
        h: Math.floor(newHPx - 40),
        w: Math.floor(newWPx)
      }
      this.size_graph = tmp
    },

    get_data(key) {
      const _t = this
      // axios.defaults.withCredentials = true
      const url = _t.url + '/graphs/' + key
      axios.get(url, { // 还可以直接把参数拼接在url后边
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        // console.log(res.data)
        if (Object.keys(res.data).length > 0) {
          // _t.web_data = res.data
          // console.log('get', res.data)
          _t.set_web_data(res.data)
        }
      }).catch(function(error) {
        console.log(error)
      })
    },

    // set_g_sel(sel) {
    //   const _t = this
    //   _t.g_sel_f = sel
    // },

    set_web_data(row) {
      const _t = this
      _t.web_data = row.data
      _t.web_data['id'] = row.id
      // console.log('set', row.data)
      // set size
      // _t.size_graph.h = row.size.h
      // _t.size_graph.w = row.size.w
      // set config
      const tmp = {}
      tmp.ver = row.config.version
      tmp.plat = row.config.platform
      tmp.per = row.config.per
      tmp.sou = row.config.source
      tmp.tar = row.config.target
      tmp.data_source = 'external'
      _t.config_graph = tmp
      _t.path1 = tmp.sou
      _t.path2 = tmp.tar
      _t.plat_list = _t.ver_list[_t.ver_list.findIndex((item) => item.value === tmp.ver)].platform
      _t.get_path_list()
    },
    set_by_url(query) {
      const _t = this
      if (query.ver) {
        _t.config_graph.ver = query.ver
        // _t.get_path_list()
      }
      if (query.plat) {
        _t.config_graph.plat = query.plat
        // _t.get_path_list()
      }
      if (query.per) {
        if (query.per === 'true') _t.config_graph.per = true
        else _t.config_graph.per = false
        // _t.get_path_list()
      }
      if (query.ver && query.plat) {
        // console.log('set,url', _t.ver_list)
        // _t.plat_list = _t.ver_list[_t.ver_list.findIndex((item) => item.value === _t.config_graph.ver)].platform
        _t.get_path_list()
      }
      if (query.sou) {
        _t.path1 = _t.config_graph.sou = query.sou
      }
      if (query.tar) {
        _t.path2 = _t.config_graph.tar = query.tar
      }
      if (query.table_sou && query.table_tar) {
        _t.funlist_conf({
          source: query.table_sou,
          target: query.table_tar
        })
      }
    },
    web_url() {
      const _t = this
      const conf = {}
      let url = window.location.href.toString().split('?')[0]
      if (_t.$route.params.hasOwnProperty('pathMatch')) {
        url = url.slice(0, url.lastIndexOf('/'))
      }
      url += '?'
      if (_t.config_graph.ver !== '') {
        conf['ver'] = _t.config_graph.ver
      }
      if (_t.config_graph.plat !== '') {
        conf['plat'] = _t.config_graph.plat
      }
      if (_t.config_graph.per !== '') {
        conf['per'] = _t.config_graph.per
      }
      if (_t.config_graph.sou !== '') {
        conf['sou'] = _t.config_graph.sou
      }
      if (_t.config_graph.tar !== '') {
        conf['tar'] = _t.config_graph.tar
      }
      // if (_t.g_sel_f !== '') {
      //   conf['sel_f'] = _t.g_sel_f
      // }
      if (_t.config_funlist.sou !== '') {
        conf['table_sou'] = _t.config_funlist.sou
      }
      if (_t.config_funlist.tar !== '') {
        conf['table_tar'] = _t.config_funlist.tar
      }
      // if (Object.keys(conf).length > 0)url += '?'
      for (const item in conf) {
        url += item + '=' + conf[item] + '&'
      }
      return url.slice(0, -1)
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
