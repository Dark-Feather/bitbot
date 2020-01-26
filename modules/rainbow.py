import random
from src import ModuleManager, utils

COLORS = [
    utils.consts.BLUE,
    utils.consts.LIGHTBLUE,
    utils.consts.CYAN,
    utils.consts.LIGHTCYAN,
    utils.consts.GREEN,
    utils.consts.LIGHTGREEN,
    utils.consts.YELLOW,
    utils.consts.ORANGE,
    utils.consts.BROWN,
    utils.consts.RED,
    utils.consts.PINK,
    utils.consts.PURPLE
]

@utils.export("channelset", utils.BoolSetting("rainbow",
    "Enable/disable allowing rainbowification of strings"))
class Module(ModuleManager.BaseModule):
    @utils.hook("received.command.rainbow")
    @utils.kwarg("help", "Rainbowify a given string or the last message")
    @utils.kwarg("usage", "[string]")
    def rainbow(self, event):
        if event["is_channel"] and not event["target"].get_setting(
                "rainbow", False):
            return

        args = event["args"]
        if not args:
            args = event["target"].buffer.get()
            if not args:
                raise utils.EventError("No line found to rainbowify")
        args = utils.irc.strip_font(args)

        offset = random.randint(0, len(COLORS))
        out = ""
        for i, c in enumerate(args):
            color = COLORS[(i+offset)%len(COLORS)]
            out += utils.irc.color(c, color, terminate=False)
        event["stdout"].write(out)