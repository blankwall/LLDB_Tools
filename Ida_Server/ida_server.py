import socket,time,threading,code


class Server():
    def __init__(self, host='localhost', port=11946):
        self.s = socket.socket()
        self.s.bind((host, port))
        self.data = ""
        self.serve_loop()

    def serve_loop(self):
        self.s.listen(5)
        while True:
           c, addr = self.s.accept()     # Establish connection with client.
           print 'Got connection from', addr
           while True:
               self.data = c.recv(1000)
               try:
                   exec(str(self.data))
               except:
                   print "BAD MESSAGE", self.data
               self.data = ""


def server_runner():
    s = Server()


if __name__ == '__main__':
    print "Starting server"
    t = threading.Thread(target=server_runner)
    t.start()
    print "Running server in background"
