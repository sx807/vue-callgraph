<template>
  <div>
    <ul v-show="isShow" class="context-menu" :style="contextMenuStyle">
      <li>Option 1</li>
      <li>Option 2</li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ContextMenu',
  data() {
    return {
      isShow: false,
      activeMenu: '',
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
    doShow(data) {
      const _t = this
      _t.options = data
      console.log(data.item.getType())
      // _t.handleContextMenuList()
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
    z-index: 9999;
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #e2e2e2;
    border-radius: 4px;
    font-size: 12px;
    color: #545454;
    padding: 10px 8px;
    z-index: 999;
  }
  .context-menu li {
    cursor: pointer;
    list-style-type:none;
    list-style: none;
    margin-left: 0px;
  }
  .context-menu li:hover {
    color: #aaa;
  }
</style>
