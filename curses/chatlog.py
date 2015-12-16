import logging
import cui

chatlog = logging.getLogger("ManaChat.Chat")
chatlog.setLevel(logging.INFO)

class ChatLogHandler(logging.Handler):
    """
    Logging handler that prints messages to chat log.
    """

    def emit(self, record):
        msg = self.format(record)
        cui.chatlog_append(msg)

ch = ChatLogHandler()
ch.setLevel(logging.INFO)
fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M")
ch.setFormatter(fmt)

chatlog.addHandler(ch)

del ch, fmt
