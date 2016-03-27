#!/usr/bin/python2

try:
    import construct
    import plyer
    # import pytmx
    del construct
    del plyer
    # del pytmx
except ImportError:
    import os
    import sys
    sys.path.append(os.path.join(os.getcwd(), "external"))

from gui.managui import ManaGuiApp


def main():
    ManaGuiApp().run()


if __name__ == "__main__":
    main()
