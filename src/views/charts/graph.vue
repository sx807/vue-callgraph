<template>
  <div class="chart-container">
    <el-row :gutter="20">
      <el-col :span="4" :offset="2">
        <el-select v-model="ver" filterable placeholder="选择内核版本" @change="verchange">
          <el-option
            v-for="item in ver_list"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-input v-model="path1" filterable placeholder="请输入路径" @change="pathchange"></el-input>
      </el-col>
      <el-col :span="4">
        <el-input v-model="path2" filterable placeholder="请输入路径" @change="pathchange"></el-input>
      </el-col>
      <el-col :span="9">
        <label class="radio-label">Layout:  </label>
        <el-select v-model="layout" style="width:120px;">
          <el-option
            v-for="item in layout_options"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <!-- <el-button type="primary" round>生成调用图</el-button> -->
      </el-col>
    </el-row>
    <graph height="100%" width="100%" v-if="showgraph()" :layout="layout" :ver="ver" :sou="sou" :tar="tar"/>
  </div>
</template>

<script>
import graph from '@/components/Charts/Graph'
import axios from 'axios'

export default {
  name: 'Graph',
  components: { graph },
  data() {
    return {
      url:'http://192.168.3.30:7001/api/v1/',
      ver: '',
      ver_list: [],
      path1: '',
      path2: '',
      sou: '',
      tar: '',
      show: false,
      path_list: [],
      layout: 'random',
      layout_options: ['random', 'fruchterman', 'mds', 'circular', 'concentric']
    }
  },
  mounted() {
    this.getverlist()
  },
  methods:{
    verchange(item){
      this.getpathlist()
    },
    pathchange(item){
      // console.log(item)
      if(this.path1 !== ''){
        this.sou = this.path1
      }
      if(this.path2 !== ''){
        this.tar = this.path2
      }
    },

    showgraph(){
      if(this.ver !== '' && this.sou !== '' && this.tar !== ''){
        return true
      }
      else return false
    },

    getverlist(){
      const _t = this
      let url = _t.url + 'options'
      axios.get(url,{
        headers: {
          "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
      }).then(function(res){
        console.log(res)
      }).catch(function (error) {
        console.log(error)
      });
    },
    
    getpathlist(){
      const _t = this
      let url = _t.url + 'options/' + _t.ver
      axios.get(url,{
        headers: {
          "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
      }).then(function(res){
        console.log(res)
      }).catch(function (error) {
        console.log(error)
      });
    }
  }
}
</script>

<style scoped>
  .chart-container{
    position: relative;
    width: 100%;
    height: calc(100vh - 84px);
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
