# rtt_probe.py —— 掐表测"握手耗时"（RTT）：对比国内站和国际站
# 原理：socket.create_connection 内部完成 DNS 查号 + SYN 三次握手，
#       返回瞬间 = 接通。前后掐表，差值 ≈ 一个来回的时间（RTT）。
import socket
import time

HOSTS = [
    ("www.baidu.com", 80),   # 国内站
    ("github.com", 80),      # 国际站（预期：慢 + 可能丢包重传）
]
ATTEMPTS = 3

for host, port in HOSTS:
    print(f"\n目标: {host}:{port}，握手 {ATTEMPTS} 次")
    for i in range(ATTEMPTS):
        t0 = time.perf_counter()                # 拨号前，记时间
        try:
            s = socket.create_connection((host, port), timeout=3)
            t1 = time.perf_counter()            # 接通了，再记时间
            s.close()                           # 挂电话
            print(f"  第{i + 1}次握手: {(t1 - t0) * 1000:.1f} 毫秒")
        except (socket.timeout, OSError) as e:  # 3 秒内没人应答（SYN 全丢）
            print(f"  第{i + 1}次握手: 失败（{type(e).__name__}），3 秒无人应答")
