<template>
  <div>
    <ul v-show="isShow" class="context-menu" :style="contextMenuStyle">
      <li v-for="(item, index) in contextMenuList" :key="index" @click="doChick(item)">{{ item.label }}</li>
    </ul>
  </div>
</template>
C
<script>
export default {
  name: 'ContextMenu',
  data() {
    return {
      isShow: false,
      type: '',
      options: null,
      contextMenuList: [],
      contextMenuStyle: {}
    }
  },
  created() {
    const _t = this
    _t.$EventBus.bus.$on('graph/contextmenu/open', _t.doShow)
    _t.$EventBus.bus.$on('graph/contextmenu/close', _t.doHide)
  },
  destroyed() {
    const _t = this
    _t.$EventBus.bus.$off('graph/contextmenu/open')
    _t.$EventBus.bus.$off('graph/contextmenu/close')
  },
  methods: {
    handleContextMenuList(type) {
      const list_node = [
        {
          value: 'Code',
          label: '显示源码'
        },
        {
          value: 'SetSou',
          label: '设为源路径'
        },
        {
          value: 'SetTar',
          label: '设为目标路径'
        },
        {
          value: 'Expand',
          label: '展开下一级'
        },
        {
          value: 'Delete',
          label: '删除节点'
        }
      ]
      const list_edge = [
        {
          value: 'FunList',
          label: '显示函数列表'
        },
        {
          value: 'Graph',
          label: '切换调用图'
        },
        {
          value: 'Inside',
          label: '切换内部调用图'
        }
      ]
      if (type === 'node') {
        this.contextMenuList = list_node
      } else {
        this.contextMenuList = list_edge
      }
    },
    handleContextMenuStyle() {
      const _t = this
      const style = {}
      if (!_t.options) {
        return style
      }
      style['left'] = `${_t.options.canvasX}px`
      style['top'] = `${_t.options.canvasY + 20}px`
      _t.contextMenuStyle = style
      // console.log(_t.contextMenuStyle)
    },
    doChick(val) {
      const _t = this
      console.log(val)
      const path = {}
      const item = _t.options.item.getModel()
      switch (val.value) {
        case 'SetSou':
          path.sou = item.id
          break
        case 'SetTar':
          path.tar = item.id
          break
        case 'Delete':
          _t.$EventBus.bus.$emit('graph/delete', _t.options.item)
          break
        case 'Expand':
          _t.$EventBus.bus.$emit('graph/expand', _t.options.item)
          break
        case 'Inside':
          _t.$EventBus.bus.$emit('graph/options', { per: false })
        // eslint-disable-next-line no-fallthrough
        case 'Graph':
          path.sou = item.source
          path.tar = item.target
          break
      }
      // if (path.disabled) console.log('{}')
      if (Object.keys(path).length > 0) _t.$EventBus.bus.$emit('graph/path/change', path)
      _t.doHide()
    },
    doShow(data) {
      const _t = this
      _t.options = data
      console.log(_t.options.item)
      _t.handleContextMenuList(_t.options.item.getType())
      // 处理样式
      _t.handleContextMenuStyle()
      _t.isShow = true
    },
    doHide() {
      const _t = this
      _t.options = null
      _t.contextMenuList = []
      _t.isShow = false
    }
  }
}
</script>

<style scoped>
  .context-menu {
    position: absolute;
    min-width: 120px;
    list-style-type: none;
    width: auto !important;
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #e2e2e2;
    border-radius: 4px;
    font-size: 12px;
    color: #545454;
    padding: 10px 8px;
    z-index: 999;
  }
  .context-menu li {
    padding: 5px 10px;
    cursor: pointer;
    list-style: none;
    margin-left: 0px;
  }
  .context-menu li:hover {
    color: #aaa;
  }
</style>
