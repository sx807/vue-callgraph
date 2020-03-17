
# 1. 服务器 node.js

## 1.1. 安装

### 1.1.1. Development

```bash
npm i
npm run dev
open http://localhost:7001/
```

### 1.1.2. Deploy

```bash
npm start
npm stop
```

## 1.2. egg项目结构

> <https://eggjs.org/zh-cn/basics/structure.html>

```txt
/app
│  router.js // Router 主要用来描述请求 URL 和具体承担执行动作的 Controller 的对应关系， 框架约定了 app/router.js 文件用于统一所有路由规则。
│
├─controller // Controller 负责解析用户的输入，处理后返回相应的结果。主要相应路由的调用，并执行service中的方法处理数据
│  │  home.js
│  │
│  └─v1
│          graphs.js
│          topics.js
│
├─middleware // app/middleware/** 用于编写中间件
│      error_handler.js
│
└─service // Service 就是在复杂业务场景下用于做业务逻辑封装的一个抽象层。将同类处理函数封装成的service类
        graphs.js
        test.js
        topics.js

/config // 框架配置目录
|  config.default.js // config.default.js 为默认的配置文件，所有环境都会加载这个配置文件，一般也会作为开发环境的默认配置文件。
|  plugin.js // plugin.js 用于配置需要加载的插件
```

## 1.3. RESTful API

目标是使用 RESTful 风格的 API 定义，规范化数据获取和处理的流程。

在egg.js框架中，提供了 app.resources('routerName', 'pathMatch', controller) 快速在一个路径上生成 CRUD 路由结构。具体对应如下：

Method | Path | Route Name | Controller.Action
 - | - | - | -
GET | /posts | posts | app.controllers.posts.index
GET | /posts/new | new_post | app.controllers.posts.new
GET | /posts/:id | post | app.controllers.posts.show
GET | /posts/:id/edit | edit_post | app.controllers.posts.edit
POST | /posts | posts | app.controllers.posts.create
PUT | /posts/:id | post | app.controllers.posts.update
DELETE | /posts/:id | post | app.controllers.posts.destroy

## 1.4. 获取函数调用图数据的API设计

功能描述：通过此 API 获取函数调用图的节点和边的数据，使用http get请求获取，在请求中须包含所需要的函数调用关系数据的内核版本号、两个相关路径信息。路径数据可一个或全为'/'，表示请求根目录的函数调用图。

api定义： GET /api/v1/graphs

controller.action：app.controllers.v1.graphs.index

必要接收参数：

```json
params: {
    version: "4-xx-xx"
    source: "/xx"
    target: "/xx"
}

```

相应状态码：200

返回数据格式：

```json
data：{
    Nodes:[],
    Edges:[]
}
```

### 1.4.1. 文件结构

```txt
/app
├─router.js
├─controller
│  └─v1
│     └─graphs.js
└─service
   └─graphs.js
```

#### 1.4.1.1. 路由文件

app/router.js
路由文件中定义graph路由，根据 RESTful 风格规范，定义一下路由：

```js
router.resources('graphs', '/api/v1/graphs', controller.v1.graphs);
```

根据配置处理以下两种访问
GET | /graphs | app.controllers.v1.graphs.index
GET | /graphs/:id | app.controllers.v1.graphs.show

#### 1.4.1.2. 控制器文件

app/controllers/v1/graphs.js
控制器文件中，处理请求的输入数据，调用服务类中的相应函数进行处理

对于路由 /graphs 的访问，由控制器中 index() 函数进行处理
函数使用验证规则，对请求中包含的数据进行初步验证，防止异常输入和恶意输入
验证通过的数据，作为调用服务类中 test() 函数的输入参数

#### 1.4.1.3. 服务文件

app/service/graphs.js
服务文件，包含：处理请求数据，查找数据库，处理读取数据。
处理后的数据提供给页面模块生成函数调用图。

test() 函数，提供生成新函数调用图数据和生成函数调用图中节点展开的新增数据

### 1.4.2. 实现功能

1. 获取函数调用图数据
    读取请求中的内核版本和生成函数调用图的路径，生成图表id，查询历史记录
    使用内核版本号作为读取数据库表名的依据。
    查找对应内核的FDLIST数据表，返回对应的下一级路径或文件内函数列表，同时使用递归方式逐级查找同级和上级路径。将这些路径转换成节点列表。
    通过遍历节点列表，使用Promise构建的异步队列查询SOLIST表生成关联边列表。
    返回生成的调用图数据，并将数据存入查询历史列表。
2. 获取内部效用图数据
   与获取函数调用图数据方式相同，增加per关键字，再查找加点列表过程中不进行递归查找同级和上级路径。
