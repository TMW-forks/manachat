import logging


def load_plugin(config, plugin_name):
    plugin = __import__(plugin_name)
    plugin.init(config)


def load_plugins(config, plugin_names):
    for pn in plugin_names:
        try:
            load_plugin(config, pn)
            logging.info('Plugin %s loaded', pn)
        except ImportError:
            logging.error('Error loading plugin %s', pn)
