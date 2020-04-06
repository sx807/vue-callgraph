<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="3" :offset="1">
        <el-switch
          v-model="sel_from_other"
          active-text="other ->"
          @change="select_edge()"
        />
      </el-col>
      <el-col :span="3">
        <el-switch
          v-model="sel_to_other"
          active-text="-> other"
          @change="select_edge()"
        />
      </el-col>
      <el-col :span="3">
        <el-switch
          v-model="sel_p_self"
          active-text="path -> self"
          @change="select_edge()"
        />
      </el-col>
      <el-col :span="3">
        <el-switch
          v-model="sel_s_to_t"
          active-text="path1 -> path2"
          @change="select_edge()"
        />
      </el-col>
      <el-col :span="3">
        <el-switch
          v-model="sel_t_to_s"
          active-text="path2 -> path1"
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
    config: {
      type: Object,
      default: function() {
        return {
          var: '',
          sou: '',
          tar: '',
          w: 1000,
          h: 500
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
      graph: null,
      minimap: null,
      graph_id: '',
      options: {},
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
      sel_s_to_t: true,
      sel_t_to_s: true,
      sel_p_self: true,
      sel_from_other: true,
      sel_to_other: true,
      contextMenuStyle: {},
      share_dialog: false,
      share_url: ''
    }
  },
  watch: {
    config: {
      handler(newValue, oldValue) {
        const _t = this
        console.log('watch config', newValue)
        if (newValue.h !== _t.graph_h || newValue.w !== _t.graph_w) {
          _t.graph_h = newValue.h
          _t.graph_w = newValue.w
          // _t.graph.set('width', Number(newValue.w))
          // _t.graph.set('height', Number(newValue.h))
          _t.graph.changeSize(_t.graph_w, _t.graph_h)
          _t.graph.fitView()
          // _t.graph.destroy()
          // _t.initChart()
          // _t.graph.data(_t.data)
          // _t.graph.render()
          // console.log('mounted', _t.$refs.graphChart.offsetWidth)
          console.log(_t.graph.get('width'), _t.graph.get('height'))
        } else {
          _t.backup()
          _t.get_data('new')
        }
        _t.graph_config = newValue
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
    _t.$EventBus.bus.$on('graph/options', _t.setOptions)
    _t.$EventBus.bus.$on('graph/back', _t.back_graph)
    _t.$EventBus.bus.$on('graph/post', _t.save_graph)
    // this.$nextTick(function() {
    //   console.log('next', _t.$refs.graphChart.offsetWidth)
    // })
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
    // _t.graph_w = _t.$refs.graphChart.offsetWidth
    _t.graph_config = _t.config
    _t.initChart()
    // console.log('mounted', _t.config, _t.ex_data)
    // console.log('mounted', _t.$refs.graphChart.offsetHeight, _t.$refs.graphChart.offsetWidth)
    if (_t.config.ex) {
      _t.get_data('external')
    } else {
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
        graph_config: {},
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
              formatText: function formatText(model) {
                return model.id
              }
            },
            {
              type: 'edge-tooltip',
              formatText: function formatText(model, e) {
                var edge = e.item
                return '调用次数：' + edge.getModel().sourceWeight + '<br/>来源：' + edge.getSource().getModel().id + '<br/>去向：' + edge.getTarget().getModel().id
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
        this.$EventBus.bus.$emit('graph/contextmenu/close')
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
    setOptions(val) {
      const keys = Object.keys(val)
      for (const key of keys) {
        this.options[key] = val[key]
      }
    },
    get_data(type) {
      const _t = this
      const loadingInstance = Loading.service({ target: '#graphChart' })
      const config = {
        version: _t.config.ver,
        source: _t.config.sou,
        target: _t.config.tar
      }
      for (const key in _t.options) {
        config[key] = _t.options[key]
      }
      if (type === 'external') {
        const tmp = _t.handle_data(_t.ex_data)
        _t.data = JSON.parse(JSON.stringify(tmp))
        _t.graph.setAutoPaint(false)
        _t.graph.changeData({
          // groups: _t.data.groups,
          nodes: _t.data.nodes,
          edges: _t.data.edges
        })
        for (const node of tmp.nodes) {
          // console.log(node)
          // _t.graph.add('node', node)
          // _t.graph.findById(node.id).updatePosition({ x: node.x, y: node.y })
          _t.graph.updateItem(node.id, { x: node.x, y: node.y })
        }
        // _t.select_edge()
        _t.clearAllStats()
        _t.graph.paint()
        _t.graph.setAutoPaint(true)
        _t.graph.fitView()
        loadingInstance.close()
      } else {
        // axios.defaults.withCredentials = true
        axios.get('http://192.168.3.44:7001/api/v1/graphs', { // 还可以直接把参数拼接在url后边
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
            if (type === 'new') {
              _t.data = tmp
            }
            if (type === 'add') {
              _t.data.nodes = _t.data.nodes.concat(tmp.nodes)
              _t.data.edges = _t.data.edges.concat(tmp.edges)
              console.log(_t.data.nodes)
            }
            _t.graph.data({
              // groups: _t.data.groups,
              nodes: _t.data.nodes,
              edges: _t.data.edges
            })
            // console.log(_t.graph.getNodes().length)
            _t.options = {}
            _t.graph.render()
            _t.graph.fitView()
            _t.select_edge()
          }
          loadingInstance.close()
        }).catch(function(error) {
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
      _t.graph.getEdges().forEach(function(edge) {
        // console.log(edge.getSource().getModel().type)
        if (edge.getSource().getModel().type === 2) {
          // console.log(edge)
          if (_t.sel_from_other) {
            _t.graph.showItem(edge)
          } else {
            // console.log('hide')
            _t.graph.hideItem(edge)
          }
        } else if (edge.getTarget().getModel().type === 2) {
          if (_t.sel_to_other) {
            _t.graph.showItem(edge)
          } else {
            _t.graph.hideItem(edge)
          }
        } else if (edge.getSource().getModel().type === 0 &&
                   edge.getTarget().getModel().type === 1) {
          if (_t.sel_s_to_t) {
            _t.graph.showItem(edge)
          } else {
            _t.graph.hideItem(edge)
          }
        } else if (edge.getSource().getModel().type === 1 &&
          edge.getTarget().getModel().type === 0) {
          if (_t.sel_t_to_s) {
            _t.graph.showItem(edge)
          } else {
            _t.graph.hideItem(edge)
          }
        } else {
          if (_t.sel_p_self) {
            _t.graph.showItem(edge)
          } else {
            _t.graph.hideItem(edge)
          }
        }
      })
      _t.graph.paint()
      _t.graph.setAutoPaint(true)
    },
    backup() {
      const _t = this
      _t.backup_data.id = _t.graph_id
      _t.backup_data.layout = _t.layout
      _t.backup_data.config = _t.graph_config
      _t.backup_data.data = _t.graph.save()
      // console.log(_t.backup_data.data)
    },
    back_graph(item) {
      const _t = this
      if (Object.keys(_t.backup_data.data).length > 0) {
        _t.graph.setAutoPaint(false)
        // _t.graph.clear()
        _t.graph.changeData({
          // groups: _t.data.groups,
          nodes: _t.backup_data.data.nodes,
          edges: _t.backup_data.data.edges
        })
        const nodes = _t.backup_data.data.nodes
        for (const node of nodes) {
          // console.log(node)
          // _t.graph.add('node', node)
          const item = _t.graph.findById(node.id)
          _t.graph.updateItem(item, node)
        }
        // _t.graph.refresh()
        // _t.select_edge()
        _t.clearAllStats()
        _t.graph.paint()
        _t.graph.setAutoPaint(true)
      }
    },
    save_graph() {
      const _t = this
      // console.log(Cookies.get('csrfToken'))
      // const loadingInstance = Loading.service({ target: '#graphChart' })
      const config = {
        version: _t.config.ver,
        source: _t.config.sou,
        target: _t.config.tar
      }
      // axios.defaults.withCredentials = true
      // axios.defaults.xsrfCookieName = 'csrfToken' // default: XSRF-TOKEN
      // axios.defaults.xsrfHeaderName = 'x-csrf-token' // default: X-XSRF-TOKEN
      const row = _t.graph.save()
      const data = {
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
      axios.post('http://192.168.3.44:7001/api/v1/graphs', {
        // axios.get('./public/data.json', {
        config: config,
        data: data
      }, {
        headers: {
          // 'x-csrf-token': Cookies.get('csrfToken'),
          'Content-Type': 'application/json;charset=utf-8'
          // 'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        console.log(res.data)
        _t.share_url = window.location.href + '/' + res.data.share_key
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
      console.log(_t.data.nodes)
      for (const edge of _t.data.edges) {
        if (edge.source !== nodeId && edge.target !== nodeId) {
          tmp.push(edge)
        }
      }
      _t.data.edges = tmp
      _t.setOptions({
        id: _t.graph_id,
        expand: nodeId
      })
      _t.get_data('add')
      // console.log('node', _t.graph.getNodes(), 'edge', _t.graph.getEdges())
    },
    updateLayout(layout) {
      const _t = this
      console.log(_t.layout)
      _t.graph.updateLayout({
        width: 1200,
        height: 600,
        type: layout,
        preventOverlap: true,
        nodeSize: 50,
        linkDistance: 50
      })
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

