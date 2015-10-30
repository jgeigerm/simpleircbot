import socket
import select
from threading import Thread
from functools import wraps
from time import sleep
from sys import stderr, stdout

def thread(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl
    return async_func

class IRCBot(object):

    def __init__(self, server_tuple, nick, channel_list, debug=False, quiet=False):
        self.joined = []
        self.server_tuple = server_tuple
        self.debug = debug
        self.quiet = quiet
        self.nick = nick
        self.channel_list = channel_list
        self.ready = False
        self.connected = False

    @thread
    def connect(self):
        if not self.connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(15)
            try:
                self.socket.connect(self.server_tuple)
                self.pdebug("Bot connected")
                self.connected = True
            except Exception as e:
                print "Bot ({}) not connected (connect): {}".format(self.nick, str(e))
                return
            self.setnick(self.nick)
            self.sendline("USER " + self.nick + " " + self.nick + " " + self.nick + " :" + self.nick)
            try:
                self.socket.recv(2048)
            except socket.timeout as e:
                print "Timeout waiting for server response... "
                self.disconnect()
                return
            self.recvloop()
            self.ready = True
            self.pdebug("Bot ready")
            self.join_all(self.channel_list)
        else:
            print "Bot ({}) already connected".format(self.nick)

    def wait_until_ready(self):
        while not self.connected:
            sleep(.5)
        while not self.ready:
            sleep(.5)

    def connect_and_wait(self):
        self.connect()
        self.wait_until_ready()

    def disconnect(self):
        if self.connected:
            self.socket.close()
            self.connected = False
            self.ready = False
            self.joined = []
            self.pdebug("Bot disconnected")
        else:
            print "Bot ({}) not connected (disconnec)".format(self.nick)

    def quit(self, msg="Bye!"):
        self.sendline("QUIT :" + msg)
        self.disconnect()

    def pdebug(self, msg):
        if self.debug:
            stderr.write("DEBUG ({}): {}\n".format(self.nick, msg))

    def reconnect(self):
        self.close()
        self.connect()

    @thread
    def recvloop(self):
        self.pdebug("entering recvloop")
        while 1:
            if self.connected:
                try:
                    inputready = select.select([self.socket], [], [], 1)[0]
                    for sock in inputready:
                        out = self.socket.recv(2048)
                        if not self.quiet:
                            for line in out.split("\n"):
                                stdout.write("S ({}): {}\n".format(self.nick, line))
                        if out.startswith("PING"):
                            self.sendline("PONG :" + self.server_tuple[0])
                except select.error:
                    if self.connected:
                        self.disconnect()
            else:
                self.pdebug("recvloop exiting")
                return

    def setnick(self, nick):
        self.nick = nick[:9]
        self.sendline("NICK " + self.nick)

    def sendline(self, text):
        if self.connected:
            try:
                self.pdebug("Sending: " + text)
                self.socket.send(text + "\r\n")
            except socket.timeout as e:
                self.disconnect()
                print "Connection was lost! ({}): {}".format(self.nick, str(e))
        else:
            print "Bot ({}) not connected (sendline)".format(self.nick)

    def join(self, channel):
        if self.connected and self.ready:
            if channel[0] is '#' and channel not in self.joined:
                self.sendline("JOIN " + channel)
                self.joined.append(channel)
            else:
                print "'{}' is not a valid channel or has already been joined ({})".format(channel, self.nick)
        else:
            print "Bot ({}) not connected (join)".format(self.nick)

    def join_all(self, channels):
        for c in channels:
            self.join(c)

    def leave(self, channel):
        if self.connected and self.ready:
            if channel[0] is '#' and channel in self.joined:
                self.sendline("PART " + channel)
                self.joined.remove(channel)
            else:
                print "'{}' is not a valid channel or is not joined ({})".format(channel, self.nick)
        else:
            print "Bot ({}) not connected (leave)".format(self.nick)

    def msg(self, chan_usr, msg):
        self.sendline("PRIVMSG " + chan_usr + " :" + msg.rstrip())

    def msg_all_channels(self, msg):
        for c in self.joined:
            self.msg(c, msg)
