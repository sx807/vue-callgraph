# 分析平台

## 服务器 node.js

### 安装

#### Development

```bash
npm i
npm run dev
open http://localhost:7001/
```

#### Deploy

```bash
npm start
npm stop
```

### egg项目结构

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

### API

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

#### 获取函数调用图数据的API设计

功能描述：通过此 API 获取函数调用图的节点和边的数据数据，使用http get请求获取，在请求中须包含所需要的函数调用关系数据的内核版本号、两个相关路径信息。路径数据可一个或全为'/'，表示请求根目录的函数调用图。

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

##### 相关文件

```txt
/app
├─router.js
├─controller
│  └─v1
│     └─graphs.js
└─service
   └─graphs.js
```

app/router.js
路由文件中定义graph路由，根据 RESTful 风格规范，定义一下路由：

```js
router.resources('graphs', '/api/v1/graphs', controller.v1.graphs);
```

根据配置处理以下两种访问
GET | /graphs | app.controllers.v1.graphs.index
GET | /graphs/:id | app.controllers.v1.graphs.show

app/controllers/v1/graphs.js
控制器文件中

## Web页面 Vue.js

### 开发

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

浏览器访问 http://localhost:9527

### 发布

```bash
# 构建测试环境
npm run build:stage

# 构建生产环境
npm run build:prod
```

### VUE项目结构

