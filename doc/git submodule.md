# GIT 子模块使用

>官方文档连接
> <https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97>

在项目中使用子模块的最简模型，就是只使用子项目并不时地获取更新，而并不在你的检出中进行任何更改。

```sh
git clone --recurse-submodules
```

如果给 git clone 命令传递 --recurse-submodules 选项，它就会自动初始化并更新仓库中的每一个子模块， 包括可能存在的嵌套子模块。

```sh
git pull --recurse-submodules
```

当运行 git submodule update --remote 时，Git 默认会尝试更新所有子模块， 所以如果有很多子模块的话，你可以传递想要更新的子模块的名字。

Git 进入到 DbConnector 模块中然后在推送主项目前推送了它。 如果那个子模块因为某些原因推送失败，主项目也会推送失败。
$ git push --recurse-submodules=on-demand
