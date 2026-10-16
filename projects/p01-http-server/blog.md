# P1 · 手写 HTTP 服务器（阶段一：开店营业）

> 对应章节：第 2 章 2.7（套接字编程）。本篇覆盖服务器部分；客户端与反向代理见后续。

## 1. 现象

30 行 Python 在 `127.0.0.1:8001` 开店。浏览器访问 `/`、`/about` 各得上菜，未知路径得 404。`curl.exe -v` 拿到完整对话实录：

```
> GET /about HTTP/1.1          "来份 about"
> Host: 127.0.0.1:8001         "我去的是这家店"
> User-Agent: curl/8.13.0      "我是 curl"
> Accept: */*                  "啥都行"

< HTTP/1.1 200 OK              "有货"
< Content-Type: text/html; charset=utf-8
< Content-Length: 65
< Connection: close
<h1>关于本店</h1><p>...</p>     ← 正文
```

与 P0 抓 example.com 看到的响应格式逐字段一致——这次是自己的代码发出来的。

## 2. 矛盾

- 一台机器一个 IP，凭什么开多家店？→ **端口**（0~65535，店家门牌）
- 客人五花八门的要法怎么区分？→ 解析**请求行**（`GET /路径 HTTP/1.1`），按路径分发
- 出错了，锅是谁的？→ 错误必须分层归责

## 3. 设计

- `accept()` 返回的瞬间 = 三次握手完成 = "开门接客"，之后 `conn` 是一条专线
- 响应格式是铁律：**状态行 → 头 → 空行 → 正文**，空行是头和正文的分界
- `Content-Length` 必须是**字节数**：正文含中文时 `len(body)` ≠ `len(body.encode())`（UTF-8 中文 3 字节/字，本例 65 字节）
- 不存在的路径由**服务器代码**回 `404`——店开着，只是没这道菜

## 4. 实现

演进两版：

- **v1**：固定响应。socket → bind → listen → 循环 accept/recv/send/close
- **v2**：拆解请求行 `method, path, _ = first_line.split(" ", 2)`，按 `/`、`/about` 分发，其余走 `404 Not Found`；回话抽成 `send_response()` 函数

## 5. 验证（实测三层错误）

| 现象 | 谁回的话 | 实测方式 |
|---|---|---|
| `Connection refused`（秒拒） | **操作系统** | 端口改 8001 后再访问 8000，立刻拒绝——店没开 |
| `404 Not Found` | **服务器代码** | 访问未知路径 |
| `Connection timed out`（干等） | 没人回 | P0 实测 GitHub：SYN 石沉大海 + RTO 重传 |

排障第一刀：**先问报错来自哪一层**。refused=店不在，404=店在菜没有，timeout=路不通。

## 6. 升华与遗留

- 浏览器、curl、Python `socket`，说的是同一套话——协议就是跨软件的"普通话"
- PowerShell 的 `curl` 是 `Invoke-WebRequest` 的别名，真 curl 要敲 `curl.exe`
- 下阶段：① 自己当客人（手写 HTTP 客户端）② 反向代理（一家店替你去多家店取菜）
