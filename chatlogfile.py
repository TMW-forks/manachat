import os
import logging
import config


class ChatLogFiles:

    def __init__(self, chat_log_dir):
        self.chat_log_dir = chat_log_dir
        self.loggers = {}
        if not os.path.exists(self.chat_log_dir):
            os.makedirs(self.chat_log_dir)

    def log(self, message, user="General"):
        user = ''.join(map(lambda c: c if c.isalnum() else '_', user))

        if user in self.loggers:
            logger = self.loggers[user]
        else:
            logger = logging.getLogger("ManaChat.ChatLogFiles." + user)
            logger.setLevel(logging.INFO)
            self.loggers[user] = logger
            handler = logging.FileHandler(os.path.join(
                self.chat_log_dir, user + ".txt"))
            formatter = logging.Formatter("[%(asctime)s] %(message)s",
                                          datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.info(message)


root_logger = ChatLogFiles(config.chatlog_dir)


def log(message, user="General"):
    root_logger.log(message, user=user)
