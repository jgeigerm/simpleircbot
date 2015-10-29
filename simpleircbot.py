import socket

class IRCBot(object):

    def __init__(self, server_tuple, nick, channel_list):
        self.server_tuple =  server_tuple
        self.nick = nick
        self.channel_list = channel_list
        self.connected = False

    def connect(self):
        if not self.connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            try:
                self.socket.connect(self.server_tuple)
                self.connected = True
            except Exception as e:
                print "Bot not connected: " + str(e)
        else:
            print "Bot already connected"

    def setnick(self, nick):
        self.sendline("NICK " + nick)

    def sendline(self, text):
        if self.connected:
            self.socket.send(text + "\n")
        else:
            print "Bot is not connected"

    def join_one(self, channel):
        self.sendline("JOIN " + channel)

    def join_all(self):
        for c in self.channel_list:
            self.join_one(c)

    def leave_one(self, channel):
        self.sendline("PART " + channel)
