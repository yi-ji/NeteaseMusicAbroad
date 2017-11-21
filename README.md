# NeteaseMusicAbroad

[ English follows Chinese ]

## Mac网易云音乐解除歌曲锁区限制

### 说明

此工具帮助Mac网易云音乐的海外用户解除歌曲锁区限制（所谓锁区：很多歌曲仅限大陆地区播放）。<br/>
对用户比较友好。

为什么不使用Unblock-Youku等通用的反向代理解决方案？因为：
1. Mac版网易云音乐没有内置代理接口，全局代理会使得网络通信变慢；即便使用PAC等，歌曲下载等较大流量也会变慢，并且不稳定
2. 安全原因，请不要轻易相信商业代理服务器...
3. 此工具最傻瓜，绿色😅

不同OS下的类似工具的评论区经常出现“买个会员不就好了”等言论，注意：
1. 即便会员，该锁区也一样锁区，会员只是可以听网易版权歌曲
2. 想了想还是算了，不说了

感谢[一个Windows下类似工具](https://github.com/tiancaihb/NeteaseReverseLadder)提供的思路以及作者的[博文](https://zhuanlan.zhihu.com/p/23601736)。

此工具的使用、传播、修改均无需征得作者同意，同时作者对此不负一切责任。

### 使用方法

需要条件：<br/>
下载该repo文件夹，不要修改任何文件名<br/>
安装python包[Twisted](https://github.com/twisted/twisted)和PyQuery（均可用pip安装）。<br/>
最新版本的Twisted需要更新pyOpenSSL才能使用。也可以选择装个旧版本。

在每次打开网易云音乐之前：<br/>
进入文件夹，双击NeteaseMusicHelper即可。等待提示信息成功之后可以关掉它，然后一片清净，开心听歌，不用善后。<br/>

### 测试环境

macOS 10.12，NeteaseMusic Version 1.5.6，python 2.7.10，年费会员。未测试任何其他情况，欢迎测试报bug谢谢。

### 实现细节

见下方Inplementation details。这里只说两点：<br/>
1. 歌单中所有歌曲都不再显示灰色，但点击部分下架歌曲（大陆也不能播放）后仍然可能提示“播放失败”。<br/>
2. 目前对音频文件URL请求（也只有这一请求）采用的是cn-proxy提供的代理列表，缺省代理为作者的阿里云地址。

_________________

### Introduction

This tool helps abroad users of NeteaseMusic for macOS unblock songs that are allowed to play in mainland China only.

Why general solutions like Unblock-Youku are not recommended? Because:
1. NeteaseMusic for macOS does not provide a proxy interface, so global proxy will slow down the network traffic; Even if PAC is used, when it comes to audio stream downloading, the latency and unstableness become annoying.
2. For safety reasons, better not to trust commercial proxy servers.
3. This tool is most lightweight and easy to use.

Thanks to a similar tool [NeteaseReverseLadder](https://github.com/tiancaihb/NeteaseReverseLadder) on Windows and the author's [blog](https://zhuanlan.zhihu.com/p/23601736).

Copyright: The author waives all rights, please feel free to use, share and modify this tool.

### Usage

Prerequisites: <br/>
1. Download this folder and do not change file names.
2. Install Python package [Twisted](https://github.com/twisted/twisted) and PyQuery. You may also need to update pyOpenSSL or use a older version of Twisted.

Everytime before you launch NeteaseMusic:<br/>
Just enter the folder and double-click "NeteaseMusicHelper". See the success info and then be free to close it, enjoy your music.

### Test Environment

macOS 10.12，NeteaseMusic Version 1.5.6，python 2.7.10, yearly-paid membership.<br/>
Other cases are not tested and your report is welcomed.

### Implementation Details

Part 1. Force NeteaseMusic to communicate with Netease servers through local proxy.

Methods that I tried:
1. Use `pfctl` (package forwarding), like `iptables` on Linux. Not working normally & too less helpful documentations, given up.
2. Use [proxychains](https://github.com/rofl0r/proxychains-ng), a preloader which hooks calls to sockets in dynamically linked programs and redirects it through proxies. It is basically a hack and hacks do not always work. Acting weired on NeteaseMusic for macOS, issue reported at [#181](https://github.com/rofl0r/proxychains-ng/issues/181). Remaining unsolved.
3. Use `networksetup`, macOS network PAC. It works easily.

Part 2. Intercept, modify and redirect requests.

See `NeteaseMusicProxy.py` (deployed as local proxy) and `AudioRequestProxy.py` (deployed as domestic proxy).

Mainland proxy server is dynamically selected from http://cn-proxy.com/. Because those proxies can be unstable (may be refused by NeteaseMusic server), so an auto proxy selector will replace current proxy with new one or default one after a certain amount of request failures.
