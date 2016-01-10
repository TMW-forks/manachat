import os
import logging
from loggers import chatlog


class ChatLogHandler(logging.Handler):

    def __init__(self, chat_log_dir):
        logging.Handler.__init__(self, 0)
        self.chat_log_dir = chat_log_dir
        self.loggers = {}
        if not os.path.exists(self.chat_log_dir):
            os.makedirs(self.chat_log_dir)

    def emit(self, record):
        try:
            user = record.user
        except AttributeError:
            return

        user = ''.join(map(lambda c: c if c.isalnum() else '_', user))

        if user in self.loggers:
            logger = self.loggers[user]
        else:
            logger = chatlog.getChild(user)
            self.loggers[user] = logger
            # FIXME: it can open too many files, need cleanup
            handler = logging.FileHandler(os.path.join(
                self.chat_log_dir, user + ".txt"))
            logger.addHandler(handler)

        message = self.format(record)
        logger.info(message)


def log(message, user='General'):
    chatlog.info(message, extra={'user': user})
