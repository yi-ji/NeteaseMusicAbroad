# NeteaseMusicAbroad

[ English follows Chinese ]

## Mac网易云音乐解除歌曲锁区限制

### 说明

此工具帮助Mac网易云音乐的海外用户解除歌曲锁区限制（所谓锁区：很多歌曲仅限大陆地区播放）。对用户比较友好。

为什么不使用Unblock-Youku等通用的反向代理解决方案？因为：
1. Mac版网易云音乐没有内置代理接口，全局代理会使得网络通信变慢；即便使用PAC等，歌曲下载等较大流量也会变慢，并且不稳定
2. 安全原因，请不要轻易相信商业代理服务器...
3. 此工具最傻瓜，绿色😅

不同OS下的类似工具的评论区经常出现“买个会员不就好了”等言论，注意：
1. 即便会员，该锁区也一样锁区，会员只是可以听网易版权歌曲
2. 想了想还是算了，不说了

感谢[一个Windows下类似工具](https://github.com/tiancaihb/NeteaseReverseLadder)提供的思路以及作者的[博文](https://zhuanlan.zhihu.com/p/23601736)。

### 使用方法

需要条件：<br/>
下载该repo文件夹，不要修改任何文件名<br/>
安装python包[Twisted](https://github.com/twisted/twisted)。<br/>
最新版本的twisted可能需要update一下你的pyOpenSSL才能使用。也可以选择装个旧版本。

在每次打开网易云音乐之前：<br/>
进入文件夹，双击NeteaseMusicHelper即可。等待提示信息成功之后可以关掉它，然后一片清净，开心听歌，不用善后。

### 测试环境

macOS 10.12，NeteaseMusic Version 1.5.6，年费会员。未测试任何其他情况，欢迎测试报bug谢谢。

### 实现细节

见下方Inplementation details。这里只说两点：<br/>
1. 歌单中所有歌曲都不再显示灰色，但点击无版权歌曲（大陆也不能播放）后仍然会提示“播放失败”。暂无解决思路，且不想涉及版权法。<br/>
2. 目前对音频文件URL请求（也只有这一请求）走的是窝的国内阿里云。显然带宽很小，有时有一点延迟。TODO：换成自动使用 http://cn-proxy.com/ 的免费代理。
