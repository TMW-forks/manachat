import logging
import sys

sys.path.insert(0, "plugins")
debuglog = logging.getLogger("ManaChat.Debug")

plugins_loaded = []


class PluginError(Exception):
    pass


def load_plugin(config, plugin_name):
    if plugin_name in plugins_loaded:
        return

    plugin = __import__(plugin_name)

    for p in plugin.PLUGIN['blocks']:
        if p in plugins_loaded:
            raise PluginError("{} blocks {}".format(p, plugin_name))

    for p in plugin.PLUGIN['requires']:
        if p not in plugins_loaded:
            load_plugin(config, p)

    this = sys.modules[__name__]
    setattr(this, plugin_name, plugin)

    # filling the gaps in config
    if not config.has_section(plugin_name):
        config.add_section(plugin_name)

    default_config = plugin.PLUGIN.setdefault('default_config', {})
    for option, value in default_config.iteritems():
        if not config.has_option(plugin_name, option):
            config.set(plugin_name, option, str(value))

    plugin.init(config)
    plugins_loaded.append(plugin_name)
    debuglog.info('Plugin %s loaded', plugin_name)


def load_plugins(config):
    for pn in config.options('Plugins'):
        if config.getboolean('Plugins', pn):
            try:
                load_plugin(config, pn)
            except ImportError as e:
                debuglog.error('Error loading plugin %s: %s', pn, e)
