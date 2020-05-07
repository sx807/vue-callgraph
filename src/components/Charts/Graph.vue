<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="3" :offset="1" v-for="(item,key) in sel" :key="key">
        <el-switch
          v-model="sel[key].value"
          :active-text="item.label"
          @change="select_edge()"
        />
      </el-col>
    </el-row>
    <ContextMenu />
    <div id="graphChart" ref="graphChart" class="graphChart" style="height:100%; width:100%" />
    <el-dialog
      title="分享链接"
      :modal=false
      :visible.sync="share_dialog"
      :before-close="handleClose">
      <span>{{share_url}}</span>
      <span slot="footer" class="dialog-footer">
<!--        <el-button @click="share_dialog = false">取 消</el-button>-->
        <el-button type="primary" @click="share_dialog = false">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import G6 from '@antv/g6'
import insertCss from 'insert-css'
import axios from 'axios'
import { Loading } from 'element-ui'
// import Clipboard from 'clipboard'
import ContextMenu from './ContextMenu'
// import bus from '@/utils/bus'
// import { mapGetters } from 'vuex'
const Minimap = require('@antv/g6/build/minimap')
const colors = ['#BDD2FD', '#BDEFDB', '#C2C8D5', '#FBE5A2', '#F6C3B7', '#B6E3F5', '#D3C6EA', '#FFD8B8', '#AAD8D8', '#FFD6E7']
const strokes = ['#5B8FF9', '#5AD8A6', '#5D7092', '#F6BD16', '#E8684A', '#6DC8EC', '#9270CA', '#FF9D4D', '#269A99', '#FF99C3']

insertCss(`
  .g6-tooltip {
    border: 1px solid #e2e2e2;
    border-radius: 4px;
    font-size: 12px;
    color: #545454;
    background-color: rgba(255, 255, 255, 0.9);
    padding: 10px 8px;
    box-shadow: rgb(174, 174, 174) 0px 0px 10px;
  }`)