3. 获取展开节点新增数据
    通过请求中关键字expand进行判断，

## 1.5. 函数列表API设计

功能描述：通过此 API 获取函数调用列表数据，使用 http get 请求获取，在请求中须包含所需要的函数调用数据的内核版本号、两个相关路径信息。

api定义： GET /api/v1/functions

controller.action：app.controllers.v1.functions.index

必要接收参数：

```json
params: {
    version: "X-xx-xx"
    source: "/xx"
    target: "/xx"
}
```

### 1.5.1. 文件结构

```txt
/app
├─router.js
├─controller
│  └─v1
│     └─functions.js
└─service
   └─functions.js
```

#### 1.5.1.1. 服务文件

app/service/functions.js
服务文件，包含：处理请求数据，查找数据库，处理读取数据

test() 函数，提供生成新函数调用图数据和生成函数调用图中节点展开的新增数据

## 1.6. 配置获取API

功能描述：通过此 API 获取配置信息：服务器存在内核版本，文件夹列表等配置信息的数据。

api定义： GET /api/v1/options

controller.action：app.controllers.v1.options.index

## API 缓存机制

对于数据获取API，设置缓存机制，能够对相同API、相同参数的请求，处理数据进行缓存，设置过期机制。

# 2. Web页面 Vue.js

## 2.1. 开发

```bash
# 克隆项目
git clone https://github.com/PanJiaChen/vue-element-admin.git

# 进入项目目录
cd vue-element-admin

# 安装依赖
npm install

# 建议不要直接使用 cnpm 安装依赖，会有各种诡异的 bug。可以通过如下操作解决 npm 下载速度慢的问题
npm install --registry=https://registry.npm.taobao.org

# 启动服务
npm run dev
```

浏览器访问 <http://localhost:9527>

## 2.2. 发布

```bash
# 构建测试环境
npm run build:stage

# 构建生产环境
npm run build:prod
```

## 2.3. VUE项目结构

```txt
/src
│  App.vue
│  main.js
│  permission.js
│  settings.js
│
├─components
│  └─Charts
│     │  ContextMenu.vue
│     │  demo.js
│     │  FunList.vue
│     │  Graph.vue
│
├─router
│  │  index.js
│  │
│  └─modules
│          charts.js
│          components.js
│          nested.js
│          table.js
│
└─views
    ├─charts
         graph.vue
```

## 2.4. Graph 函数调用图

基于 Antv G6 实现的函数调用交互图，能够查看内核模块之间的关系。
通过页面上的一组选择器进行内核版本、源路径、目标路径的选择，生成对应的函数调用图

### 2.4.1. 页面文件结构

/src/views/charts/graph.vue为页面文件，文件中包含选择路径版本等选择器组件、函数调用图、函数调用表组件。

/components/Charts/Graph.vue

```txt
/src
├─components
│  └─Charts
│     │  ContextMenu.vue
│     │  FunList.vue
│     └─ Graph.vue
│
└─views
    └─charts
       └─graph.vue
```

### 2.4.2. 页面实现功能

#### 2.4.2.1. 可搜索下菜单选择路径

使用者选择内核版本后，页面会动态加载路径列表，

#### 2.4.2.2. 函数调用图查看

对于生成的函数调用图，查看效果实现有：

1. 画布缩放
2. 拖动整体
3. 拖动节点
4. 鼠标覆盖高亮
5. 详细信息气泡提示框显示
6. 缩略图

#### 2.4.2.3. 筛选查看

通过开关切换显示不同类型的边，切换类别为

1. 源为非所选路径节点
2. 目标为非所选路径节点
3. 源路径节点 到 目标路径节点
4. 目标路径节点 到 源路径节点
5. 源路径节点 到 源路径节点
6. 目标路径节点 到 目标路径节点

#### 2.4.2.4. 右键菜单

实现通过右键函数调用图中组件，弹出对应菜单

1. 右键节点
   菜单内容为：

2. 右键边
   菜单内容为：

#### 2.4.2.5. 动态加载部分更新数据

实现动态更新图中节点数据，将所选节点，更新为其下级路径内容

通过对节点右键菜单中的展开节点，对应函数获取节点信息，并向服务器请求当前节点的展开后新增数据，同时图中将此节点与其相连的边进行删除显示，获取到数据后，对图中数据进行加载，重新绘制当前函数调用图

## 2.5. Function List 函数列表

组件用于显示**源路径**中所包含函数调用**目标路径**中函数的调用列表

组件通过调用图边的右键菜单进行调出显示，显示表格内容如下

\# | 源函数 | 所在文件 | 行号 | 调用次数 | 调用行号 | 被调函数 | 所在文件 | 行号
-| - | - | - | - | - | - | - | -

