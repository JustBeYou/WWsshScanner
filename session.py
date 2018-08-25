from ssh2.session import Session
from socket import socket, AF_INET, SOCK_STREAM

class SSH(object):
    socket  = None
    session = None
    channel = None

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port     = port
        self.username = username
        self.password = password

    def full_init(self):
        self.create_socket()
        if self.create_session():
            return 1
        self.create_channel()
        return 0

    def create_socket(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.hostname, self.port))

    def create_session(self):
        self.session = Session()
        self.session.set_timeout(0.5)
        self.session.handshake(self.socket)
        return self.session.userauth_password(self.username, self.password)

    def create_channel(self):
        self.channel = self.session.open_session()

    def execute_command(self, command):
        self.channel.execute(command)
        ret_data = ""
        size = 1
        while size > 0:
            size, data = self.channel.read()
            ret_data = ret_data + data

        return ret_data

    def destroy(self):
        if self.channel != None:
            self.channel.close()
        if self.socket != None:
            self.socket.close()