export default {
  name: 'Graph',
  components: {
    ContextMenu
  },
  props: {
    id: {
      type: String,
      default: 'chart'
    },
    layout: {
      type: String,
      default: 'random'
    },
    size: {
      type: Object,
      default: function() {
        return {
          w: 1000,
          h: 500
        }
      }
    },
    config: {
      type: Object,
      default: function() {
        return {
          var: '',
          sou: '',
          tar: '',
          per: 1,
        }
      }
    },
    ex_data: {
      type: Object,
      default: function() {
        return {}
      }
    }
  },
  data() {
    return {
      // url: 'http://192.168.3.100:7001/api/v1/graphs',
      url: process.env.VUE_APP_BASE_API + '/graphs',
      graph: null,
      minimap: null,
      graph_id: '',
      options: {
        per: 1,
        expanded: ''
      },
      graph_config: {},
      backup_data: {
        id: '',
        layout: '',
        data: {},
        config: {}
      },
      data: {
        nodes: [],
        edges: [],
        groups: []
      },
      graph_w: 1000,
      graph_h: 500,
      sel: {
        s_to_t: {
          value: true,
          label: 'sou->tar'
        },
        t_to_s: {
          value: true,
          label: 'tar->sou'
        },
        s_to_s: {
          value: true,
          label: 'sou->sou'
        },
        t_to_t: {
          value: true,
          label: 'tar->tar'
        },
        o_to: {
          value: true,
          label: 'other->'
        },
        to_o: {
          value: true,
          label: '->other'
        }
      },
      contextMenuStyle: {},
      share_dialog: false,
      share_url: ''
    }
  },
  watch: {
    size: {
      handler(newValue, oldValue) {
        const _t = this
        _t.graph_h = newValue.h
        _t.graph_w = newValue.w
        _t.graph.changeSize(_t.graph_w, _t.graph_h)
        _t.graph.fitView()
      },
      deep: true
    },
    config: {
      handler(newValue, oldValue) {
        const _t = this
        console.log('graph config change', newValue)
        if (newValue.data_source === 'server') {
          let per = 1
          _t.options.expanded = ''
          _t.backup()
          _t.graph_config = JSON.parse(JSON.stringify(newValue))
          if (newValue.per) per = 0
          _t.set_options({ per: per })
          _t.get_data('new')
        }
      },
      deep: true
    },
    layout(val) {
      this.updateLayout(val)
    }
  },
  created() {
    const _t = this
    _t.$EventBus.bus.$on('graph/delete', _t.delete_node)
    _t.$EventBus.bus.$on('graph/expand', _t.expand_node)
    _t.$EventBus.bus.$on('graph/layout', _t.updateLayout)
    _t.$EventBus.bus.$on('graph/options', _t.set_options)
    _t.$EventBus.bus.$on('graph/back', _t.back_graph)
    _t.$EventBus.bus.$on('graph/post', _t.save_graph)
    // this.$nextTick(function() {
    //   console.log('next', _t.$refs.graphChart.offsetWidth)
    // })
    if (_t.$route.query.hasOwnProperty('sel_f')) {
      _t.sel_load(_t.$route.query.sel_f)
    }
  },
  destroyed() {
    const _t = this
    _t.$EventBus.bus.$off('graph/delete')
    _t.$EventBus.bus.$off('graph/expand')
    _t.$EventBus.bus.$off('graph/layout')
    _t.$EventBus.bus.$off('graph/option')
    _t.$EventBus.bus.$off('graph/back')
    _t.$EventBus.bus.$off('graph/post')
  },
  mounted() {
    const _t = this
    // console.log('mounted', _t.$refs.graphChart.offsetWidth)
    _t.graph_w = _t.$refs.graphChart.offsetWidth
    console.log(_t.config.per, _t.graph_config.per)
    _t.graph_config = JSON.parse(JSON.stringify(_t.config))
    console.log(_t.config.per, _t.graph_config.per)
    _t.set_options({ per: _t.config.per ? 0 : 1 })
    _t.initChart()
    console.log('mounted', _t.config, _t.graph_config)
    // console.log('mounted', _t.$refs.graphChart.offsetHeight, _t.$refs.graphChart.offsetWidth)
    if (_t.config.data_source === 'external') {
      _t.get_data('external')
    } else {
      _t.options.expanded = ''
      _t.get_data('new')
    }
  },
  methods: {
    initChart() {
      const _t = this
      // const el = _t.$el
      // const mountNode = el.querySelector('#mountNode')
      _t.minimap = new Minimap({
        size: [200, 100],
        className: 'minimap',
        type: 'keyShape'
      })
      _t.graph = new G6.Graph({
        container: 'graphChart',
        width: _t.graph_w,
        height: _t.graph_h,
        fitView: true,
        autoPaint: true,
        animate: false,
        minZoom: 0.5,
        maxZoom: 3,
        plugins: [_t.minimap],
        modes: {
          default: [
            'drag-canvas',
            'zoom-canvas',
            // 'drag-group',
            // 'collapse-expand-group',
            'drag-node',
            {
              type: 'tooltip',
              formatText(model) {
                return model.id
              }
            },
            {
              type: 'edge-tooltip',
              formatText(model) {
                return '调用次数：' + model.sourceWeight + '<br/>来源：' + model.source + '<br/>去向：' + model.target
              }
            }
          ]
        },
        layout: {
          type: _t.layout
        },
        defaultNode: {
          shape: 'ellipse',
          size: [30, 15],
          color: 'steelblue',
          labelCfg: {
            style: {
              fill: '#787878',
              fontSize: 12
            }
          }
        },
        defaultEdge: {
          shape: 'quadratic',
          size: 2
        },
        nodeStateStyles: {
        // nodeStyle: {
          default: {
            lineWidth: 1,
            fill: 'steelblue'
          },
          highlight: {
            opacity: 1
          },
          dark: {
            opacity: 0.2
          }
        },
        edgeStateStyles: {
        // edgeStyle: {
          default: {
            opacity: 0.2,
            // stroke: '#e2e2e2',
            lineAppendWidth: 3
          },
          highlight: {
            // stroke: '#999'
            opacity: 1
          }
        }
      })
      _t.graph.on('node:mouseenter', function(e) {
        var item = e.item
        // console.log(e)
        _t.graph.setAutoPaint(false)
        _t.graph.getNodes().forEach(function(node) {
          _t.graph.clearItemStates(node)
          _t.graph.setItemState(node, 'dark', true)
        })
        _t.graph.setItemState(item, 'dark', false)
        _t.graph.setItemState(item, 'highlight', true)
        _t.graph.getEdges().forEach(function(edge) {
          if (edge.getSource() === item) {
            _t.graph.setItemState(edge.getTarget(), 'dark', false)
            _t.graph.setItemState(edge.getTarget(), 'highlight', true)
            _t.graph.setItemState(edge, 'highlight', true)
            edge.toFront()
          } else if (edge.getTarget() === item) {
            _t.graph.setItemState(edge.getSource(), 'dark', false)
            _t.graph.setItemState(edge.getSource(), 'highlight', true)
            _t.graph.setItemState(edge, 'highlight', true)
            edge.toFront()
          } else {
            _t.graph.setItemState(edge, 'highlight', false)
          }
        })
        _t.graph.paint()
        _t.graph.setAutoPaint(true)
      })
      _t.graph.on('edge:mouseenter', function(e) {
        var item = e.item
        // console.log(e)
        _t.graph.setAutoPaint(false)
        _t.graph.getNodes().forEach(function(node) {
          _t.graph.clearItemStates(node)
          _t.graph.setItemState(node, 'dark', true)
        })
        _t.graph.setItemState(item, 'highlight', true)
        _t.graph.setItemState(item.getTarget(), 'dark', false)
        _t.graph.setItemState(item.getTarget(), 'highlight', true)
        _t.graph.setItemState(item.getSource(), 'dark', false)
        _t.graph.setItemState(item.getSource(), 'highlight', true)
        _t.graph.paint()
        _t.graph.setAutoPaint(true)
      })
      _t.graph.on('node:mouseleave', _t.clearAllStats)
      _t.graph.on('edge:mouseleave', _t.clearAllStats)
      // _t.graph.on('canvas:click', _t.clearAllStats)
      _t.graph.on('node:contextmenu', evt => {
        console.log(evt.item.getBBox())
        this.$EventBus.bus.$emit('graph/contextmenu/open', evt)
      })
      _t.graph.on('edge:contextmenu', evt => {
        // console.log(evt)
        this.$EventBus.bus.$emit('graph/contextmenu/open', evt)
      })
      _t.graph.on('canvas:contextmenu', evt => {
        // console.log(evt)
        this.$EventBus.bus.$emit('graph/contextmenu/open', evt)
      })
      _t.graph.on('canvas:click', () => {
        _t.clearAllStats()
        _t.$EventBus.bus.$emit('graph/contextmenu/close')
      })
    },
    clearAllStats() {
      const _t = this
      _t.graph.setAutoPaint(false)
      _t.graph.getNodes().forEach(function(node) {
        _t.graph.clearItemStates(node)
      })
      _t.graph.getEdges().forEach(function(edge) {
        _t.graph.clearItemStates(edge)
      })
      _t.graph.paint()
      _t.graph.setAutoPaint(true)
    },
    set_options(val) {
      console.log('set', val)
      const keys = Object.keys(val)
      for (const key of keys) {
        this.options[key] = val[key]
      }
    },
    check_status() {
      const _t = this
      let ex_nodes = 0
      if (_t.options.expanded !== '') {
        ex_nodes = _t.options.expanded.split(',').length
      }
      // if (ex_nodes >= 1 && ex_nodes < 3) {
      //   this.$message.warning('多个展开节点 不会显示展开点之间的边！')
      // }
      if (_t.options.hasOwnProperty('expand') &&
        _t.options.expand.lastIndexOf('.') > 0 &&
        _t.options.expand.lastIndexOf('.') < _t.options.expand.length - 2) {
        this.$message.error('错误 函数节点不可展开！')
        const tmp = _t.options.expanded
        _t.options = {
          expanded: tmp
        }
        return false
      }
      if (ex_nodes >= 3) {
        this.$message.error('错误 展开节点达到上限(3)！')
        const tmp = _t.options.expanded
        _t.options = {
          expanded: tmp
        }
        return false
      }
      return true
    },
    get_data(type) {
      const _t = this
      if (!_t.check_status()) return
      console.log('get_data', _t.graph_config)
      const loadingInstance = Loading.service({ target: '#graphChart' })
      const config = {
        version: _t.graph_config.ver,
        platform: _t.graph_config.plat,
        source: _t.graph_config.sou,
        target: _t.graph_config.tar
      }
      for (const key in _t.options) {
        if (_t.options[key] !== '') {
          config[key] = _t.options[key]
        }
      }
      if (type === 'external') {
        const tmp = JSON.parse(JSON.stringify(_t.handle_data(_t.ex_data)))
        // console.log('tmp', tmp)
        _t.graph_id = tmp.id
        _t.data.nodes = tmp.nodes
        _t.data.edges = tmp.edges
        _t.graph.setAutoPaint(false)
        _t.graph.data({
          nodes: _t.data.nodes,
          edges: _t.data.edges
        })
        _t.graph.render()
        for (const node of _t.ex_data.nodes) {
          _t.graph.updateItem(node.id, { x: node.x, y: node.y })
        }
        // _t.select_edge()
        _t.sel_load(tmp.sel)
        // _t.clearAllStats()
        _t.graph.paint()
        _t.graph.setAutoPaint(true)
        _t.graph.fitView()
        loadingInstance.close()
      } else {
        // axios.defaults.withCredentials = true
        axios.get(_t.url, { // 还可以直接把参数拼接在url后边
          // axios.get('./public/data.json', {
          params: config,
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
          }
        }).then(function(res) {
          // console.log(res.data)
          // console.log('get', Cookies.get('csrfToken'))
          if (res.data.nodes.length > 0) {
            _t.graph_id = res.data.id
            const tmp = _t.handle_data(res.data)
            const expanded = []
            for (const ex of _t.options.expanded.split(',')) {
              if (ex !== '') expanded.push(ex)
            }
            if (type === 'new') {
              _t.data = tmp
            }
            if (type === 'add') {
              _t.backup()
              _t.data.nodes = _t.data.nodes.concat(tmp.nodes)
              _t.data.edges = _t.data.edges.concat(tmp.edges)
              // console.log(_t.data.nodes)
              expanded.push(_t.options.expand)
            }
            _t.graph.data({
              // groups: _t.data.groups,
              nodes: _t.data.nodes,
              edges: _t.data.edges
            })
            // console.log(expanded)
            _t.options = {
              expanded: expanded.join()
            }
            _t.graph.render()
            _t.graph.fitView()
            _t.select_edge()
          }
          loadingInstance.close()
        }).catch(function(error) {
          loadingInstance.close()
          this.$message.error(error)
          const tmp = _t.options.expanded
          _t.options = {
            expanded: tmp
          }
          console.log(error)
        })
      }
    },
    handle_data(data) {
      data.nodes.map(function(node) {
        node.label = node.id
        if (!node.style) {
          node.style = {}
        }
        node.style.fill = colors[node.type % colors.length]
        node.style.stroke = strokes[node.type % strokes.length]
      })
      data.edges.map(function(edge) {
        if (!edge.style) {
          edge.style = {}
        }
        edge.style.stroke = strokes[edge.type % strokes.length]
      })
      return data
    },
    select_edge() {
      const _t = this
      _t.graph.setAutoPaint(false)
      // _t.clearAllStats()
      _t.graph.getEdges().forEach(function(edge) {
        // console.log(edge.getSource().getModel().type)
        let show = true
        const sou_type = edge.getSource().getModel().type
        const tar_type = edge.getTarget().getModel().type
        if (sou_type === 2 && tar_type === 2) {
          show = _t.sel['o_to'].value && _t.sel['to_o'].value
        } else if (sou_type === 2) {
          show = _t.sel['o_to'].value
        } else if (tar_type === 2) {
          show = _t.sel['to_o'].value
        } else if (sou_type === 0 && tar_type === 1) {
          show = _t.sel['s_to_t'].value
        } else if (sou_type === 1 && tar_type === 0) {
          show = _t.sel['t_to_s'].value
        } else if (sou_type === 0 &&
          tar_type === 0) {
          show = _t.sel['s_to_s'].value
        } else if (sou_type === 1 && tar_type === 1) {
          show = _t.sel['t_to_t'].value
        }
        if (show) {
          _t.graph.showItem(edge)
        } else {
          _t.graph.hideItem(edge)
        }
      })
      _t.$EventBus.bus.$emit('graph/sel/to_url', _t.sel_save())
      _t.graph.paint()
      _t.graph.setAutoPaint(true)
    },
    sel_save() {
      const _t = this
      const tmp = []
      for (const key in _t.sel) {
        if (!_t.sel[key].value) tmp.push(key)
      }
      return tmp.toString()
    },
    sel_load(str) {
      const _t = this
      if (str.length > 0) {
        const list = str.toString().split(',')
        if (list.length > 0) {
          for (const key of list) {
            // console.log(key)
            _t.sel[key].value = false
          }
          _t.select_edge()
        }
      }
    },
    backup() {
      const _t = this
      _t.backup_data.id = _t.graph_id
      _t.backup_data.layout = _t.layout
      _t.backup_data.config = _t.graph_config
      _t.backup_data.sel = _t.sel_save()
      _t.backup_data.expanded = _t.options.expanded
      const row = _t.graph.save()
      _t.backup_data.data = {
        nodes: [],
        edges: []
      }
      for (const node of row.nodes) {
        const tmp = {}
        tmp.id = node.id
        tmp.type = node.type
        tmp.x = Math.floor(node.x)
        tmp.y = Math.floor(node.y)
        _t.backup_data.data.nodes.push(tmp)
      }
      for (const edge of row.edges) {
        const tmp = {}
        tmp.source = edge.source
        tmp.target = edge.target
        tmp.sourceWeight = edge.sourceWeight
        tmp.type = edge.type
        _t.backup_data.data.edges.push(tmp)
      }
      console.log(_t.backup_data)
    },
    back_graph(item) {
      const _t = this
      if (Object.keys(_t.backup_data.data).length > 0) {
        _t.graph.setAutoPaint(false)
        // graph id
        _t.graph_id = _t.backup_data.id
        // config
        _t.graph_config = _t.backup_data.config
        _t.options.expanded = _t.backup_data.expanded
        // data
        _t.data = JSON.parse(JSON.stringify(_t.handle_data(_t.backup_data.data)))
        _t.graph.setAutoPaint(false)
        _t.graph.data({
          nodes: _t.data.nodes,
          edges: _t.data.edges
        })
        _t.graph.render()
        for (const node of _t.backup_data.data.nodes) {
          _t.graph.updateItem(node.id, { x: node.x, y: node.y })
        }
        // sel edges
        _t.sel_load(_t.backup_data.sel)
        _t.graph.paint()
        _t.graph.fitView()
        _t.graph.setAutoPaint(true)
        console.log('back_graph', _t.graph_config)
        _t.$EventBus.bus.$emit('graph/path/change', {
          ver: _t.backup_data.config.ver,
          plat: _t.backup_data.config.plat,
          sou: _t.backup_data.config.sou,
          tar: _t.backup_data.config.tar,
          per: _t.backup_data.config.per,
          data_source: 'backup'
        })
      }
    },
    save_graph() {
      const _t = this
      const row = _t.graph.save()
      const data = {
        sel: _t.sel_save(),
        nodes: [],
        edges: []
      }
      for (const node of row.nodes) {
        const tmp = {}
        tmp.id = node.id
        tmp.type = node.type
        tmp.x = Math.floor(node.x)
        tmp.y = Math.floor(node.y)
        data.nodes.push(tmp)
      }
      for (const edge of row.edges) {
        const tmp = {}
        tmp.source = edge.source
        tmp.target = edge.target
        tmp.sourceWeight = edge.sourceWeight
        tmp.type = edge.type
        data.edges.push(tmp)
      }
      axios.post(_t.url, {
        config: {
          version: _t.graph_config.ver,
          platform: _t.graph_config.plat,
          source: _t.graph_config.sou,
          target: _t.graph_config.tar,
          per: _t.graph_config.per,
        },
        data: data
      }, {
        headers: {
          // 'x-csrf-token': Cookies.get('csrfToken'),
          'Content-Type': 'application/json;charset=utf-8'
          // 'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        // console.log(res.data)
        _t.share_url = window.location.href.toString().split('#')[0] + '#/charts/graph/' + res.data.share_key
        _t.share_dialog = true
      }).catch(function(error) {
        console.log(error)
      })
    },
    delete_node(node) {
      const _t = this
      _t.graph.removeItem(node)
      _t.clearAllStats()
    },
    expand_node(node) {
      const _t = this
      const nodeId = node.getModel().id
      const tmp = []
      const index = _t.data.nodes.findIndex((node) => node.id === nodeId)
      _t.data.nodes.splice(index, 1)
      // console.log(_t.data.nodes)
      for (const edge of _t.data.edges) {
        if (edge.source !== nodeId && edge.target !== nodeId) {
          tmp.push(edge)
        }
      }
      _t.data.edges = tmp
      _t.set_options({
        id: _t.graph_id,
        expand: nodeId
      })
      _t.get_data('add')
      // console.log('node', _t.graph.getNodes(), 'edge', _t.graph.getEdges())
    },
    updateLayout(layout) {
      const _t = this
      // console.log(_t.layout)
      _t.graph.updateLayout({
        width: 1200,
        height: 600,
        type: layout,
        preventOverlap: true,
        nodeSize: 50,
        linkDistance: 50
      })
      _t.graph.fitView()
    },
    share_copy(url) {
      this.$alert(url, '分享链接', {
        confirmButtonText: '确定'
        // callback: action => {
        //   this.$message({
        //     type: 'info',
        //     message: `action: ${ action }`
        //   })
        // }
      })
      // this.$msgbox({
      //   title: '分享链接',
      //   message: url,
      //   showCancelButton: true,
      //   confirmButtonText: '复制',
      //   cancelButtonText: '取消',
      //   beforeClose: (action, instance, done) => {
      //     if (action === 'confirm') {
      //       const clipboard = new Clipboard('.code-path .el-button', {
      //         text: function() {
      //           return url
      //         }
      //       })
      //       clipboard.on('success', function() {
      //         this.$message.success('复制成功！')
      //         done()
      //       })
      //       clipboard.on('error', function() {
      //         this.$message.error('复制失败！')
      //       })
      //     } else {
      //       done()
      //     }
      //     // if (action === 'confirm') {
      //     //   instance.confirmButtonLoading = true
      //     //   instance.confirmButtonText = '执行中...'
      //     //   setTimeout(() => {
      //     //     done()
      //     //     setTimeout(() => {
      //     //       instance.confirmButtonLoading = false
      //     //     }, 300)
      //     //   }, 3000)
      //     // } else {
      //     //   done()
      //     // }
      //   }
      // }).then(action => {
      //   this.$message({
      //     type: 'info',
      //     message: 'action: ' + action
      //   })
      // })
    },
    handleClose(done) {
      this.$confirm('确认关闭？')
        .then(_ => {
          done()
        })
        .catch(_ => {})
    }
  }
}
</script>

<style>
  .graphChart .minimap{
    position: absolute;
    left: 1px;
    top: 2px;
  }
</style>

