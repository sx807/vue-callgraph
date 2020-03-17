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
    <div id="graphchart" class="graphchart" :style="{height:height,width:width}" />
  </div>
</template>

<script>
import G6 from '@antv/g6'
import insertCss from 'insert-css'
import axios from 'axios'
import { Loading } from 'element-ui'
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
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '100%'
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
          tar: ''
        }
      }
    },
    ver: {
      type: String,
      default: ''
    },
    sou: {
      type: String,
      default: ''
    },
    tar: {
      type: String,
      default: ''
    }
  },
  watch: {
    config: {
      handler(newValue, oldValue) {
        console.log(newValue)
        this.getdata('new')
      },
      deep: true
    }
  },
  data() {
    return {
      graph: null,
      minimap: null,
      graph_id: '',
      options: {},
      data: {
        nodes: [],
        edges: [],
        groups: []
      },
      sel_s_to_t: true,
      sel_t_to_s: true,
      sel_p_self: true,
      sel_from_other: true,
      sel_to_other: true,
      contextMenuStyle: {}
    }
  },
  created() {
    const _t = this
    _t.$EventBus.bus.$on('graph/delete', _t.delete_node)
    _t.$EventBus.bus.$on('graph/expand', _t.expand_node)
    _t.$EventBus.bus.$on('graph/layout', _t.updateLayout)
    _t.$EventBus.bus.$on('graph/options', _t.setOptions)
  },
  destroyed() {
    const _t = this
    _t.$EventBus.bus.$off('graph/delete')
    _t.$EventBus.bus.$off('graph/expand')
    _t.$EventBus.bus.$off('graph/layout')
    _t.$EventBus.bus.$off('graph/option')
  },
  mounted() {
    this.initChart()
    this.getdata('new')
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
        container: 'graphchart',
        width: 1200,
        height: 600,
        fitView: true,
        autoPaint: true,
        animate: false,
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
      _t.graph.on('node:mouseleave', _t.clearAllStats)
      // _t.graph.on('canvas:click', _t.clearAllStats)
      _t.graph.on('node:contextmenu', evt => {
        // console.log(evt)
        this.$EventBus.bus.$emit('graph/contextmenu/open', evt)
      })
      _t.graph.on('edge:contextmenu', evt => {
        // console.log(evt)
        this.$EventBus.bus.$emit('graph/contextmenu/open', evt)
      })
      _t.graph.on('canvas:click', () => {
        _t.clearAllStats()
        this.$EventBus.bus.$emit('graph/contextmenu/close')
      })
      // _t.graph.on('node:mouseleave', () => {
      //   _t.contextMenuStyle.left = '-150px'
      // })
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
    getdata(type) {
      const _t = this
      const loadingInstance = Loading.service({ target: '#graphchart' })
      const config = {
        version: _t.config.ver,
        source: _t.config.sou,
        target: _t.config.tar
      }
      for (const key in _t.options) {
        config[key] = _t.options[key]
      }
      axios.get('http://192.168.3.44:7001/api/v1/graphs', { // 还可以直接把参数拼接在url后边
      // axios.get('./public/data.json', {
        params: config,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        // console.log(res.data)
        if (res.data.nodes.length > 0) {
          _t.graph_id = res.data.id
          const tmp = res.data
          tmp.nodes.map(function(node) {
            node.label = node.id
            if (!node.style) {
              node.style = {}
            }
            node.style.fill = colors[node.type % colors.length]
            node.style.stroke = strokes[node.type % strokes.length]
          })
          tmp.edges.map(function(edge) {
            if (!edge.style) {
              edge.style = {}
            }
            edge.style.stroke = strokes[edge.type % strokes.length]
          })
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
          _t.select_edge()
          loadingInstance.close()
        }
      }).catch(function(error) {
        console.log(error)
      })
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
      _t.getdata('add')
      // console.log('node', _t.graph.getNodes(), 'edge', _t.graph.getEdges())
    },
    updateLayout(layout) {
      const _t = this
      console.log(_t.layout)
      _t.graph.updateLayout({
        type: layout,
        preventOverlap: true,
        nodeSize: 50
      })
    }
  }
}
</script>

<style>
  .graphchart .minimap{
    position: absolute;
    left: 1000px;
    top: 1px;
  }
</style>

