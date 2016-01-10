import re

__all__ = ('preprocess', 'remove_formatting', 'replace_emotes',
           'simplify_links', 'expand_links')

formatting_re = re.compile(r'##[0-9bB]')
emotes_re = re.compile(r'%%[^%]')
mplus_link_re = re.compile(r'@@([^|]+)\|([^@]+)@@')
url_re = re.compile(r'(^|[^@|])((http|https|ftp)://([^\t ]+))')


def remove_formatting(text):
    return re.sub(formatting_re, '', text)


def replace_emotes(text):

    emotes = ( ":-D", ":-)", ";-)", ":-(", ":-o", ":-|", ":-/", "B-)",
        ":-D", ":-[", ":-P", "*blush*", ":'-(", "*:-]*",
        "*weird emote*", "*ninja*", ":-)", "*star*", "*?*", "*!*", "*idea*",
        "*->*", "<3", "^_^", ":-)", ";-)", ":-(", ":-O", ":-(",
        "*mimi*", ":-D", ":-D", "*perturbed*", ":-P",
        "*shame*", ":-(", ">:-D", "0_o", "*ninja*", "*bad geek*",
        "*star*", "*?*", "*!*", "*bubble*", ">_>", "*in love*",
        "*disgust*", ">:-D", ":-(", "xD", "u.u", "x_x",
        "*facepalm*", ">:-D", "*angry*", ":-D", "*metal*",
        ":'-(", "*...*", "*@:=*", ":3", "*zZzZz*", "-.-'",
        "*alien*")

    def emote_repl(m):
        code = ord(m.group(0)[2]) - 48
        if code > len(emotes):
            return m.group(0)
        else:
            return emotes[code]

    return re.sub(emotes_re, emote_repl, text)


def simplify_links(text):

    def simplify(m):
        return m.group(2)

    return re.sub(mplus_link_re, simplify, text)


def expand_links(text):

    def expand(m):
        return '{}[@@{}|{}@@]'.format(m.group(1), m.group(2), m.group(4))

    # text = ' ' + text
    return re.sub(url_re, expand, text)


def preprocess(text, actions=(simplify_links,
                              remove_formatting,
                              replace_emotes)):
    for f in actions:
        text = f(text)

    return text
