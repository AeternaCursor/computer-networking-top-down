# client.py —— 自己当客人：手写 HTTP 客户端，去敲自己的店
import socket

HOST = "127.0.0.1"   # 店的地址（本机）
PORT = 8001          # 店的门牌
PATH = "/about"      # 要的菜

# 1) 出门、找路、敲门 —— connect 的一瞬间三次握手完成
s = socket.create_connection((HOST, PORT), timeout=3)

# 2) 按村里的规矩开口：请求行 → 头 → 空行
req = (
    f"GET {PATH} HTTP/1.1\r\n"
    f"Host: {HOST}:{PORT}\r\n"
    "User-Agent: my-hand-client/0.1\r\n"
    "Connection: close\r\n"
    "\r\n"
)
s.sendall(req.encode("utf-8"))

# 3) 听店回话。店说了"说完就挂"（Connection: close），
#    所以一直听到对方挂断（recv 返回空）就是收完了
data = b""
while True:
    chunk = s.recv(4096)
    if not chunk:
        break
    data += chunk
s.close()

print(data.decode("utf-8"))
