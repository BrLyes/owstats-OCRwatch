import configparser
import time

from PIL import Image
from mss import mss

config = configparser.ConfigParser()
config.read("config.ini")

monitor = config.getint("input", "monitor")


def take_screenshot():
    with mss() as sct:
        sct.shot(mon=monitor)
    print("*snap*")

    ##resize the screenshot
    #Need to sleep otherwise the screenshot might be partial
    time.sleep(0.1)
    image = Image.open(f"monitor-{monitor}.png")
    image.thumbnail((1920,1080), Image.ANTIALIAS)
    image.save(f"monitor-{monitor}.png","png")

    return f"monitor-{monitor}.png"
