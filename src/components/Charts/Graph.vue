<template>
  <div>
    <ul id="contextMenu" :style="contextMenuStyle">
      <li>Option 1</li>
      <li>Option 2</li>
    </ul>
    <el-row :gutter="20">
      <el-col :span="4" :offset="2">
        <el-switch
          v-model="sel_from_other"
          inactive-text="from-other"
          @change="select_edge()"
        >
        </el-switch>
      </el-col>
      <el-col :span="4">
        <el-switch
          v-model="sel_to_other"
          inactive-text="to-other"
          @change="select_edge()"
        >
        </el-switch>
      </el-col>
      <el-col :span="4">
        <el-switch
          v-model="sel_p_self"
          inactive-text="from-other"
          @change="select_edge()"
        >
        </el-switch>
      </el-col>
      <el-col :span="4">
        <el-switch
          v-model="sel_p_to_p"
          inactive-text="from-other"
          @change="select_edge()"
        >
        </el-switch>
      </el-col>
    </el-row>
    <div id="mountNode" class="graphchart" :style="{height:height,width:width}" />
  </div>
</template>

<script>
import G6 from '@antv/g6'
import insertCss from 'insert-css'
import axios from 'axios'
// import Minimap from '@antv/g6/build/minimap'
const Minimap = require('@antv/g6/build/minimap')
const colors = ['#BDD2FD', '#BDEFDB', '#C2C8D5', '#FBE5A2', '#F6C3B7', '#B6E3F5', '#D3C6EA', '#FFD8B8', '#AAD8D8', '#FFD6E7']
const strokes = ['#5B8FF9', '#5AD8A6', '#5D7092', '#F6BD16', '#E8684A', '#6DC8EC', '#9270CA', '#FF9D4D', '#269A99', '#FF99C3']

insertCss(`
  .g6-tooltip {
    border: 1px solid #e2e2e2;
    border-radius: 4px;
    font-size: 12px;
    color: #545454;/
    background-color: rgba(255, 255, 255, 0.9);
    padding: 10px 8px;
    box-shadow: rgb(174, 174, 174) 0px 0px 10px;
  }
  #contextMenu {
    position: absolute;
    list-style-type: none;
    padding: 10px 8px;
    left: -150px;
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #e2e2e2;
    border-radius: 4px;
    font-size: 12px;
    color: #545454;
  }
  #contextMenu li {
    cursor: pointer;
    list-style-type:none;
    list-style: none;
    margin-left: 0px;
  }
  #contextMenu li:hover {
    color: #aaa;
  }`)

// JSX and HTML templates are available for the menu
// create ul

export default {
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
    ver() {
      this.getdata()
    },
    sou() {
      this.getdata()
    },
    tar() {
      this.getdata()
    },
    layout(val) {
      console.log(val)
      this.updateLayout()
    }
  },
  data() {
    return {
      graph: null,
      minimap: null,
      data: {
        nodes: [],
        edges: []
      },
      sel_p_to_p: true,
      sel_p_self: true,
      sel_from_other: true,
      sel_to_other: true,
      contextMenuStyle: {}
    }
  },
  mounted() {
    this.initChart()
    this.getdata()
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
        container: 'mountNode',
        width: 1200,
        height: 600,
        fitView: true,
        autoPaint: true,
        animate: false,
        plugins: [_t.minimap],
        modes: {
          default: ['drag-canvas',
            'zoom-canvas',
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
                return '来源：' + edge.getSource().getModel().id + '<br/>去向：' + edge.getTarget().getModel().id
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
      _t.graph.on('canvas:click', _t.clearAllStats)
      _t.graph.on('node:contextmenu', evt => {
        console.log(evt)
        evt.preventDefault()
        evt.stopPropagation()
        _t.contextMenuStyle.left = `${(evt.x + 20)}px`
        _t.contextMenuStyle.top = `${evt.y}px`
      })

      _t.graph.on('node:mouseleave', () => {
        _t.contextMenuStyle.left = '-150px'
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
    getdata() {
      const _t = this
      axios.get('http://192.168.3.44:7001/api/v1/graphs', { // 还可以直接把参数拼接在url后边
      // axios.get('./public/data.json', {
        params: {
          version: _t.ver,
          source: _t.sou,
          target: _t.tar
        },
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        // console.log(res.data)
        _t.data = res.data
        _t.data.nodes.map(function(node, i) {
          node.label = node.id
          if (!node.style) {
            node.style = {}
          }
          node.style.fill = colors[node.type % colors.length]
          node.style.stroke = strokes[node.type % strokes.length]
        })
        _t.data.edges.map(function(edge, i) {
          edge.id = 'edge' + i
          // edge.source = 'node' + edge.source
          // edge.target = 'node' + edge.target
          // console.log(edge)
          if (!edge.style) {
            edge.style = {}
          }
          // edge.style.fill = colors[node.type % colors.length]
          edge.style.stroke = strokes[edge.type % strokes.length]
        })
        _t.graph.data({
          nodes: _t.data.nodes,
          edges: _t.data.edges
        })
        _t.graph.render()
      }).catch(function(error) {
        console.log(error)
      })
      // _t.data.nodes.map(function(node, i) {
      //   node.label = node.id
      // })
      // // $.getJSON('./test.json', function(data) {
      // _t.graph.data({
      //   nodes: _t.data.nodes,
      //   edges: _t.data.edges.map(function(edge, i) {
      //     edge.id = 'edge' + i
      //     // edge.source = 'node' + edge.source
      //     // edge.target = 'node' + edge.target
      //     // console.log(edge)
      //     return Object.assign({}, edge)
      //   })
      // })
      // _t.graph.render()
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
        } else if (edge.getTarget().getModel().type === edge.getSource().getModel().type) {
          if (_t.sel_p_to_p) {
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
    ticked() {
      const _t = this
      _t.graph.refreshPositions()
      _t.graph.paint()
    },
    updateLayout() {
      const _t = this
      _t.graph.updateLayout({
        type: _t.layout,
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
    top: 0px;
  }
  #contextMenu {
    position: absolute;
    list-style-type: none;
    padding: 10px 8px;
    left: -150px;
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #e2e2e2;
    border-radius: 4px;
    font-size: 12px;
    color: #545454;
  }
  #contextMenu li {
    cursor: pointer;
    list-style-type:none;
    list-style: none;
    margin-left: 0px;
  }
  #contextMenu li:hover {
    color: #aaa;
  }
</style>

