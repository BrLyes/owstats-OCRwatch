import configparser
from PIL import Image
from mss import mss

config = configparser.ConfigParser()
config.read("config.ini")

monitor = config.getint("input", "monitor")


def take_screenshot():
    with mss() as sct:
        sct.shot(mon=monitor)
        
    #resize the screenshot
    image = Image.open(f"monitor-{monitor}.png")
    image.thumbnail((1920,1080), Image.ANTIALIAS)
    image.save(f"monitor-{monitor}.png","png")

    print("*snap*")
    return f"monitor-{monitor}.png"
