# proxy.py —— 反向代理：前台店。客人只跟它说话，它替客人去后厨取菜
import socket

LISTEN_HOST, LISTEN_PORT = "127.0.0.1", 8002   # 前台门牌
BACK_HOST, BACK_PORT = "127.0.0.1", 8001       # 真正的后厨（server.py）

front = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
front.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
front.bind((LISTEN_HOST, LISTEN_PORT))
front.listen(5)
print(f"前台店开张: http://{LISTEN_HOST}:{LISTEN_PORT}  （真菜在后厨 {BACK_PORT}）")

while True:
    conn, addr = front.accept()            # 接待客人（对客人来说，前台就是店）
    req = conn.recv(65535)                 # 客人的原话——不看内容，原样转
    if not req:
        conn.close()
        continue

    # 前台转身去后厨点菜：此刻它是一个客户端（对后厨来说，前台就是客人）
    try:
        back = socket.create_connection((BACK_HOST, BACK_PORT), timeout=3)
        back.sendall(req)                  # 一字不改递过去
        dish = b""
        while True:
            chunk = back.recv(4096)
            if not chunk:
                break
            dish += chunk
        back.close()
        conn.sendall(dish)                 # 菜端给客人——他不知道菜是后厨做的
    except OSError:
        # 后手：后厨失联/超时，前台不倒，给客人一个交代
        bad = (
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Connection: close\r\n\r\n"
            "<h1>502</h1><p>前台在，后厨失联了</p>"
        )
        conn.sendall(bad.encode("utf-8"))
    finally:
        conn.close()
