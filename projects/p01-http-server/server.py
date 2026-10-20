# server.py v2 —— 会看菜单的店：按客人要的路径上菜，没有的菜回 404
import socket

HOST = "127.0.0.1"
PORT = 8001

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(5)
print(f"服务器已启动: http://{HOST}:{PORT}  （Ctrl+C 停止）")


def send_response(conn, status_line, body, content_type="text/html; charset=utf-8"):
    """按村里规矩回话：状态行 → 头 → 空行 → 正文"""
    resp = (
        f"{status_line}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{body}"
    )
    conn.sendall(resp.encode("utf-8"))
    conn.close()


while True:
    conn, addr = srv.accept()                      # 开门接客（握手完成）
    conn.settimeout(3)                             # 防卡死：客人光坐着不点菜就请出去
    try:
        req = conn.recv(65535).decode("utf-8", errors="replace")
        if not req:
            conn.close()
            continue
        first_line = req.splitlines()[0]           # 形如 "GET /about HTTP/1.1"
        method, path, _ = first_line.split(" ", 2)
        print(f"客人要: {method} {path}")

        if path == "/":
            send_response(conn, "HTTP/1.1 200 OK",
                          "<h1>欢迎光临</h1><p>这是首页，我是你亲手养的服务器</p>")
        elif path == "/about":
            send_response(conn, "HTTP/1.1 200 OK",
                          "<h1>关于本店</h1><p>P1 练习店，店主：AeternaCursor</p>")
        else:
            send_response(conn, "HTTP/1.1 404 Not Found",
                          "<h1>404</h1><p>本店没有这道菜</p>")
    except OSError:
        conn.close()                               # 这单砸了就砸了，店接着开
