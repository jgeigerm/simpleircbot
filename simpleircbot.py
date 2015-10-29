import socket
from threading import Thread
from functools import wraps
from time import sleep

def thread(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl
    return async_func

class IRCBot(object):

    def __init__(self, server_tuple, nick, channel_list, debug=True, quiet=False):
        self.server_tuple = server_tuple
        self.debug = debug
        self.quiet = quiet
        self.nick = nick
        self.channel_list = channel_list
        self.connected = False
        self.recvloop()

    def connect(self):
        if not self.connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            try:
                self.socket.connect(self.server_tuple)
                self.connected = True
            except Exception as e:
                print "Bot not connected: " + str(e)
                return
            self.sendline("USER " + self.nick + " "  + self.nick + " " + self.nick + " :hi" )
            self.setnick(self.nick)
            print "Bot connected"
        else:
            print "Bot already connected"

    def close(self):
        if self.connected:
            self.socket.close()
            self.connected = False

    def reconnect(self):
        self.close()
        self.connect()

    @thread
    def recvloop(self):
        while 1:
            if self.connected:
                try:
                    out = self.socket.recv(2048)
                    if not self.quiet:
                        print out
                    if out.startswith("PING"):
                        self.sendline("PONG :" + self.server_tuple[0])
                except socket.timeout:
                    pass
            sleep(.5)



    def setnick(self, nick):
        self.sendline("NICK " + nick)

    def sendline(self, text):
        if self.connected:
            try:
                if self.debug:
                    print("DEBUG: " + text)
                    self.socket.send(text + "\n")
            except socket.timeout as e:
                self.connected = False
                print "Connection was lost!: " + str(e)


        else:
            print "Bot is not connected"

    def join_one(self, channel):
        self.sendline("JOIN " + channel)

    def join_all(self):
        for c in self.channel_list:
            self.join_one(c)

    def leave_one(self, channel):
        self.sendline("PART " + channel)

    def msg(self, chan_usr, msg):
        self.sendline("PRIVMSG " + chan_usr + " :" + msg)
