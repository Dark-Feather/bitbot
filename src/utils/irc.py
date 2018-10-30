import string, re, typing

ASCII_UPPER = string.ascii_uppercase
ASCII_LOWER = string.ascii_lowercase
STRICT_RFC1459_UPPER = ASCII_UPPER+r'\[]'
STRICT_RFC1459_LOWER = ASCII_LOWER+r'|{}'
RFC1459_UPPER = STRICT_RFC1459_UPPER+"^"
RFC1459_LOWER = STRICT_RFC1459_LOWER+"~"

def remove_colon(s: str) -> str:
    if s.startswith(":"):
        s = s[1:]
    return s

MULTI_REPLACE_ITERABLE = typing.Iterable[str]
# case mapping lowercase/uppcase logic
def _multi_replace(s: str,
        chars1: typing.Iterable[str],
        chars2: typing.Iterable[str]) -> str:
    for char1, char2 in zip(chars1, chars2):
        s = s.replace(char1, char2)
    return s
def lower(case_mapping: str, s: str) -> str:
    if case_mapping == "ascii":
        return _multi_replace(s, ASCII_UPPER, ASCII_LOWER)
    elif case_mapping == "rfc1459":
        return _multi_replace(s, RFC1459_UPPER, RFC1459_LOWER)
    elif case_mapping == "strict-rfc1459":
        return _multi_replace(s, STRICT_RFC1459_UPPER, STRICT_RFC1459_LOWER)
    else:
        raise ValueError("unknown casemapping '%s'" % case_mapping)

# compare a string while respecting case mapping
def equals(case_mapping: str, s1: str, s2: str) -> bool:
    return lower(case_mapping, s1) == lower(case_mapping, s2)

class IRCHostmask(object):
    def __init__(self, nickname: str, username: str, hostname: str,
            hostmask: str):
        self.nickname = nickname
        self.username = username
        self.hostname = hostname
        self.hostmask = hostmask
    def __repr__(self):
        return "IRCHostmask(%s)" % self.__str__()
    def __str__(self):
        return self.hostmask

def seperate_hostmask(hostmask: str) -> IRCHostmask:
    hostmask = remove_colon(hostmask)
    nickname, _, username = hostmask.partition("!")
    username, _, hostname = username.partition("@")
    return IRCHostmask(nickname, username, hostname, hostmask)

class IRCLine(object):
    def __init__(self, tags: dict, prefix: str, command: str,
            args: typing.List[str], arbitrary: typing.Optional[str],
            last: str):
        self.tags = tags
        self.prefix = prefix
        self.command = command
        self.args = args
        self.arbitrary = arbitrary
        self.last = last

def parse_line(line: str) -> IRCLine:
    tags = {}
    prefix = None
    command = None

    if line[0] == "@":
        tags_prefix, line = line[1:].split(" ", 1)
        for tag in filter(None, tags_prefix.split(";")):
            tag, _, value = tag.partition("=")
            tags[tag] = value

    line, _, arbitrary = line.partition(" :")
    arbitrary = arbitrary or None

    if line[0] == ":":
        prefix, line = line[1:].split(" ", 1)
        prefix = seperate_hostmask(prefix)
    command, _, line = line.partition(" ")

    args = line.split(" ")
    last = arbitrary or args[-1]

    return IRCLine(tags, prefix, command, args, arbitrary, last)

COLOR_WHITE, COLOR_BLACK, COLOR_BLUE, COLOR_GREEN = 0, 1, 2, 3
COLOR_RED, COLOR_BROWN, COLOR_PURPLE, COLOR_ORANGE = 4, 5, 6, 7
COLOR_YELLOW, COLOR_LIGHTGREEN, COLOR_CYAN, COLOR_LIGHTCYAN = (8, 9,
    10, 11)
COLOR_LIGHTBLUE, COLOR_PINK, COLOR_GREY, COLOR_LIGHTGREY = (12, 13,
    14, 15)
FONT_BOLD, FONT_ITALIC, FONT_UNDERLINE, FONT_INVERT = ("\x02", "\x1D",
    "\x1F", "\x16")
FONT_COLOR, FONT_RESET = "\x03", "\x0F"
REGEX_COLOR = re.compile("%s\d\d(?:,\d\d)?" % FONT_COLOR)

def color(s: str, foreground: str, background: str=None) -> str:
    foreground = str(foreground).zfill(2)
    if background:
        background = str(background).zfill(2)
    return "%s%s%s%s%s" % (FONT_COLOR, foreground,
        "" if not background else ",%s" % background, s, FONT_COLOR)

def bold(s: str) -> str:
    return "%s%s%s" % (FONT_BOLD, s, FONT_BOLD)

def underline(s: str) -> str:
    return "%s%s%s" % (FONT_UNDERLINE, s, FONT_UNDERLINE)

def strip_font(s: str) -> str:
    s = s.replace(FONT_BOLD, "")
    s = s.replace(FONT_ITALIC, "")
    s = REGEX_COLOR.sub("", s)
    s = s.replace(FONT_COLOR, "")
    return s

