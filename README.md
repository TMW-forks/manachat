# README #

## Table of contents ##
1. About
2. Dependencies
3. Installation
4. Configuration
5. Usage
6. Author
7. Links

## About ##
ManaChat is a chat client for The Mana World MMORPG. It is written on Python,
and provides few types of user interface (headless, curses, kivy GUI). It is
extendable via plugins.

## Dependencies ##
 * Python 2.7
 * ncurses (optional)
 * Kivy 1.9.1 (recommended)
 * python-construct-2.5.2 (bundled)
 * Plyer 1.2.4 (bundled)
 * six 1.10.0 (bundled)

## Installation ##
Download the latest version:
```
# wget https://bitbucket.org/rumly111/manachat/get/tip.zip
# unzip tip.zip
```
Alternatively you can use Mercurial CVS to stay up-to-date with ease:
```
# hg clone https://bitbucket.org/rumly111/manachat/
```
For more information see INSTALL.txt

## Configuration ##
The main config file is manachat.ini, you can change your settings by
editing it. But if you are using Kivy GUI, it has it's own settings
window (press F1 to display it), which modifies manachat.ini automatically.

## Usage ##
Several versions of progam is provided:
```
./main.py          -- starts the Kivy GUI
./headless.py      -- useful for debugging errors
./simple.py        -- simple console client with many features
./curses/tmwcli.py -- ncurses-based interface
```

## Author ##
Joseph Botosh <rumly111@gmail.com> (TMW nickname: Travolta)

## Links ##
* Project homepage: https://bitbucket.org/rumly111/manachat/
* The Mana World homepage: https://www.themanaworld.org/
* Kivy: https://kivy.org/
* Construct: http://construct.readthedocs.org/
