This directory contains plugins for ManaChat.

To autoload the plugin, in the [Plugins] section of manachat.ini add

[Plugins]
...
pluginname = 1
...

The plugin and it's dependencies will be autoloaded.
The plugin must export a variable PLUGIN, and the function init()

PLUGIN = {
   'name' : 'PluginName'  # not really used atm
   'requires' : (plugin1, plugin2, ...)  # list of required plugins
   'blocks' : (plugin3, plugin4, ...)    # list of incompatible plugins
}

def init(config):   # config is ConfigParser instance
    # ... plugin initialisation code ...
    pass

See 'shop.py' as an example.
