from simpleircbot import IRCBot
bot = IRCBot(("irc server", 6667), "dad", ["#general", "#general2"])
bot.connect_and_wait()
bot.msg("#general", "hi")
bot.join("#general3")
bot.leave("#general")
bot.quit()
