Title: 树莓派3零附件配置 Wi-Fi 和 SSH
Date: 2018-01-03 17:30
Category: linux
Tags: linux, raspberrypi
Slug: raspberry-pi-3-setup
Authors: 
Summary: 在没有外接键盘和显示器的条件下，配置树莓派通过 Wi-Fi 进行 SSH 登录

[树莓派](https://raspberrypi.org/)是一款基于 Linux 的单片机，由于体积小巧，价格低廉，可以用来学习 Linux 系统，编写并运行小型应用，做[家庭影音服务中心](https://kodi.tv/)等。

几天前朋友送给我一块[树莓派 3B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)，拥有四核 1.2GHz 64 位 ARM CPU，1GB LPDDR2 内存，四个 USB 2.0 接口，一个 MicroSD 卡槽，一个百兆以太网接口，支持 Wi-Fi 802.11n 和 蓝牙 4.1。

## 1. 安装系统

树莓派官方的操作系统 [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) 有三个版本：

- Raspbian with desktop and recommended software
- Raspbian with desktop
- Raspbian Lite

我安装的是非桌面版本 Raspbian Lite，通过烧录工具 [ApplePi-Baker](https://www.tweaking4all.com/software/macosx-software/macosx-apple-pi-baker/) for macOS 把下载好的镜像文件[写入 SD 卡](https://sspai.com/post/38542)。

## 2. 启用 SSH

几乎所有的教程都会要求使用外接键盘和显示器连接树莓派进行接下来的操作。如果没有这些附件怎么办呢？办法是有的。

SSH 默认状态下是关闭的，启用的方法是在 Raspbian 系统目录 `/mnt/sdc1` 下创建一个名为 `ssh` 的空文件。

## 3. 启用自动连接 Wi-Fi

在启用 SSH 的情况下，可以通过网络连接树莓派，比如网线或者 Wi-Fi。如果你恰好和我一样没有网线，或者只是讨厌给树莓派多插一条线的话，还可以通过 Wi-Fi 进行连接。

Wi-Fi 默认状态也是关闭的，幸运的是我找到了这个[帖子](https://raspberrypi.stackexchange.com/questions/37920/how-do-i-set-up-networking-wifi-static-ip-address/37921#37921)，里面介绍了在烧录系统后直接配置 Wi-Fi 的方法。

Raspbian 在启动时会检查 `/boot` 目录下的 `wpa_supplicant.conf` 文件并把它移动到 `/etc/wpa_supplicant/wpa_supplicant.conf` （如果文件已存在则会被覆盖），可以在这里进行 Wi-Fi 连接的参数配置。

在 Raspbian 根目录下新建 `wpa_supplicant.conf` 文件并添加进下面几行：

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="SSID"
    psk="PASSWORD"
}
```

然后，替换 `SSID` 和 `PASSWORD` 为你希望连接的 Wi-Fi 名称和密码。

## 4. 运行树莓派并通过 Wi-Fi 进行 SSH 登录

现在你可以把树莓派插卡通电放到角落里了。在终端中输入 `ssh pi@raspberrypi.local` 进行登录，使用 `raspberry` 作为初始密码。现在你应该已经登入了树莓派，可以按照自己的想法使用它了。

希望这篇文章对你有所帮助。