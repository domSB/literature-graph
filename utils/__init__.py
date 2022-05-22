class Colours:
    """
    This is a little helper class to add some colours to the logs.

    Escape with \x1b[ or \u001b[
    Text style 0-normal, 1-bold, 2-light, 3-italic, 4-underlined, 5-blink
    separate with ;
    Text colour 30-black, 31-red, 32-green, 33-yellow, 34-blue, 35-purple, 36-cyan, 37-white
    Then optional another Seperator ; and background colour (40-47)
    finish with m
    """
    green = "\x1b[0;32m"
    yellow = "\x1b[0;33m"
    red = "\x1b[0;31m"
    bold_red = "\x1b[1;31m"
    blue = "\x1b[0;34m"
    reset = "\x1b[0m"
