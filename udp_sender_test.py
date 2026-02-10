import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 8000

print(f"开始发送测试数据到 {UDP_IP}:{UDP_PORT}")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # 模拟发送 50 个数据包
    for i in range(0, 1000, 20):
        # 构造 T-Code: L0000 I100 到 L0980 I100
        # L0 是线性轴，I100 是间隔/速度
        msg = f"L0{i:04d} I100\n" 
        sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
        print(f"发送: {msg.strip()}")
        time.sleep(0.05) # 50ms 发送一次
        
    # 发送归位指令
    sock.sendto(b"L0500\n", (UDP_IP, UDP_PORT))
    print("发送归位指令: L0500")
    
except KeyboardInterrupt:
    print("停止发送")
finally:
    sock.close()