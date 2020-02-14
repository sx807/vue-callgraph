<template>
  <div id="mountNode" class="graphchart" :style="{height:height,width:width}" />
</template>

<script>
import G6 from '@antv/g6'
import insertCss from 'insert-css'
import axios from 'axios'
// import Minimap from '@antv/g6/build/minimap'
const Minimap = require('@antv/g6/build/minimap')

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
      type: String
    },
    sou: {
      type: String
    },
    tar: {
      type: String
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
      }
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
              style: {
                'border': '1px solid #e2e2e2',
                'border-radius': '4px',
                'font-size': '8px',
                'color': '#545454',
                'background-color': 'rgba(255, 255, 255, 0.9)',
                'padding': '10px 8px',
                'box-shadow': 'rgb(174, 174, 174) 0px 0px 10px'
              },
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
          size: [20, 10],
          color: 'steelblue',
          labelCfg: {
            style: {
              fill: '#000',
              fontSize: 10
            }
          }
        },
        defaultEdge: {
          shape: 'quadratic',
          size: 1
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
            stroke: '#e2e2e2',
            lineAppendWidth: 2
          },
          highlight: {
            stroke: '#999'
          }
        }
      })
      _t.graph.on('node:mouseenter', function(e) {
        var item = e.item
        console.log(e)
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
        params: {
          version: _t.ver,
          source: _t.sou,
          target: _t.tar
        },
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        console.log(res.data)
        _t.data = res.data
        _t.data.nodes.map(function(node, i) {
          node.label = node.id
        })
        _t.graph.data({
          nodes: _t.data.nodes,
          edges: _t.data.edges.map(function(edge, i) {
            edge.id = 'edge' + i
            // edge.source = 'node' + edge.source
            // edge.target = 'node' + edge.target
            // console.log(edge)
            return Object.assign({}, edge)
          })
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
    ticked() {
      const _t = this
      _t.graph.refreshPositions()
      _t.graph.paint()
    },
    updateLayout() {
      const _t = this
      _t.graph.updateLayout({
        type: _t.layout
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
</style>

