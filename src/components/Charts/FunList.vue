<template>
  <el-table
    v-loading="loading"
    :data="data.list"
    style="width: 100%"
    :default-sort="{prop: 's_fun', order: 'descending'}"
    max-height="500"
  >
  <!--    height="500"-->
  <!--    max-height="500"-->
    <el-table-column
      type="index"
      width="50"
    />
    <el-table-column
      prop="s_fun"
      label="源函数"
      sortable
    />
    <el-table-column
      prop="s_file"
      label="所在文件"
    >
      <template slot-scope="scope">
        <el-button @click="handleClick(scope.row, 's_file', 0)" type="text" size="small">
          {{ scope.row.s_file }}
        </el-button>
      </template>
    </el-table-column>
    <el-table-column
      prop="s_line"
      label="行号"
    >
      <template slot-scope="scope">
        <el-button
          @click="handleClick(scope.row, 's_line', scope.row.s_line)"
          type="text"
          size="small"
        >
          {{ scope.row.s_line }}
        </el-button>
      </template>
    </el-table-column>
    <el-table-column
      prop="num"
      label="调用次数"
    />
    <el-table-column
      prop="call_line"
      label="调用行号"
    >
      <template slot-scope="scope">
        <el-button
          @click="handleClick(scope.row, 'call', scope.row.call_line)"
          type="text"
          size="small"
          v-for="item in scope.row.call_line"
          :key="item"
        >
          {{ item }}
        </el-button>
      </template>
    </el-table-column>
    <el-table-column
      prop="t_fun"
      label="被调函数"
    />
    <el-table-column
      prop="t_file"
      label="所在文件"
    >
      <template slot-scope="scope">
        <el-button
          @click="handleClick(scope.row, 't_file', 0)"
          type="text"
          size="small"
        >
          {{ scope.row.t_file }}
        </el-button>
      </template>
    </el-table-column>
    <el-table-column
      prop="t_line"
      label="行号"
    >
      <template slot-scope="scope">
        <el-button
          @click="handleClick(scope.row, 't_line', scope.row.t_line)"
          type="text"
          size="small"
        >
          {{ scope.row.t_line }}
        </el-button>
      </template>
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
      handler(newValue) {
        console.log(newValue)
        // if (this.height !== newValue.h) {
        //   this.height = newValue.h
        //   console.log(this.height)
        // } else {
        this.getdata()
        // }
      },
      deep: true
    }
  },
  data() {
    return {
      table_id: '',
      options: {},
      height: 500,
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
    },
    handleClick(row, type, num) {
      const _t = this
      let path = ''
      const line = num
      switch (type) {
        case 'call':
        case 's_line':
        case 's_file':
          path = row.s_file
          break
        case 't_line':
        case 't_file':
          path = row.t_file
          break
      }
      _t.$EventBus.bus.$emit('code/show', '/' + path, line)
    }
  }
}
</script>

<style scoped>

</style>