```txt
/src
│  App.vue
│  main.js
│  permission.js
│  settings.js
│
├─api
│      article.js
│      qiniu.js
│      remote-search.js
│      role.js
│      user.js
│
├─assets
│  ├─401_images
│  │      401.gif
│  │
│  ├─404_images
│  │      404.png
│  │      404_cloud.png
│  │
│  └─custom-theme
│      │  index.css
│      │
│      └─fonts
│              element-icons.ttf
│              element-icons.woff
│
├─components
│  ├─BackToTop
│  │      index.vue
│  │
│  ├─Breadcrumb
│  │      index.vue
│  │
│  ├─Charts
│  │  │  ContextMenu.vue
│  │  │  demo.js
│  │  │  FunList.vue
│  │  │  Graph.vue
│  │  │  Keyboard.vue
│  │  │  LineMarker.vue
│  │  │  MixChart.vue
│  │  │
│  │  └─mixins
│  │          resize.js
│  │
│  ├─DndList
│  │      index.vue
│  │
│  ├─DragSelect
│  │      index.vue
│  │
│  ├─Dropzone
│  │      index.vue
│  │
│  ├─ErrorLog
│  │      index.vue
│  │
│  ├─GithubCorner
│  │      index.vue
│  │
│  ├─Hamburger
│  │      index.vue
│  │
│  ├─HeaderSearch
│  │      index.vue
│  │
│  ├─ImageCropper
│  │  │  index.vue
│  │  │
│  │  └─utils
│  │          data2blob.js
│  │          effectRipple.js
│  │          language.js
│  │          mimes.js
│  │
│  ├─JsonEditor
│  │      index.vue
│  │
│  ├─Kanban
│  │      index.vue
│  │
│  ├─MarkdownEditor
│  │      default-options.js
│  │      index.vue
│  │
│  ├─MDinput
│  │      index.vue
│  │
│  ├─Pagination
│  │      index.vue
│  │
│  ├─PanThumb
│  │      index.vue
│  │
│  ├─RightPanel
│  │      index.vue
│  │
│  ├─Screenfull
│  │      index.vue
│  │
│  ├─Share
│  │      DropdownMenu.vue
│  │
│  ├─SizeSelect
│  │      index.vue
│  │
│  ├─Sticky
│  │      index.vue
│  │
│  ├─SvgIcon
│  │      index.vue
│  │
│  ├─TextHoverEffect
│  │      Mallki.vue
│  │
│  ├─ThemePicker
│  │      index.vue
│  │
│  ├─Tinymce
│  │  │  dynamicLoadScript.js
│  │  │  index.vue
│  │  │  plugins.js
│  │  │  toolbar.js
│  │  │
│  │  └─components
│  │          EditorImage.vue
│  │
│  ├─Upload
│  │      SingleImage.vue
│  │      SingleImage2.vue
│  │      SingleImage3.vue
│  │
│  └─UploadExcel
│          index.vue
│
├─directive
│  │  sticky.js
│  │
│  ├─clipboard
│  │      clipboard.js
│  │      index.js
│  │
│  ├─el-drag-dialog
│  │      drag.js
│  │      index.js
│  │
│  ├─el-table
│  │      adaptive.js
│  │      index.js
│  │
│  ├─permission
│  │      index.js
│  │      permission.js
│  │
│  └─waves
│          index.js
│          waves.css
│          waves.js
│
├─filters
│      index.js
│
├─icons
│  │  index.js
│  │  svgo.yml
│  │
│  └─svg
│          404.svg
│          bug.svg
│          chart.svg
│          clipboard.svg
│          component.svg
│          dashboard.svg
│          documentation.svg
│          drag.svg
│          edit.svg
│          education.svg
│          email.svg
│          example.svg
│          excel.svg
│          exit-fullscreen.svg
│          eye-open.svg
│          eye.svg
│          form.svg
│          fullscreen.svg
│          guide.svg
│          icon.svg
│          international.svg
│          language.svg
│          link.svg
│          list.svg
│          lock.svg
│          message.svg
│          money.svg
│          nested.svg
│          password.svg
│          pdf.svg
│          people.svg
│          peoples.svg
│          qq.svg
│          search.svg
│          shopping.svg
│          size.svg
│          skill.svg
│          star.svg
│          tab.svg
│          table.svg
│          theme.svg
│          tree-table.svg
│          tree.svg
│          user.svg
│          wechat.svg
│          zip.svg
│
├─layout
│  │  index.vue
│  │
│  ├─components
│  │  │  AppMain.vue
│  │  │  index.js
│  │  │  Navbar.vue
│  │  │
│  │  ├─Settings
│  │  │      index.vue
│  │  │
│  │  ├─Sidebar
│  │  │      FixiOSBug.js
│  │  │      index.vue
│  │  │      Item.vue
│  │  │      Link.vue
│  │  │      Logo.vue
│  │  │      SidebarItem.vue
│  │  │
│  │  └─TagsView
│  │          index.vue
│  │          ScrollPane.vue
│  │
│  └─mixin
│          ResizeHandler.js
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
├─store
│  │  getters.js
│  │  index.js
│  │
│  └─modules
│          app.js
│          errorLog.js
│          permission.js
│          settings.js
│          tagsView.js
│          user.js
│
├─styles
│      btn.scss
│      element-ui.scss
│      element-variables.scss
│      index.scss
│      mixin.scss
│      sidebar.scss
│      transition.scss
│      variables.scss
│
├─utils
│      auth.js
│      bus.js
│      clipboard.js
│      error-log.js
│      get-page-title.js
│      index.js
│      open-window.js
│      permission.js
│      request.js
│      scroll-to.js
│      validate.js
│
├─vendor
│      Export2Excel.js
│      Export2Zip.js
│
└─views
    ├─charts
    │      graph.vue
    │      keyboard.vue
    │      line.vue
    │      mix-chart.vue
    │
    ├─clipboard
    │      index.vue
    │
    ├─components-demo
    │      avatar-upload.vue
    │      back-to-top.vue
    │      count-to.vue
    │      dnd-list.vue
    │      drag-dialog.vue
    │      drag-kanban.vue
    │      drag-select.vue
    │      dropzone.vue
    │      json-editor.vue
    │      markdown.vue
    │      mixin.vue
    │      split-pane.vue
    │      sticky.vue
    │      tinymce.vue
    │
    ├─dashboard
    │  │  index.vue
    │  │
    │  ├─admin
    │  │  │  index.vue
    │  │  │
    │  │  └─components
    │  │      │  BarChart.vue
    │  │      │  BoxCard.vue
    │  │      │  LineChart.vue
    │  │      │  PanelGroup.vue
    │  │      │  PieChart.vue
    │  │      │  RaddarChart.vue
    │  │      │  TransactionTable.vue
    │  │      │
    │  │      ├─mixins
    │  │      │      resize.js
    │  │      │
    │  │      └─TodoList
    │  │              index.scss
    │  │              index.vue
    │  │              Todo.vue
    │  │
    │  └─editor
    │          index.vue
    │
    ├─documentation
    │      index.vue
    │
    ├─error-log
    │  │  index.vue
    │  │
    │  └─components
    │          ErrorTestA.vue
    │          ErrorTestB.vue
    │
    ├─error-page
    │      401.vue
    │      404.vue
    │
    ├─example
    │  │  create.vue
    │  │  edit.vue
    │  │  list.vue
    │  │
    │  └─components
    │      │  ArticleDetail.vue
    │      │  Warning.vue
    │      │
    │      └─Dropdown
    │              Comment.vue
    │              index.js
    │              Platform.vue
    │              SourceUrl.vue
    │
    ├─excel
    │  │  export-excel.vue
    │  │  merge-header.vue
    │  │  select-excel.vue
    │  │  upload-excel.vue
    │  │
    │  └─components
    │          AutoWidthOption.vue
    │          BookTypeOption.vue
    │          FilenameOption.vue
    │
    ├─guide
    │      index.vue
    │      steps.js
    │
    ├─icons
    │      element-icons.js
    │      index.vue
    │      svg-icons.js
    │
    ├─login
    │  │  auth-redirect.vue
    │  │  index.vue
    │  │
    │  └─components
    │          SocialSignin.vue
    │
    ├─nested
    │  ├─menu1
    │  │  │  index.vue
    │  │  │
    │  │  ├─menu1-1
    │  │  │      index.vue
    │  │  │
    │  │  ├─menu1-2
    │  │  │  │  index.vue
    │  │  │  │
    │  │  │  ├─menu1-2-1
    │  │  │  │      index.vue
    │  │  │  │
    │  │  │  └─menu1-2-2
    │  │  │          index.vue
    │  │  │
    │  │  └─menu1-3
    │  │          index.vue
    │  │
    │  └─menu2
    │          index.vue
    │
    ├─pdf
    │      content.js
    │      download.vue
    │      index.vue
    │
    ├─permission
    │  │  directive.vue
    │  │  page.vue
    │  │  role.vue
    │  │
    │  └─components
    │          SwitchRoles.vue
    │
    ├─profile
    │  │  index.vue
    │  │
    │  └─components
    │          Account.vue
    │          Activity.vue
    │          Timeline.vue
    │          UserCard.vue
    │
    ├─qiniu
    │      upload.vue
    │
    ├─redirect
    │      index.vue
    │
    ├─tab
    │  │  index.vue
    │  │
    │  └─components
    │          TabPane.vue
    │
    ├─table
    │  │  complex-table.vue
    │  │  drag-table.vue
    │  │  inline-edit-table.vue
    │  │
    │  └─dynamic-table
    │      │  index.vue
    │      │
    │      └─components
    │              FixedThead.vue
    │              UnfixedThead.vue
    │
    ├─theme
    │      index.vue
    │
    └─zip
            index.vue
```

### Graph

基于 Antv G6 实现的函数调用交互图，能够查看内核模块之间的关系。
