# NeteaseMusicAbroad

[ English follows Chinese ]

## Mac/Linux网易云音乐解除歌曲锁区限制

### 说明

此工具帮助Mac/Linux网易云音乐的海外用户解除歌曲锁区限制（所谓锁区：很多歌曲仅限大陆地区播放）。<br/>
对用户比较友好。

为什么不使用Unblock-Youku等通用的反向代理解决方案？因为：
1. Mac/Linux版网易云音乐没有内置代理接口，全局代理会使得网络通信变慢；即便使用PAC等，歌曲下载等较大流量也会变慢，并且不稳定
2. 安全原因，请不要轻易相信商业代理服务器...
3. 此工具最傻瓜，绿色😅

不同OS下的类似工具的评论区经常出现“买个会员不就好了”等言论，注意：
1. 即便会员，该锁区也一样锁区，会员只是可以听网易版权歌曲
2. 想了想还是算了，不说了

感谢[一个Windows下类似工具](https://github.com/tiancaihb/NeteaseReverseLadder)提供的思路以及作者的[博文](https://zhuanlan.zhihu.com/p/23601736)。

此工具的使用、传播、修改均无需征得作者同意，同时作者对此不负一切责任。

### 使用方法

需要条件：<br/>
1. 下载该repo文件夹，不要修改任何文件名<br/>
2. `pip install twisted requests pyquery --user` <br/>

#### macOS
进入文件夹，双击`NeteaseMusicHelper`来启动网易云音乐。提示成功之后可以关掉终端窗口，然后开心听歌，不用善后。<br/>

#### Linux
`vim /usr/share/applications/netease-cloud-music.desktop` <br/>
修改Exec变量为：<br/>
`Exec=/bin/bash -c "unset SESSION_MANAGER && netease-cloud-music %U & cd __YOUR_PATH_TO_NeteaseMusicHelper__ && ./NeteaseMusicHelper"` <br/>
以后只需正常从桌面图标启动网易云音乐即可。

\*  为什么要`unset SESSION_MANAGER`？详见[这里](https://www.zhihu.com/question/277330447)

#### FAQ
- 运行之后无效怎么办？<br/>
  - 检查是否正确安装了依赖库：`python -c "import twisted; import requests; import pyquery; exit"`
  - 打开：_系统偏好设置 -> 网络 -> 高级 -> 代理 -> 自动代理配置_ 是否被勾选？ 配置文件的路径是否存在？
  - 第一次使用时，请尝试反复切换刷新歌单若干次
  - 如多次尝试，请先退出网易云音乐等待1分钟或者`` kill -9 `ps x | grep NeteaseMusic | awk '{print $1}'` ``
  - 如仍然无效，请执行`python NeteaseMusicProxy.py`将输出贴在issue里，并标明网络环境（Wi-Fi/有线网络等）

- 使用Python 3的话需要怎么做？<br/>
  - 确认安装了Python 3版本的上述packages（如使用`pip`安装则查看`pip -V`，等等）
  - 如果`python -V`提示版本在3以上，直接正常使用即可；否则, 将`run_*.sh`里面的`python`替换为你的`python3`


### 测试环境

年费会员;
- macOS 10.12 & NeteaseMusic Version 1.5.6~1.5.9 & python 2.7.10/3.6.5 <br/>
- Linux Ubuntu 18.04 & NeteaseMusic Version 1.1.0 & python 2.7.15/3.6.6 <br/>

未测试任何其他情况，欢迎测试报bug谢谢。

### 实现细节

见下方Inplementation details。这里只说两点：<br/>
1. 歌单中所有歌曲都不再显示灰色，但点击部分下架歌曲（大陆也不能播放）后仍然可能提示“播放失败”。<br/>
2. 目前对音频文件URL请求（也只有这一请求）采用的是cn-proxy提供的代理列表，缺省代理为作者的阿里云地址。

_________________

### Introduction

This tool helps abroad users of macOS/Linux NeteaseMusic unblock songs that are allowed to play in mainland China only.

Why general solutions like Unblock-Youku are not recommended? Because:
1. NeteaseMusic on macOS/Linux does not provide a proxy interface, so global proxy will slow down the network traffic; Even if PAC is used, the latency and unstableness become annoying when it comes to audio stream downloading.
2. For safety reasons, better not to trust commercial proxy servers.
3. This tool is most lightweight and easy to use.

Thanks to a similar tool [NeteaseReverseLadder](https://github.com/tiancaihb/NeteaseReverseLadder) on Windows and the author's [blog](https://zhuanlan.zhihu.com/p/23601736).

Copyright: The author waives all rights, please feel free to use, share and modify this tool.

### Usage

Prerequisites: <br/>
1. Download this folder and do not change file names.
2. `pip install twisted requests pyquery --user`

#### macOS
Enter the folder and double-click `NeteaseMusicHelper` to launch NeteaseMusic. See the success info and then be free to close it, enjoy your music.

#### Linux
Do this at the first time: <br/>
`vim /usr/share/applications/netease-cloud-music.desktop` <br/>
Change "Exec" variable to `Exec=/bin/bash -c "unset SESSION_MANAGER && netease-cloud-music %U & cd __YOUR_PATH_TO_NeteaseMusicHelper__ && ./NeteaseMusicHelper"` <br/>
Then enjoy NeteaseMusic by simply clicking its desktop icon from now on.

#### FAQ
- Not working? <br/>
  - Make sure packages are installed：`python -c "import twisted; import requests; import pyquery; exit"`
  - Navigate to：_Systems Preferences -> Network -> Advanced -> Proxies -> Automatic Proxy Configuration_, is it checked? Does the config path exist?
  - For first launch, please switch playlists and refresh for a couple of times
  - If try again, please exit netease-cloud-music first and wait 1 min or`` kill -9 `ps x | grep NeteaseMusic | awk '{print $1}'` ``
  - If still not working, please run `python NeteaseMusicProxy.py` and paste the output to your issue, also report your network type (e.g. Wi-Fi/Ether)

- What if using Python 3？<br/>
  - Make sure packages above are installed for Python 3 (e.g. by checking `pip -V`)
  - If `python -V` return version > 3, do nothing; Otherwise, replace `python` in `run_*.sh` to `python3`
  
### Test Environment

Yearly-paid membership;
- macOS 10.12 & NeteaseMusic Version 1.5.6~1.5.10 & python 2.7.10/3.6.5 <br/>
- Linux Ubuntu 18.04 & NeteaseMusic Version 1.1.0 & python 2.7.15/3.6.6 <br/>

Other cases are not tested and your report is welcomed.

### Implementation Details

Part 1. Force NeteaseMusic to communicate with Netease servers through local proxy.

#### macOS

Methods that I tried:
1. Use `pfctl` (package forwarding), like `iptables` on Linux. Not working normally & too less helpful documentations, given up.
2. Use [proxychains](https://github.com/rofl0r/proxychains-ng), a preloader which hooks calls to sockets in dynamically linked programs and redirects it through proxies. It is basically a hack and hacks do not always work. Acting weired on NeteaseMusic for macOS, issue reported at [#181](https://github.com/rofl0r/proxychains-ng/issues/181). Remaining unsolved.
3. Use `networksetup`, macOS network PAC. It works easily.

#### Linux

Finally I chose `gsettings` tool provided by GNOME for redirecting traffics because root privilege won't be needed.
`iptables` can also do the job:
```
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A OUTPUT -p tcp -d music.163.com -j REDIRECT --to-ports 32794
```
but requires to fix redirection-modified request headers. Target parameter `TPROXY` instead of `REDIRECT` is actually built for this, however we have another problem unsolved in our case: [How to let locally generated packets pass through PREROUTING chain?](https://unix.stackexchange.com/questions/469477/how-to-let-locally-generated-packets-pass-through-prerouting-chain)

Part 2. Intercept, modify and redirect requests.

See `NeteaseMusicProxy.py` (deployed as local proxy) and `AudioRequestProxy.py` (deployed as default mainland proxy).

Mainland proxy server is dynamically selected from http://cn-proxy.com/. Because those proxies can be unstable (may be refused by NeteaseMusic server), so an auto proxy selector will replace current proxy with new one or default one after a certain amount of request failures.
