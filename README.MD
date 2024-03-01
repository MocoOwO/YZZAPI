# <p align="center">云中转API</p>

<p align="center">
<img src="https://img.shields.io/badge/-Python-black?style=flat-square&logo=Python" alt=""/>
<img src="https://img.shields.io/badge/-SQLite-black?style=flat-square&logo=sqlite" alt=""/>
<br>
云中转的第三方API
<br>
✨ฅ•∀•ฅ 可爱才是第一生产力 ฅ•∀•ฅ✨
<br>
(｡･ω･｡)つ━☆.. ・*。
</p>

## 简介 (⁎˃ᆺ˂)

一个云中转盘(yunzhongzhuan.com, yzzpan.com)的第三方API，同时实现了云中转盘的WebDav只读挂载(?)

~~为什么是问号啊喂~~

## 用法 ʕ•͡-•ʔ

请您创建一个config.json，内容如下
``` config.json
{
  "USERNAME": "MY_USERNAME",
  "PASSWORD": "MY_PASSWORD"
}
```
然后安装requirements.txt里的需求，启动webdav.py 就可以了。

> ~~注意: 没有外链功能可能导致文件下载失败(这是一个已知Bug)~~  
> ~~解决方案是在webdav.py中 ```flask.redirect(f"https://a.download.yunzhongzhuan.com{file.url}")``` 改成自己的域名(需要在云中转开通)~~ 
> 目前此问题已经解决，感谢官方提供的公链

## 声明 (๑•ิཬ•ั๑)

### 一切开发旨在学习，请勿用于非法用途

- YZZAPI 是完全免费且开放源代码的软件，仅供学习和娱乐用途使用
- Moco 不会通过任何方式强制收取费用，或对使用者提出物质条件
- Moco 无法监督每个使用者的使用情况，所以请自觉不要用于非法用途

### 安全性警告

- WebDav服务并没有加入认证系统，所以任何账号都可以登录！
- 此项目没有错误处理，可能会出现安全性问题
- 这个程序对于网络要求不低，请不要把它暴露在公网，以免请求过多。
- ~~Moco的程序力很低，代码可能很难看，可能会导致血压升高~~

## 关于 ISSUE (ﾟヘﾟ)？

以下 ISSUE 会被直接关闭

- 询问已知问题
- 提问找不到重点
- 重复提问

> 请注意, Moco并没有义务回复您的问题. 您应该具备基本的提问技巧。  
>有关如何提问，请阅读[《提问的智慧》](https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way/blob/main/README-zh_CN.md)

~~Moco可能会忘记看issues~~

## 鸣谢 (*ゝω・)ﾉ

咕咕咕了

<hr>
<p align="center">底线到了,再看变傻瓜ww(｡･ω･｡)つ━☆.. ・*。</p>