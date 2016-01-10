import logging
import sys

sys.path.insert(0, "plugins")
debuglog = logging.getLogger("ManaChat.Debug")


def load_plugin(config, plugin_name):
    plugin = __import__(plugin_name)
    plugin.init(config)


def load_plugins(config, *plugin_names):
    for pn in plugin_names:
        try:
            load_plugin(config, pn)
            debuglog.info('Plugin %s loaded', pn)
        except ImportError:
            debuglog.error('Error loading plugin %s', pn)
