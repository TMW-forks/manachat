# -*- coding: utf-8 -*-
import random
import chatbot
from commands import general_chat, send_whisper


__all__ = [ 'PLUGIN', 'init' ]

PLUGIN = {
    'name': 'lazytree',
    'requires': ('chatbot',),
    'blocks': (),
}


# -----------------------------------------------------------------------------
greetings = {
    "Hi {0}!"  : 4,
    "Hey {0}"  : 3,
    "Yo {0}"   : 2,
    "{0}!!!!"  : 1,
    "{0}!!!"   : 1,
    "{0}!!"    : 1,
    "Hello {0}" : 5,
    "Hello {0}!" : 5,
    "Welcome back {0}" : 3,
    "Hello {0}! You are looking lovely today!" : 1,
    "{0} is back!!" : 1,
    "Hello and welcome to the Aperture Science \
computer-aided enrichment center." : 1,
}

drop_items = [
    "a bomb", "a bowl of petunias", "a cake", "a candy", "a chocobo",
    "a coin", "a cookie", "a drunken pirate", "a freight train",
    "a fruit", "a mouboo", "an angry cat",
    "an angry polish spelling of a rare element with the atomic number 78",
    "an anvil", "an apple", "an iten", "a magic eightball", "a GM",
    "a whale", "an elephant", "a piano", "a piece of moon rock", "a pin",
    "a rock", "a tub", "a wet mop", "some bass", "Voldemort", "a sandworm",
    "a princess", "a prince", "an idea", "Luvia", "a penguin",
    "The Hitchhiker's Guide to the Galaxy",
]

dropping_other = [
    "Hu hu hu.. {0} kicked me!",
    "Ouch..",
    "Ouchy..",
    "*drops dead*",
    "*sighs*",
    "Leaf me alone.",
    "Stop it! I doesn't drop branches, try the Druid tree for once!",
]

dropping_special = {
    "ShaiN2" : "*drops a nurse on {0}*",
    "Shainen" : "*drops a nurse on {0}*",
    "Silent Dawn" : "*drops a box of chocolate on {0}*",
    "veryape" : "*drops a chest of rares on {0}*",
    "veryapeGM" : "*drops a chest of rares on {0}*",
    "Ginaria" : "*drops a bluepar on {0}*",
    "Rift Avis" : "*drops an acorn on {0}*",
}

die_answers = [
    "*drops a bomb on {0}'s head*",
    "*drops a bowl of petunias on {0}'s head*",
    "*drops a drunken pirate on {0}'s head*",
    "*drops a freight train on {0}'s head*",
    "*drops a mouboo on {0}'s head*",
    "*drops an angry cat on {0}'s head*",
    "*drops an angry polish spelling of a rare element with \
the atomic number 78 on {0}'s head*",
    "*drops an iten on {0}'s head*",
    "*drops a piano on {0}'s head*",
    "*drops a piece of moon rock on {0}'s head*",
    "*drops Voldemort on {0}'s head*",
    "*drops dead*",
    "*sighs*",
    "Avada Kedavra!",
    "Make me!",
    "Never!!",
    "You die, {0}!",
    "You die, {0}!",
    "You die, {0}!",
    "You die, {0}!",
    "No!",
    "In a minute..",
    "Suuure... I'll get right on it",
]

healme_answers = [
    "Eat an apple, they're good for you.",
    "If I do it for you, then I have to do it for everybody.",
    "Oh, go drink a potion or something.",
    "Whoops! I lost my spellbook.",
    "no mana",
]

whoami_answers = [
    "An undercover GM.",
    "An exiled GM.",
    "I'm not telling you!",
    "I'm a bot! I'll be level 99 one day! Mwahahahaaha!!!111!",
    "Somebody said I'm a Chinese copy of Confused Tree",
    "I am your evil twin.",
    "I don't remember anything after I woke up! What happened to me?",
    "I don't know. Why am I here??",
    "Who are you?",
    "On the 8th day, God was bored and said 'There will be bots'. \
So here I am.",
    "♪ I'm your hell, I'm your dream, I'm nothing in between ♪♪",
    "♪♪ Aperture Science. We do what we must, because.. we can ♪",
    "I'm just a reincarnation of a copy.",
]

