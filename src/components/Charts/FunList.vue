<template>
  <el-table
    :data="data.list"
    style="width: 100%"
    height="500"
    max-height="500"
    v-loading="loading"
    :default-sort = "{prop: 's_fun', order: 'descending'}"
  >
    <el-table-column
      type="index"
      width="50">
    </el-table-column>
    <el-table-column
      prop="s_fun"
      label="源函数"
      sortable>
    </el-table-column>
    <el-table-column
      prop="s_file"
      label="所在文件">
    </el-table-column>
    <el-table-column
      prop="s_line"
      label="行号">
    </el-table-column>
    <el-table-column
      prop="num"
      label="调用次数">
    </el-table-column>
    <el-table-column
      prop="call_line"
      label="调用行号">
    </el-table-column>
    <el-table-column
      prop="t_fun"
      label="被调函数">
    </el-table-column>
    <el-table-column
      prop="t_file"
      label="所在文件">
    </el-table-column>
    <el-table-column
      prop="t_line"
      label="行号">
    </el-table-column>
  </el-table>
</template>

<script>
// import { Loading } from 'element-ui'
import axios from 'axios'

export default {
  name: 'FunList',
  props: {
    id: {
      type: String,
      default: 'chart'
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
    }
  },
  watch: {
    config: {
      handler(newValue, oldValue) {
        console.log(newValue)
        this.getdata()
      },
      deep: true
    }
  },
  data() {
    return {
      table_id: '',
      options: {},
      loading: false,
      data: {
        list: []
      }
    }
  },
  methods: {
    getdata() {
      const _t = this
      _t.loading = true
      const config = {
        version: _t.config.ver,
        source: _t.config.sou,
        target: _t.config.tar
      }
      for (const key in _t.options) {
        config[key] = _t.options[key]
      }
      axios.get('http://192.168.3.44:7001/api/v1/functions', { // 还可以直接把参数拼接在url后边
        // axios.get('./public/data.json', {
        params: config,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
      }).then(function(res) {
        console.log(res.data)
        if (res.data.list.length > 0) {
          _t.table_id = res.data.id
          _t.data = res.data
          _t.options = {}
          _t.loading = false
        }
      }).catch(function(error) {
        console.log(error)
      })
    }
  }
}
</script>

<style scoped>

</style>
