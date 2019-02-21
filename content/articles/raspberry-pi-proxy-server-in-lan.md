Title: 树莓派局域网代理加速 Tetris® 99 for Nintendo Switch
Date: 2019-02-17 17:30
Category: linux
Tags: linux, raspberrypi
Slug: raspberry-pi-as-proxy-server-in-lan
Authors: 
Summary: 通过设置 privoxy over ss-local 作为局域网代理服务器，来加速 Switch 的网络连接

## 1. Tetris® 99 的网络连接问题

任天堂在 2 月 13 日推出了一款大逃杀模式的俄罗斯方块游戏 [Tetris® 99 for Nintendo Switch](https://www.nintendo.com/games/detail/tetris-99-switch)。作为一名 Tetris 老玩家，自然是不能错过。由于是在线对战游戏，对网络质量要求较高。对战过程中经常出现网络连接失败导致自动退出，气得很想摔 Switch。

最简单的方法是[修改 Switch 网络设置的 DNS](https://twitter.com/ibingfei/status/1096354236047081472)，但效果并不好，下载游戏很快，但对战更容易掉线。

给路由器添加代理支持是个好办法，但我现在用的路由器不支持，安装插件后无法正常连接代理节点，只好另辟蹊径。

Switch 的网络接入点里面有 HTTP 代理的设置项，而我的 MacBook 上有 [Surge](https://nssurge.com/) 支持局域网访问，此法可行。但是这个方案需要 MacBook 一直保持在唤醒状态，休眠的话 Tetris 99 立刻掉线给你看，所以只能作为临时方案使用。

正好抽屉里还有个 24 小时运行的树莓派，做局域网 HTTP 代理服务器最合适不过了。shadowsocks 是最流行的代理方式，但它的官方客户端只支持 socks5 协议的流量，因此我们还需要一个将 HTTP 流量转换为 socks5 流量的工具，[privoxy](https://wiki.archlinux.org/index.php/Privoxy_(简体中文)) 可以做到。

## 2. 给树莓派安装 shadowsocks

首先，安装 [shadowsocks-libev](https://github.com/shadowsocks/shadowsocks-libev)：

```sh
$ sudo apt-get update
$ sudo apt-get install shadowsocks-libev
```

配置节点信息：

```sh
$ sudo vim /etc/shadowsocks-libev/config.json
```

文件格式如下：

```
{
    "server":"REMOTE-SERVER-IP-OR-DOMAIN",
    "server_port":"REMOTE-PORT",
    "local_address":"127.0.0.1",
    "local_port":1080,
    "password":"YOUR-PASSWORD",
    "method":"YOUR-METHOD"
}
```

这时运行 `ss-local` 命令，你就可以在的前台看到节点连接情况。但当你关闭 SSH 会话时，这个进程也会停止，因此需要把它设为服务运行。

### 设置 `ss-local` 服务

编辑 `ss-local` 服务的配置文件 `/lib/systemd/system/ss-local.service`：

```sh
$ sudo vim /lib/systemd/system/ss-local.service
```

文件内容如下（格式参考了 `/lib/systemd/system/shadowsocks-libev.service`）：

```
[Unit]
Description=Shadowsocks-libev Default Client Service
Documentation=man:ss-local
After=network.target

[Service]
Type=simple
EnvironmentFile=/etc/default/shadowsocks-libev
User=nobody
Group=nogroup
LimitNOFILE=32768
ExecStart=/usr/bin/ss-local -c /etc/shadowsocks-libev/config.json

[Install]
WantedBy=multi-user.target
```

启用 `ss-local.service`：

```sh
$ sudo systemctl start ss-local.service  # 启动服务
$ sudo systemctl enable ss-local.service # 设置开机自启动
```

现在 `ss-local.service` 服务已经成功运行了，测试一下：

```sh
$ curl --socks5 localhost:1080 ipconfig.io
```

你应该看到输出了远程 ss 代理节点的 IP 地址。

## 3. 安装 privoxy 转发 HTTP 流量

[privoxy](https://wiki.archlinux.org/index.php/Privoxy_(简体中文)) 是一个 HTTP 协议过滤代理软件，安装：

```sh
$ sudo apt-get install privoxy
```

修改配置文件 `/etc/privoxy/config`：

```sh
$ sudo vim /etc/privoxy/config
```

在文件底部添加：

```
forward-socks5 / 127.0.0.1:1080 . # 转发目的地址，注意末尾有一个空格和点号
listen-address  0.0.0.0:8010      # 监听局域网本机地址和端口
```

`privoxy.service` 服务在安装时已经启用，可以通过 `systemctl status privoxy.service` 来确认，现在重启该服务：

```sh
$ sudo systemctl restart privoxy.service
```

现在 `privoxy.service` 服务已经成功运行了，测试一下：

```sh
$ curl -x, --proxy localhost:8010 ipconfig.io
```

你应该看到输出了远程 ss 代理节点的 IP 地址。

## 4. 最后一步

树莓派的代理服务已经成功运行，现在还需要在路由器的设置里面把树莓派的 IP 固定下来，以免每次树莓派切换 IP 还需要更改相应的 Switch 设置。

如果你设置的静态 IP 和当前不一致，需要重启一下树莓派的网络服务：

```sh
$ sudo ifconfig wlan0 down; sleep 10; sudo ifconfig wlan0 up
```

然后在 Switch 的网络接入点配置里添加代理的 IP （树莓派的静态 IP）和端口号 8010，保存并重新连接此接入点，提示连接成功，即可开始体验 Tetris® 99 了。

彩蛋：

![Tetris® 99 screenshot](https://pbs.twimg.com/media/DznlORWU8AELB0h.jpg)