joke_answers = [
    "How did the tree get drunk? On root beer.",
    "Do you think I'm lazy?",
    "I miss Confused Tree :(",
    "I miss CrazyTree :(",
    "I'm not telling you!",
    "*sighs*",
    "If I do it for you, then I have to do it for everybody.",
    "What did the beaver say to the tree? It's been nice gnawing you.",
    "What did the little tree say to the big tree? Leaf me alone.",
    "What did the tree wear to the pool party? Swimming trunks.",
    "What do trees give to their dogs? Treets.",
    "What do you call a tree that only eats meat? Carniforous.",
    "What do you call a tree who's always envious? Evergreen.",
    "What is the tree's least favourite month? Sep-timber!",
    "What kind of tree can fit into your hand? A palm-tree.",
    "What was the tree's favorite subject in school? Chemistree.",
    "Why did the leaf go to the doctor? It was feeling green.",
    "Why doesn't the tree need sudo? Because it has root.",
    "Why was the cat afraid of the tree? Because of its bark.",
    "Why was the tree executed? For treeson.",
    "How do trees get on the internet? They log in.",
    "Why did the pine tree get into trouble? Because it was being knotty.",
    "Did you hear the one about the oak tree? It's a corn-y one!",
    "What do you call a blonde in a tree with a briefcase? Branch Manager.",
    "How is an apple like a lawyer? They both look good hanging from a tree.",
    "Why did the sheriff arrest the tree? Because its leaves rustled.",
    "I'm to tired, ask someone else.",
    "If you are trying to get me to tell jokes you are barking \
up the wrong tree!",
    "You wodden think they were funny anyhow. Leaf me alone!",
    "What is brown and sticky? A stick.",
]

burn_answers = [
    "*curses {0} and dies %%c*",
    "Help! I'm on fire!",
    "Oh hot.. hot hot!",
    "*is glowing*",
    "*is flaming*",
    "ehemm. where are firefighters? I need them now!",
    "*is so hot!*",
]

noidea_answers = [
    "what?", "what??", "whatever", "hmm...", "huh?", "*yawns*",
    "Wait a minute..", "What are you talking about?",
    "Who are you?", "What about me?",
    "I don't know what you are talking about",
    "Excuse me?", "very interesting", "really?",
    "go on...",  "*scratches its leafy head*",
    "*feels a disturbance in the force*",
    "*senses a disturbance in the force*",
    "*humming*", "I'm bored..", "%%j", "%%U", "%%[",
]

pain_answers = [ "Ouch..", "Ouchy..", "Argh..", "Eckk...", "*howls*",
                 "*screams*", "*groans*", "*cries*", "*faints*", "%%k",
                 "Why.. What did I do to you? %%i" ]

hurt_actions = [ "eat", "shoot", "pluck", "torture", "slap", "poison",
                 "break", "stab", "throw" ]

ignored_players = []
tree_admins = [ 'TestChar2' ]


# -----------------------------------------------------------------------------
def say_greeting(nick, _, is_whisper, match):
    if is_whisper:
        return

    if nick in ignored_players:
        return

    total_weight = 0
    for w in greetings.itervalues():
        total_weight += w

    random_weight = random.randint(0, total_weight)
    total_weight = 0
    random_greeting = 'Hi {0}'
    for g, w in greetings.iteritems():
        if total_weight >= random_weight:
            random_greeting = g
            break
        total_weight += w

    general_chat(random_greeting.format(nick))


def drop_on_head(nick, _, is_whisper, match):
    if is_whisper:
        return

    if nick in ignored_players:
        return

    answer = 'yeah'
    if nick in dropping_special:
        answer = dropping_special[nick]
    else:
        r = random.randint(0, len(drop_items) + len(dropping_other))
        if r < len(drop_items):
            answer = "*drops {} on {}'s head*".format(drop_items[r], nick)
        else:
            answer = random.choice(dropping_other)

    general_chat(answer.format(nick))


def answer_threat(nick, _, is_whisper, match):
    if is_whisper:
        return

    if nick in ignored_players:
        return

    answer = random.choice(die_answers)
    general_chat(answer.format(nick))


# -----------------------------------------------------------------------------
def admin_additem(nick, _, is_whisper, match):
    if not is_whisper:
        return

    if nick not in tree_admins:
        return

    item = match.group(1)
    if item not in drop_items:
        drop_items.append(item)

    send_whisper(nick, "Added item '{}' to drop list".format(item))


def admin_addjoke(nick, _, is_whisper, match):
    if not is_whisper:
        return

    if nick not in tree_admins:
        return

    joke = match.group(1)
    if joke not in joke_answers:
        joke_answers.append(joke)

    send_whisper(nick, "Added joke")


# -----------------------------------------------------------------------------
tree_commands = {
    r'^(hello|hi|hey|heya|hiya|yo) (tree|LazyTree)' : say_greeting,
    r'^(hello|hi|hey|heya|hiya) (all|everybody|everyone)$' : say_greeting,
    r'\*?((shake|kick)s?) (tree|LazyTree)' : drop_on_head,
    r'(die|\*?((nuke|kill)s?)) (tree|LazyTree)' : answer_threat,
    r'\*?(burn(s?)) (tree|LazyTree)' : burn_answers,
    r'^tell (.*)joke([ ,]{1,2})tree' : joke_answers,
    r'^heal me([ ,]{1,2})tree' : healme_answers,
    r'^(who|what) are you([ ,]{1,3})tree' : whoami_answers,
    r'\*?(' + '|'.join(hurt_actions) + ')s? (tree|LazyTree)' : pain_answers,
    r'^!additem (.*)' : admin_additem,
    r'^!addjoke (.*)' : admin_addjoke,
}


def init(config):
    chatbot.commands.update(tree_commands)
