import time
class A:
    def __init__(self, dummy=False):
        self.dummy = dummy
        self.ser = self
        self.is_open = True
        self.ws_server = None

    def write(self, d): pass
    def broadcast(self, d): pass

a = A()

def orig():
    cmd_str = "L0500"
    if a.dummy or not a.ser or not a.ser.is_open:
        return
    if not cmd_str.endswith('\n'):
        cmd_str += '\n'
    if hasattr(a, 'ws_server') and a.ws_server:
        a.ws_server.broadcast(cmd_str.strip())
    a.ser.write(cmd_str.encode())

def new1():
    cmd_str = "L0500"
    if a.dummy or not a.ser or not a.ser.is_open:
        return
    if cmd_str[-1] != '\n':
        cmd_str += '\n'
    if a.ws_server:
        a.ws_server.broadcast(cmd_str.strip())
    a.ser.write(cmd_str.encode())

start = time.time()
for _ in range(1000000): orig()
print("Orig:", time.time() - start)

start = time.time()
for _ in range(1000000): new1()
print("New1:", time.time() - start)
